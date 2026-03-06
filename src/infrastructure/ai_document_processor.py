import os
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from pdf2image import convert_from_path
import json

from src.infrastructure.open_router_connector import OpenRouterConnector
from src.domain.models import ExtractedData, InvoiceData, LineItem, Brand, DocumentType

# ---------------------------------------------------------
# STAGE 1: Triage Router (Classification & Polarity)
# ---------------------------------------------------------
TRIAGE_SYSTEM_PROMPT = """You are a fast, lightweight Triage Router for accounting documents.
Your strictly limited job is to analyze the document, understand the context, determine the flow of money, and classify it.
Determine the document type strictly from the perspective of the receiver (the company processing this).
Identify the sender and receiver. Do NOT attempt to extract line items or financial totals."""

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": ["PURCHASE_INVOICE", "SALES_INVOICE", "BANK_STATEMENT", "UNKNOWN_DOCUMENT"]
        },
        "sender_name": {"type": "string"},
        "receiver_name": {"type": "string"},
        "confidence": {"type": "number"}
    },
    "required": ["document_type", "confidence"]
}

# ---------------------------------------------------------
# STAGE 2: Dynamic Schemas (The Specialists)
# ---------------------------------------------------------
INVOICE_SYSTEM_PROMPT = """You are a specialist extraction engine for INVOICES.
Your objective is to extract key bookkeeping data precisely as it appears, outputting exclusively in the requested JSON format.

Extraction Rules:
1. Strict Adherence: Do not guess, calculate, or infer missing values. If a value is not present, return null.
2. Formatting: Standardize all dates to YYYY-MM-DD. Return all monetary values and quantities as floats without currency symbols (e.g., convert "16.398,70" to 16398.70).
3. Line Item Integrity: Extract every individual billable line item.
4. Subtotal Exclusion: You MUST IGNORE any rows that represent subtotals, running totals, or page totals (e.g., "TOTAAL:"). Only extract the base service or product lines."""

PURCHASE_INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string"},
                "vendor_vat_id": {"type": "string"},
                "customer_name": {"type": "string"},
                "customer_vat_id": {"type": "string"}
            }
        },
        "invoice_data": {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string"},
                "invoice_date": {"type": "string"},
                "due_date": {"type": "string"},
                "currency": {"type": "string"},
                "payment_reference": {"type": "string"},
                "iban": {"type": "string"}
            }
        },
        "financials": {
            "type": "object",
            "properties": {
                "net_amount": {"type": "number"},
                "tax_amount": {"type": "number"},
                "gross_amount": {"type": "number"},
                "tax_exemption_note": {"type": "string"}
            }
        },
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "net_amount": {"type": "number"},
                    "tax_code": {"type": "string"}
                },
                "required": ["description", "net_amount"]
            }
        }
    },
    "required": ["entities", "invoice_data", "financials", "line_items"]
}

BANK_STATEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "account_number": {"type": "string"},
        "statement_date": {"type": "string"},
        "beginning_balance": {"type": "number"},
        "ending_balance": {"type": "number"},
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "description": {"type": "string"},
                    "amount": {"type": "number"},
                    "type": {"type": "string", "enum": ["CREDIT", "DEBIT"]}
                }
            }
        }
    },
    "required": ["account_number", "transactions"]
}

class AIDocumentProcessor:
    """
    Handles PDF to Image conversion and multi-stage Agentic Workflow extraction.
    Stage 1: Classification & Polarity (Triage Router)
    Stage 2: Dynamic Schema Injection (Specialist)
    """
    def __init__(self, connector: OpenRouterConnector):
        self.connector = connector
        self.model = "google/gemini-3-flash-preview"

    def process_pdf(self, file_path: str) -> List[str]:
        """
        Converts ALL PDF pages to base64 encoded JPEG images.
        """
        images = convert_from_path(file_path)
        encoded_images = []
        
        for img in images:
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            encoded_images.append(img_str)
            
        return encoded_images

    def _call_llm(self, system_prompt: str, user_prompt: str, images: List[str]) -> Dict[str, Any]:
        """Helper to invoke LLM and parse JSON output safely."""
        response = self.connector.vision_chat_multi(
            self.model,
            system_prompt,
            user_prompt,
            images
        )
        try:
            content = response['choices'][0]['message']['content']
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"AI LLM call failed to parse response: {str(e)}\nRaw: {content if 'content' in locals() else 'No content'}")

    def extract_from_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Multi-step Agentic Workflow.
        Step 1: Triage Classification.
        Step 2: Dynamic Schema Injection.
        """
        images = self.process_pdf(file_path)
        if not images:
            raise ValueError("Could not extract images from PDF")

        # ---------------------------------------------------------
        # STAGE 1: Triage Router
        # ---------------------------------------------------------
        triage_prompt = f"Analyze all pages. What type of document is this? Who sent it? Who is receiving it?\nSchema:\n{json.dumps(TRIAGE_SCHEMA, indent=2)}"
        triage_result = self._call_llm(TRIAGE_SYSTEM_PROMPT, triage_prompt, images)
        
        doc_type = triage_result.get("document_type", "UNKNOWN_DOCUMENT")
        
        # ---------------------------------------------------------
        # STAGE 2: Dynamic Schema Injection
        # ---------------------------------------------------------
        final_result = {
            "classification": {
                "document_type": doc_type,
                "confidence": triage_result.get("confidence", 0.0)
            }
        }
        
        if doc_type in ["PURCHASE_INVOICE", "SALES_INVOICE"]:
            spec_prompt = f"Extract the INVOICE data according to the following JSON schema.\nSchema:\n{json.dumps(PURCHASE_INVOICE_SCHEMA, indent=2)}"
            spec_result = self._call_llm(INVOICE_SYSTEM_PROMPT, spec_prompt, images)
            final_result.update(spec_result)
            
        elif doc_type == "BANK_STATEMENT":
            spec_prompt = f"Extract the BANK STATEMENT data according to the following JSON schema.\nSchema:\n{json.dumps(BANK_STATEMENT_SCHEMA, indent=2)}"
            spec_result = self._call_llm("You are a Bank Statement extraction specialist.", spec_prompt, images)
            final_result["bank_data"] = spec_result
            
        else:
            # UNKNOWN_DOCUMENT triggers a minimal extraction / requires human review
            final_result["error"] = "UNKNOWN_DOCUMENT: Requires human-in-the-loop review."

        return final_result

    def validate_extraction(self, raw_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Post-extraction validation: compares sum of line_items.net_amount
        against financials.net_amount.
        
        Returns:
            (is_valid, delta, message)
        """
        financials = raw_data.get("financials", {})
        header_net = financials.get("net_amount")
        line_items = raw_data.get("line_items", [])
        
        if not line_items:
            return False, 0.0, "No line items extracted"
        
        line_items_sum = sum(item.get("net_amount", 0) for item in line_items)
        
        if header_net is None:
            return True, 0.0, f"No header net amount to validate against. Line items sum: €{line_items_sum:,.2f}"
        
        delta = abs(header_net - line_items_sum)
        tolerance = 0.02  # Allow 2 cent rounding tolerance
        is_valid = delta <= tolerance
        
        if is_valid:
            message = f"✅ Validation PASSED: Line items (€{line_items_sum:,.2f}) match header (€{header_net:,.2f})"
        else:
            message = f"⚠️ Validation FAILED: Line items (€{line_items_sum:,.2f}) vs header (€{header_net:,.2f}), delta: €{delta:,.2f}"
        
        return is_valid, delta, message

    def map_to_domain(self, raw_data: Dict[str, Any]) -> ExtractedData:
        """
        Maps raw AI JSON output (zero-shot schema) to the system's domain models.
        """
        classification = raw_data.get("classification", {})
        entities = raw_data.get("entities", {})
        invoice_data = raw_data.get("invoice_data", {})
        financials = raw_data.get("financials", {})
        raw_line_items = raw_data.get("line_items", [])
        
        # Map document type
        doc_type_str = classification.get("document_type", "UNKNOWN")
        try:
            doc_type = DocumentType(doc_type_str)
        except ValueError:
            doc_type = DocumentType.UNKNOWN
        
        # Map line items to LineItem models
        line_items = []
        for item in raw_line_items:
            try:
                line_items.append(LineItem(
                    date=item.get("date"),
                    description=item.get("description", "Unknown"),
                    quantity=item.get("quantity"),
                    unit_price=item.get("unit_price"),
                    net_amount=item.get("net_amount", 0.0),
                    tax_code=item.get("tax_code")
                ))
            except Exception:
                continue  # Skip malformed line items
        
        invoice = InvoiceData(
            invoice_number=invoice_data.get("invoice_number"),
            date=invoice_data.get("invoice_date"),
            due_date=invoice_data.get("due_date"),
            total_amount=financials.get("gross_amount"),
            currency=invoice_data.get("currency", "EUR"),
            vendor_name=entities.get("vendor_name"),
            vendor_vat=entities.get("vendor_vat_id"),
            customer_name=entities.get("customer_name"),
            customer_vat=entities.get("customer_vat_id"),
            payment_reference=invoice_data.get("payment_reference"),
            iban=invoice_data.get("iban"),
            net_amount=financials.get("net_amount"),
            tax_amount=financials.get("tax_amount"),
            gross_amount=financials.get("gross_amount"),
            document_type=doc_type,
            language=classification.get("language"),
            line_items=line_items,
            confidence_score=0.95
        )
        
        # Brand detection from entity names
        brand_keywords = {
            "sacha": Brand.SACHA,
            "manfield": Brand.MANFIELD,
            "sissy boy": Brand.SISSYBOY,
            "sissyboy": Brand.SISSYBOY,
        }
        detected_brand = Brand.UNKNOWN
        customer_name = (entities.get("customer_name") or "").lower()
        for keyword, brand in brand_keywords.items():
            if keyword in customer_name:
                detected_brand = brand
                break
        
        return ExtractedData(
            source_type="invoice_pdf",
            invoice=invoice,
            structured_data={
                "detected_brand": detected_brand,
                "raw_extraction": raw_data
            }
        )

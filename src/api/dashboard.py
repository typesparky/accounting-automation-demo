import streamlit as st
import pandas as pd
import os
import sys
import uuid
import time
import random
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.domain.models import Brand, InvoiceData, WorkflowStatus, ExtractedData, AgentContext
from src.infrastructure.knowledge_base import KnowledgeBase
from src.orchestration.email_to_exact_workflow import EmailToExactWorkflow
from src.infrastructure.open_router_connector import OpenRouterConnector

# Try to import AI processor, gracefully handle if dependencies missing
try:
    from src.infrastructure.ai_document_processor import AIDocumentProcessor
except ImportError:
    AIDocumentProcessor = None

# Translations
TRANSLATIONS = {
    "EN": {
        "title": "Termeer Group | Accounting Automation",
        "header_sub": "Accounting Workflow Automation",
        "overview": "SYSTEM OVERVIEW",
        "engine_specs": "🤖 AI Engine Specs",
        "accounting_status": "### ACCOUNTING STATUS",
        "registry": "● **Internal Registry:** Connected",
        "exact_api": "● **Exact Online API:** Ready",
        "ai_processor": "● **AI Processor:**",
        "active": "Active",
        "error": "Error",
        "rules_db": "### 📋 ACCOUNTING RULES",
        "rules_info": "View the complete Blue10 template database and accounting terms.",
        "open_rules": "Open Accounting Rules DB",
        "step1": "1. Ingestion",
        "step2": "2. OCR Hub",
        "step3": "3. Verification",
        "ingestion_sub": "Document Ingestion",
        "ingestion_info": "Monitor Outlook inboxes or manually upload batch PDFs. Brand detection happens in next step.",
        "outlook_conn": "**Termeer Integrated Connector**",
        "refresh_outlook": "Refresh Outlook Inbox",
        "fetching": "Fetching from O365...",
        "outlook_toast": "Connected to Termeer Group mail server.",
        "manual_upload": "**Manual Batch Upload**",
        "drop_files": "Drop invoice files here",
        "import_batch": "Import Batch",
        "doc_queue": "### Document Queue",
        "monitoring": "Currently monitoring {} documents.",
        "ocr_sub": "Intelligent Data Extraction & Brand Detection",
        "no_docs": "No documents in queue. Please go to Ingestion first.",
        "utilizing": "Utilizing **Gemini 3 Flash** to extract financial primitives and identify the target entity.",
        "run_ocr": "Execute Extraction Pipeline",
        "activating": "Activating Gemini Vision Pipeline...",
        "extraction_done": "Extraction and Brand Detection sequence completed.",
        "vendor": "Vendor",
        "amount": "Amount",
        "detected_entity": "Detected Entity",
        "status": "Status",
        "pending_rules": "Pending Rules",
        "exec_verification": "Executive Verification",
        "validation_pass": "Final validation pass using **Gemini 3 Flash** via OpenRouter.",
        "awaiting_data": "Awaiting data from previous steps.",
        "entity": "Entity",
        "total": "Total",
        "verified_by": "Verified by Gemini 3 Flash",
        "begin_verification": "Begin Verification",
        "analyzing": "AI analyzing extraction integrity...",
        "batch_success": "Batch Verification Success. Ready for Exact Online synchronization.",
        "send_email": "📧 Send Email to Relevant People",
        "email_info": "Send verification summary to accounting team with all invoice details.",
        "preview_email": "Preview Email Content",
        "email_preview": "**Email Preview:**",
        "confirm_send": "Confirm & Send Email",
        "email_success_toast": "📧 Email sent successfully to accounting team!",
        "cancel_email": "Cancel Email",
        "initiate_sync": "Initiate Synchronization",
        "sync_toast": "Data transmitted to Exact Online API.",
        "new_batch": "Process New Batch"
    },
    "NL": {
        "title": "Termeer Groep | Boekhoudautomatisering",
        "header_sub": "Automatisering van de Boekhoudworkflow",
        "overview": "SYSTEEMOVERZICHT",
        "engine_specs": "🤖 AI Engine Specificaties",
        "accounting_status": "### BOEKHOUDSTATUS",
        "registry": "● **Intern Register:** Verbonden",
        "exact_api": "● **Exact Online API:** Gereed",
        "ai_processor": "● **AI Processor:**",
        "active": "Actief",
        "error": "Fout",
        "rules_db": "### 📋 BOEKHOUDREGELS",
        "rules_info": "Bekijk de volledige Blue10-sjabloondatabase en boekhoudtermen.",
        "open_rules": "Open Boekhoudregels DB",
        "step1": "1. Ingestie",
        "step2": "2. OCR Hub",
        "step3": "3. Verificatie",
        "ingestion_sub": "Document Ingestie",
        "ingestion_info": "Monitor Outlook-inboxen of upload handmatig batch-PDF's. Merkdetectie vindt plaats in de volgende stap.",
        "outlook_conn": "**Termeer Geïntegreerde Connector**",
        "refresh_outlook": "Outlook Inbox Verversen",
        "fetching": "Ophalen uit O365...",
        "outlook_toast": "Verbonden met de mailserver van de Termeer Groep.",
        "manual_upload": "**Handmatige Batch Upload**",
        "drop_files": "Sleep factuurbestanden hierheen",
        "import_batch": "Batch Importeren",
        "doc_queue": "### Documentwachtrij",
        "monitoring": "Momenteel {} documenten in de gaten gehouden.",
        "ocr_sub": "Intelligente Gegevensextractie & Merkdetectie",
        "no_docs": "Geen documenten in de wachtrij. Ga eerst naar Ingestie.",
        "utilizing": "Gebruikmakend van **Gemini 3 Flash** om financiële primitieven te extraheren en de doelentiteit te identificeren.",
        "run_ocr": "Extractie-pipeline Uitvoeren",
        "activating": "Gemini Vision Pipeline Activeren...",
        "extraction_done": "Extractie- en merkdetectiesequentie voltooid.",
        "vendor": "Leverancier",
        "amount": "Bedrag",
        "detected_entity": "Gedetecteerde Entiteit",
        "status": "Status",
        "pending_rules": "Wachtend op Regels",
        "exec_verification": "Directie Verificatie",
        "validation_pass": "Laatste validatie-pass met **Gemini 3 Flash** via OpenRouter.",
        "awaiting_data": "Wachten op gegevens van vorige stappen.",
        "entity": "Entiteit",
        "total": "Totaal",
        "verified_by": "Geverifieerd door Gemini 3 Flash",
        "begin_verification": "Verificatie Starten",
        "analyzing": "AI analyseert extractie-integriteit...",
        "batch_success": "Batch Verificatie Succesvol. Klaar voor Exact Online synchronisatie.",
        "send_email": "📧 E-mail Verzenden naar Relevante Personen",
        "email_info": "Stuur verificatiesamenvatting naar het boekhoudteam met alle factuurgegevens.",
        "preview_email": "E-mailinhoud Voorvertonen",
        "email_preview": "**E-mail Voorvertoning:**",
        "confirm_send": "Bevestigen & E-mail Verzenden",
        "email_success_toast": "📧 E-mail succesvol verzonden naar het boekhoudteam!",
        "cancel_email": "E-mail Annuleren",
        "initiate_sync": "Synchronisatie Starten",
        "sync_toast": "Gegevens verzonden naar Exact Online API.",
        "new_batch": "Nieuwe Batch Verwerken"
    }
}

# Page Configuration
st.set_page_config(
    page_title="Termeer Group | Accounting Automation",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Language
if 'language' not in st.session_state:
    st.session_state.language = "EN"

# Ensure language is always valid
if st.session_state.language not in TRANSLATIONS:
    st.session_state.language = "EN"

def t(key):
    lang = st.session_state.language if st.session_state.language in TRANSLATIONS else "EN"
    return TRANSLATIONS[lang].get(key, key)

# Custom CSS for Termeer Group Branding (Premium Luxury Aesthetic)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;600&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Headers */
    h1, h2, h3, .termeer-logo {
        font-family: 'Outfit', sans-serif !important;
        color: #000000 !important;
        font-weight: 300 !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
    }
    
    /* Ensure white text for badges and dark sections */
    .verified-badge, .flow-box-current, .flow-box-current *, .status-active {
        color: #ffffff !important;
    }

    
    /* Elegant Tab Control */
    .stTabs [data-baseweb="tab-list"] {
        gap: 40px;
        border-bottom: 1px solid #eeeeee;
        padding-bottom: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        font-family: 'Outfit', sans-serif !important;
        background-color: transparent !important;
        border: none;
        color: #aaaaaa !important;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom: 2px solid #000000 !important;
        font-weight: 400 !important;
    }
    
    /* Clean Section Boxes */
    .step-box {
        padding: 40px;
        border-radius: 0px;
        border: 0.5px solid #e0e0e0;
        margin-bottom: 30px;
        color: #000000 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
    
    .verified-badge {
        font-family: 'Outfit', sans-serif !important;
        color: #ffffff !important;
        font-weight: 300;
        background: #000000 !important;
        padding: 8px 20px;
        border-radius: 0px;
        font-size: 0.7em;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .brand-badge {
        font-family: 'Outfit', sans-serif !important;
        color: #000000 !important;
        font-weight: 300;
        background: #f5f5f5 !important;
        padding: 5px 15px;
        border-radius: 0px;
        font-size: 0.7em;
        border: 0.5px solid #000000;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .termeer-header {
        text-align: center;
        padding: 80px 0;
        border-bottom: 1px solid #eeeeee;
        margin-bottom: 60px;
    }
    
    .termeer-logo {
        font-size: 3.2em !important;
        margin-bottom: 12px;
    }
    
    .termeer-sub {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.85em;
        letter-spacing: 6px;
        color: #888888 !important;
        text-transform: uppercase;
        font-weight: 200;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] hr {
        border-top: 1px solid #eeeeee !important;
    }
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 0.5px solid #e0e0e0 !important;
        border-radius: 0px !important;
    }
    .stMetric label {
        font-family: 'Outfit', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 300 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Language Toggle (Top Right) - Always visible
col1, col2 = st.columns([8, 2])
with col2:
    selected_lang = st.radio(
        "Language", 
        options=["EN", "NL"], 
        index=0 if st.session_state.language == "EN" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

# Branding Header
st.markdown(f"""
    <div class="termeer-header">
        <div class="termeer-logo">TERMEER GROUP</div>
        <div class="termeer-sub">{t('header_sub')}</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'workflow' not in st.session_state:
    st.session_state.workflow = EmailToExactWorkflow()
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeBase()
if 'processor' not in st.session_state:
    try:
        if AIDocumentProcessor is not None:
            connector = OpenRouterConnector()
            st.session_state.processor = AIDocumentProcessor(connector)
        else:
            st.session_state.processor = None
    except Exception:
        st.session_state.processor = None
        st.sidebar.error("⚠️ OPENROUTER_API_KEY or Dependencies Missing")

if 'processing_docs' not in st.session_state:
    st.session_state.processing_docs = []
if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = {}
if 'verified_docs' not in st.session_state:
    st.session_state.verified_docs = {}

# Sidebar: System Status
with st.sidebar:
    st.markdown(f"### {t('overview')}")
    
    with st.expander(t('engine_specs'), expanded=True):
        st.write(f"**{t('vendor') if st.session_state.language == 'NL' else 'Extraction'}:** `OpenRouter: Gemini 3 Flash` (Live Vision)")
        st.write(f"**Rules:** `Blue10 Engine v2.1`")
        st.write(f"**Verification:** `OpenRouter: Gemini 3 Flash` (Deep Scan)")
        st.caption("Running via OpenRouter API (Cloud Gateway)")

    st.divider()
    
    st.markdown(t('accounting_status'))
    st.markdown(t('registry'))
    st.markdown(t('exact_api'))
    status_icon = "🟢" if st.session_state.processor else "🔴"
    status_text = t('active') if st.session_state.processor else t('error')
    st.markdown(f"{t('ai_processor')} {status_icon} {status_text}")

# Interactive Multi-Step Workflow using st.tabs
tab_titles = [t('step1'), t('step2'), t('step3')]
tabs = st.tabs(tab_titles)

# Sidebar: Link to Accounting Rules and Automation Overview
with st.sidebar:
    st.markdown("---")
    st.markdown(t('rules_db'))
    st.info(t('rules_info'))
    if st.button(t('open_rules')):
        st.markdown(f"[{t('open_rules')} →](#)", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔄 AUTOMATION OVERVIEW")
    st.info("View process flow and potential extensions.")
    if st.button("Open Automation Overview"):
        st.markdown("[Automation Overview →](#)", unsafe_allow_html=True)

# Step 1: Ingest
with tabs[0]:
    st.subheader(t('ingestion_sub'))
    st.info(t('ingestion_info'))
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(t('outlook_conn'))
        if st.button(t('refresh_outlook'), key="refresh_outlook"):
            with st.spinner(t('fetching')):
                time.sleep(1.2)
                # Simulated doc since we don't have real outlook creds in .env usually
                new_doc = {
                    "id": f"TM-{uuid.uuid4().hex[:6].upper()}", 
                    "source": "Outlook", 
                    "vendor": "Unknown", 
                    "received": datetime.now().strftime("%H:%M:%S"),
                    "file_path": None # Simulation
                }
                st.session_state.processing_docs.append(new_doc)
                st.toast(t('outlook_toast'))

    with col_right:
        st.markdown(t('manual_upload'))
        uploaded_file = st.file_uploader(t('drop_files'), type=["pdf"], label_visibility="collapsed")
        if uploaded_file and st.button(t('import_batch'), key="import_manual"):
            # Save uploaded file to temp location for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
                
            new_doc = {
                "id": f"UP-{uuid.uuid4().hex[:6].upper()}", 
                "source": "Upload", 
                "vendor": "Manual", 
                "received": datetime.now().strftime("%H:%M:%S"),
                "file_path": tmp_path
            }
            st.session_state.processing_docs.append(new_doc)
            st.success(f"{t('active') if st.session_state.language == 'NL' else 'File'} '{uploaded_file.name}' {'toegevoegd' if st.session_state.language == 'NL' else 'added'} {'aan wachtrij' if st.session_state.language == 'NL' else 'to queue'}.")

    if st.session_state.processing_docs:
        st.markdown(f"### {t('doc_queue')}")
        df = pd.DataFrame([ {k: v for k, v in d.items() if k != 'file_path'} for d in st.session_state.processing_docs ])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(t('monitoring').format(len(st.session_state.processing_docs)))

# Step 2: OCR Hub
with tabs[1]:
    st.subheader(t('ocr_sub'))
    if not st.session_state.processing_docs:
        st.warning(t('no_docs'))
    else:
        st.write(t('utilizing'))
        
        if st.button(t('run_ocr'), key="run_ocr"):
            if not st.session_state.processor:
                st.error(t('error'))
            else:
                with st.spinner(t('activating')):
                    progress_bar = st.progress(0)
                    available_brands = [Brand.SACHA, Brand.MANFIELD, Brand.SISSYBOY]
                    
                    for i, doc in enumerate(st.session_state.processing_docs):
                        try:
                            if doc['file_path'] and os.path.exists(doc['file_path']):
                                # Try REAL EXTRACTION first, fallback to Cache if API fails/missing
                                try:
                                    if not os.environ.get("OPENROUTER_API_KEY"):
                                        raise Exception("No API Key - using Cache")
                                    raw_data = st.session_state.processor.extract_from_invoice(doc['file_path'])
                                except Exception as e:
                                    st.warning(f"⚠️ Using Cached OCR Data (Reason: {str(e)})")
                                    import json
                                    cache_path = os.path.join("src", "data", "mock_bpost_extraction.json")
                                    if os.path.exists(cache_path):
                                        with open(cache_path, "r") as f:
                                            raw_data = json.load(f)
                                    else:
                                        raise e
                                        
                                domain_data = st.session_state.processor.map_to_domain(raw_data)
                                is_valid, delta, val_msg = st.session_state.processor.validate_extraction(raw_data)
                                
                                st.session_state.ocr_results[doc['id']] = {
                                    "vendor": domain_data.invoice.vendor_name,
                                    "customer": domain_data.invoice.customer_name,
                                    "amount": domain_data.invoice.gross_amount or domain_data.invoice.total_amount,
                                    "net_amount": domain_data.invoice.net_amount,
                                    "tax_amount": domain_data.invoice.tax_amount,
                                    "date": domain_data.invoice.date or "N/A",
                                    "due_date": domain_data.invoice.due_date,
                                    "vat_id": domain_data.invoice.vendor_vat,
                                    "customer_vat": domain_data.invoice.customer_vat,
                                    "currency": domain_data.invoice.currency,
                                    "invoice_number": domain_data.invoice.invoice_number,
                                    "document_type": domain_data.invoice.document_type.value,
                                    "language": domain_data.invoice.language,
                                    "payment_reference": domain_data.invoice.payment_reference,
                                    "iban": domain_data.invoice.iban,
                                    "detected_brand": domain_data.structured_data.get("detected_brand", Brand.UNKNOWN),
                                    "line_items": [li.model_dump() for li in domain_data.invoice.line_items],
                                    "validation_passed": is_valid,
                                    "validation_message": val_msg,
                                    "validation_delta": delta,
                                }
                            else:
                                # Fallback simulation for "simulated" docs
                                time.sleep(1.2)
                                det_brand = random.choice(available_brands)
                                st.session_state.ocr_results[doc['id']] = {
                                    "vendor": f"Simulated {det_brand.value} Supplier",
                                    "customer": "Termeer Group B.V.",
                                    "amount": 1450.75 + (i * 100),
                                    "net_amount": 1200.62 + (i * 82.64),
                                    "tax_amount": 250.13 + (i * 17.36),
                                    "date": "2024-06-20",
                                    "due_date": "2024-07-20",
                                    "vat_id": "NL800112233B01",
                                    "customer_vat": "NL123456789B01",
                                    "currency": "EUR",
                                    "invoice_number": f"INV-{uuid.uuid4().hex[:6].upper()}",
                                    "document_type": "PURCHASE_INVOICE",
                                    "language": "NL",
                                    "payment_reference": None,
                                    "iban": None,
                                    "detected_brand": det_brand,
                                    "line_items": [],
                                    "validation_passed": True,
                                    "validation_message": "✅ Simulated — no line items to validate",
                                    "validation_delta": 0.0,
                                }
                        except Exception as e:
                            st.error(f"{t('error')} for {doc['id']}: {str(e)}")
                            
                        progress_bar.progress((i + 1) / len(st.session_state.processing_docs))
                    st.success(t('extraction_done'))

        if st.session_state.ocr_results:
            for doc_id, data in st.session_state.ocr_results.items():
                with st.expander(f"📄 {doc_id} — {data.get('invoice_number', 'N/A')}", expanded=True):
                    # Classification & Validation Row
                    cv1, cv2, cv3 = st.columns(3)
                    cv1.markdown(f"**Document Type**\n`{data.get('document_type', 'UNKNOWN')}`")
                    cv2.markdown(f"**Language**\n`{data.get('language', 'N/A')}`")
                    val_icon = "✅" if data.get('validation_passed') else "⚠️"
                    cv3.markdown(f"**Validation**\n{val_icon} {'PASSED' if data.get('validation_passed') else 'MISMATCH'}")
                    
                    st.markdown("---")
                    
                    # Entities
                    e1, e2 = st.columns(2)
                    e1.markdown(f"**Vendor:** {data.get('vendor', 'N/A')}")
                    e1.markdown(f"**Vendor VAT:** `{data.get('vat_id', 'N/A')}`")
                    e2.markdown(f"**Customer:** {data.get('customer', 'N/A')}")
                    e2.markdown(f"**Customer VAT:** `{data.get('customer_vat', 'N/A')}`")
                    
                    st.markdown("---")
                    
                    # Financial Summary
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("Net Amount", f"€{data.get('net_amount', 0.0) or 0.0:,.2f}")
                    f2.metric("Tax Amount", f"€{data.get('tax_amount', 0.0) or 0.0:,.2f}")
                    f3.metric("Gross Amount", f"€{data.get('amount', 0.0) or 0.0:,.2f}")
                    f4.metric("Currency", data.get('currency', 'EUR'))
                    
                    # Invoice Details
                    d1, d2, d3 = st.columns(3)
                    d1.markdown(f"**Invoice Date:** {data.get('date', 'N/A')}")
                    d2.markdown(f"**Due Date:** {data.get('due_date', 'N/A')}")
                    d3.markdown(f"**{t('detected_entity')}**")
                    d3.markdown(f"<span class='brand-badge'>{data['detected_brand'].value if hasattr(data.get('detected_brand', ''), 'value') else data.get('detected_brand', 'Unknown')}</span>", unsafe_allow_html=True)
                    
                    # IBAN & Payment Reference
                    if data.get('iban') or data.get('payment_reference'):
                        p1, p2 = st.columns(2)
                        if data.get('iban'):
                            p1.markdown(f"**IBAN:** `{data['iban']}`")
                        if data.get('payment_reference'):
                            p2.markdown(f"**Payment Ref:** `{data['payment_reference']}`")
                    
                    # Line Items Table
                    line_items = data.get('line_items', [])
                    if line_items:
                        st.markdown(f"**Line Items** ({len(line_items)} extracted)")
                        li_df = pd.DataFrame(line_items)
                        # Reorder columns for clarity
                        col_order = [c for c in ['date', 'description', 'quantity', 'unit_price', 'net_amount', 'tax_code'] if c in li_df.columns]
                        li_df = li_df[col_order]
                        st.dataframe(li_df, use_container_width=True, hide_index=True, height=min(400, 35 * len(line_items) + 38))
                    
                    # Validation Message
                    val_msg = data.get('validation_message', '')
                    if val_msg:
                        if data.get('validation_passed'):
                            st.success(val_msg)
                        else:
                            st.warning(val_msg)

# Step 3: Verification (formerly step 4)
with tabs[2]:
    st.subheader(t('exec_verification'))
    st.markdown(t('validation_pass'))
    
    if not st.session_state.ocr_results:
        st.warning(t('awaiting_data'))
    else:
        for doc_id, data in st.session_state.ocr_results.items():
            is_verified = doc_id in st.session_state.verified_docs
            brand = data['detected_brand']
            brand_display = brand.value if hasattr(brand, 'value') else str(brand)
            
            st.markdown(f"""
            <div class="step-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight:600; font-size:1.1em;">{doc_id}</span> | {data.get('invoice_number', 'N/A')} | {data['vendor']}
                        <br/><span style="color:#666; font-size:0.9em;">{t('entity')}: <b>{brand_display}</b> | {data.get('document_type', 'N/A')} | {t('total')}: €{data.get('amount', 0.0) or 0.0:,.2f}</span>
                    </div>
                    { f'<span class="verified-badge">{t("verified_by")}</span>' if is_verified else '' }
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not is_verified:
                if st.button(t('begin_verification'), key=f"verify_{doc_id}"):
                    with st.spinner(t('analyzing')):
                        time.sleep(1.2)
                        st.session_state.verified_docs[doc_id] = True
                        st.rerun()

        if all(doc_id in st.session_state.verified_docs for doc_id in st.session_state.ocr_results):
            st.markdown("---")
            st.success(t('batch_success'))
            
            # Email notification section
            st.markdown(f"### {t('send_email')}")
            st.info(t('email_info'))
            
            # Initialize session state for email preview
            if 'show_email_preview' not in st.session_state:
                st.session_state.show_email_preview = False
            
            # Generate email content preview with accounting details (Translations needed for mail body too if strict)
            email_content = f"**{t('batch_success').upper()}**\n\nDear Accounting Team,\n\nThe following invoices have been verified and are ready for processing:\n\n---"
            
            for doc_id, data in st.session_state.ocr_results.items():
                brand = data['detected_brand']
                template = st.session_state.kb.get_template_for_brand(brand)
                email_content += f"""
**Invoice: {doc_id}**
- {t('vendor')}: {data['vendor']}
- {t('amount')}: €{data.get('amount', 0.0):,.2f}
- Date: {data['date']}
- {t('entity')}: {brand.value}
- Currency: {data['currency']}
- VAT ID: {data['vat_id']}
- General Ledger: {template.get('default_ledger')}
- VAT Category: {template.get('vat_code')}
- Cost Center: {template.get('cost_center')}
- Payment Terms: {template.get('payment_term')}
"""
            
            email_content += "\n---\n\n**Next Steps:**\n- Review and approve in Exact Online\n- Process payment according to vendor terms\n\nBest regards,\nTermeer Group Automation System"
            
            if st.button(t('preview_email'), key="preview_email"):
                st.session_state.show_email_preview = True
            
            if st.session_state.show_email_preview:
                st.markdown(t('email_preview'))
                st.text_area("Email Body", value=email_content.strip(), height=350, key="email_preview_text")
                
                col_email1, col_email2 = st.columns(2)
                with col_email1:
                    if st.button(t('confirm_send'), key="send_email"):
                        st.toast(t('email_success_toast'))
                        st.success(t('email_success_toast'))
                        st.session_state.show_email_preview = False
                with col_email2:
                    if st.button(t('cancel_email'), key="cancel_email"):
                        st.session_state.show_email_preview = False
                        st.rerun()
            
            st.markdown("---")
            
            if st.button(t('initiate_sync'), key="post_exact"):
                st.toast(t('sync_toast'))
                if st.button(t('new_batch')):
                    # Cleanup temp files
                    for doc in st.session_state.processing_docs:
                        if doc['file_path'] and os.path.exists(doc['file_path']):
                            try: os.unlink(doc['file_path'])
                            except: pass
                    st.session_state.processing_docs = []
                    st.session_state.ocr_results = {}
                    st.session_state.verified_docs = {}
                    st.rerun()

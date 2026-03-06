import json
from typing import Any, Dict, List, Optional
from src.domain.models import Brand

class KnowledgeBase:
    """
    Central repository for accounting rules, Blue10 templates, 
    and ledger bookkeeping logic.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        # Mock initial knowledge base data
        self.templates = {
            Brand.SACHA: {
                "default_ledger": "6000",
                "vat_code": "V21",
                "cost_center": "CC-SAC",
                "description_prefix": "[Sacha] Inventory",
                "payment_term": "30 Days",
                "auto_approve": True
            },
            Brand.MANFIELD: {
                "default_ledger": "6010",
                "vat_code": "V21",
                "cost_center": "CC-MAN",
                "description_prefix": "[Manfield] Inventory Purchase",
                "payment_term": "30 Days",
                "auto_approve": True
            },
            Brand.SISSYBOY: {
                "default_ledger": "6020",
                "vat_code": "V21",
                "cost_center": "CC-SIS",
                "description_prefix": "[Sissy Boy] Retail Supply",
                "payment_term": "14 Days",
                "auto_approve": False
            }
        }

    def get_template_for_brand(self, brand: Brand) -> Dict[str, Any]:
        """
        Retrieves the Blue10/Ledger template for a specific brand.
        """
        return self.templates.get(brand, self.templates.get(Brand.UNKNOWN, {}))

    def get_rules_for_vendor(self, vendor_name: str) -> Dict[str, Any]:
        """
        Retrieves vendor-specific bookkeeping rules.
        """
        # Logic to be expanded
        return {}

import streamlit as st
import os
import sys
import pandas as pd

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.domain.models import Brand
from src.infrastructure.knowledge_base import KnowledgeBase

# Page Configuration
st.set_page_config(
    page_title="Accounting Rules & Terms | Termeer Group",
    page_icon="📋",
    layout="wide"
)

# Simple CSS
st.markdown("""
    <style>
    h1, h2, h3 {
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("TERMEER GROUP")
st.caption("Accounting Rules & Terms Database")

st.markdown("---")

# Initialize Knowledge Base
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeBase()

# Main Content
st.header("📋 Accounting Rules & Terms Database")

st.markdown("""
This database contains all bookkeeping rules, Blue10 templates, and accounting terms 
used by the Termeer Group automation system. Each brand has specific configurations 
for General Ledger, VAT handling, Cost Centers, and Payment Terms.
""")

st.markdown("---")

# Get all templates
kb = st.session_state.kb
brands = [Brand.SACHA, Brand.MANFIELD, Brand.SISSYBOY]

# Create tabs for different views
view_tabs = st.tabs(["🏷️ Brand Templates", "📊 Ledger Overview", "📝 Detailed Rules"])

# Tab 1: Brand Templates
with view_tabs[0]:
    st.subheader("Brand-Specific Blue10 Templates")
    
    selected_brand = st.selectbox("Select Brand", brands)
    
    if selected_brand:
        template = kb.get_template_for_brand(selected_brand)
        
        with st.container(border=True):
            st.subheader(f"{selected_brand.value} Template")
            st.success("Active")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Ledger Configuration:**")
                st.markdown(f"- General Ledger: `{template.get('default_ledger')}`")
                st.markdown(f"- Cost Center: `{template.get('cost_center')}`")
                st.markdown(f"- Description Prefix: {template.get('description_prefix')}")
            
            with col2:
                st.markdown("**Tax & Payment:**")
                st.markdown(f"- VAT Code: `{template.get('vat_code')}`")
                st.markdown(f"- Payment Terms: {template.get('payment_term')}")
                st.markdown(f"- Auto-Approve: {'Yes' if template.get('auto_approve') else 'No - Requires Review'}")

# Tab 2: Ledger Overview
with view_tabs[1]:
    st.subheader("General Ledger Overview")
    
    # Create a table of all ledgers
    ledger_data = []
    for brand in brands:
        template = kb.get_template_for_brand(brand)
        ledger_data.append({
            "Brand": brand.value,
            "General Ledger": template.get('default_ledger'),
            "VAT Code": template.get('vat_code'),
            "Cost Center": template.get('cost_center'),
            "Payment Terms": template.get('payment_term'),
            "Auto-Approve": "✓" if template.get('auto_approve') else "✗"
        })
    
    df = pd.DataFrame(ledger_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Brands", len(brands))
    with col2:
        st.metric("Auto-Approve Enabled", sum(1 for b in brands if kb.get_template_for_brand(b).get('auto_approve')))
    with col3:
        st.metric("Unique Ledgers", len(set(t.get('default_ledger') for t in [kb.get_template_for_brand(b) for b in brands])))

# Tab 3: Detailed Rules
with view_tabs[2]:
    st.subheader("Detailed Accounting Rules")
    
    for brand in brands:
        template = kb.get_template_for_brand(brand)
        
        with st.expander(f"{brand.value} - Full Configuration", expanded=False):
            st.subheader(brand.value)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Ledger Configuration")
                st.markdown(f"**Default Ledger:** `{template.get('default_ledger')}`")
                st.markdown(f"**Cost Center:** `{template.get('cost_center')}`")
                st.markdown(f"**Description Prefix:** {template.get('description_prefix')}")
            
            with col2:
                st.markdown("#### Tax & Payment")
                st.markdown(f"**VAT Code:** `{template.get('vat_code')}`")
                st.markdown(f"**Payment Terms:** {template.get('payment_term')}")
                st.markdown(f"**Auto-Approve:** {'Enabled' if template.get('auto_approve') else 'Disabled - Manual Review Required'}")
            
            st.markdown("---")
            
            # Show rule description
            st.markdown("#### Bookkeeping Rule")
            if brand == Brand.SACHA:
                st.info("Sacha Fashion BV - Standard retail inventory purchase. Invoices are automatically approved and posted to the retail inventory ledger.")
            elif brand == Brand.MANFIELD:
                st.info("Manfield Shoes BV - Standard footwear inventory purchase. Invoices are automatically approved with 30-day payment terms.")
            elif brand == Brand.SISSYBOY:
                st.warning("Sissy Boy Retail - High-value retail purchases. All invoices require manual review before approval due to higher transaction values.")

# Footer
st.markdown("---")
st.caption("💼 Termeer Group | Accounting Rules Database | Powered by Blue10 Engine v2.1")

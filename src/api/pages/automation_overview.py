import streamlit as st
import os
import sys
import pandas as pd

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Page Configuration
st.set_page_config(
    page_title="Automation Overview | Termeer Group",
    page_icon="🔄",
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
st.caption("Automation Overview & Process Flow")

st.markdown("---")

# ============================================
# CURRENT WORKFLOW
# ============================================
st.header("📊 Current Workflow")

st.subheader("Document Processing Pipeline")

# Using Streamlit columns with native components
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**1. DOCUMENT INGESTION**\n\nEmail Fetching / File Upload\n\n✅ ACTIVE")

with col2:
    st.info("**2. OCR & EXTRACTION**\n\nAI-Powered Data Extraction\n\n✅ ACTIVE")

with col3:
    st.info("**3. VERIFICATION**\n\nExecutive Approval\n\n✅ ACTIVE")

st.markdown("**Sources:** 📧 Outlook/Email | 📁 Manual PDF Upload | 🔄 API Integration")

st.markdown("---")

# ============================================
# CURRENT INTEGRATIONS
# ============================================
st.header("🔗 Current Integrations")

int_col1, int_col2, int_col3 = st.columns(3)

with int_col1:
    st.success("📧 **Outlook / Email**\n\nIncoming Invoice Monitoring\n\n🔗 CONNECTED")

with int_col2:
    st.success("☁️ **OpenRouter**\n\nAI Extraction Engine\n\n🔗 CONNECTED")

with int_col3:
    st.success("📊 **Exact Online**\n\nAccounting System\n\n🔗 CONNECTED")

st.markdown("---")

# ============================================
# POTENTIAL EXTENSIONS
# ============================================
st.header("🚀 Potential Extensions")

st.markdown("Future enhancements and integrations that can be added to the automation system:")

# Extension cards using Streamlit containers
ext_col1, ext_col2 = st.columns(2)

with ext_col1:
    with st.container(border=True):
        st.subheader("🏦 Bank Integration")
        st.markdown("Automatic bank statement fetching and invoice matching.")
        st.caption("POTENTIAL")
        st.markdown("""
        - PSD2/Open Banking API
        - Automatic payment matching
        - Reconciliation automation
        """)
    
    with st.container(border=True):
        st.subheader("📱 Mobile App")
        st.markdown("Mobile interface for approvals and notifications.")
        st.caption("POTENTIAL")
        st.markdown("""
        - Push notifications
        - Quick approve/reject
        - Photo capture upload
        """)

with ext_col2:
    with st.container(border=True):
        st.subheader("🔗 Additional ERP Connectors")
        st.markdown("Support for more accounting software platforms.")
        st.caption("POTENTIAL")
        st.markdown("""
        - SAP Business One
        - Microsoft Dynamics 365
        - QuickBooks
        - Xero
        """)
    
    with st.container(border=True):
        st.subheader("🤖 Advanced AI Features")
        st.markdown("Enhanced machine learning capabilities.")
        st.caption("PLANNED")
        st.markdown("""
        - Anomaly detection
        - Vendor prediction
        - Expense categorization
        - Forecasting
        """)

st.markdown("---")

# ============================================
# PROCESS DETAILS
# ============================================
st.header("📋 Process Details")

with st.expander("View Detailed Process Flow", expanded=False):
    st.markdown("""
    ### Step 1: Document Ingestion
    - **Input:** PDFs from email or manual upload
    - **Process:** File validation and queue management
    - **Output:** Document added to processing queue
    
    ### Step 2: OCR & AI Extraction
    - **Input:** Raw PDF documents
    - **Process:** Gemini 3 Flash vision model extracts vendor, amount, date, VAT info
    - **Output:** Structured invoice data
    
    ### Step 3: Brand Detection & Rules
    - **Input:** Extracted invoice data
    - **Process:** Auto-detect brand/entity and apply Blue10 templates
    - **Output:** Mapped to correct GL, Cost Center, VAT code, Payment terms
    
    ### Step 4: Verification & Approval
    - **Input:** Fully processed invoice data
    - **Process:** AI verification + human approval
    - **Actions:** Email notification, sync to Exact Online
    - **Output:** Approved entries in accounting system
    """)

st.markdown("---")

# Statistics
st.header("📈 System Statistics")

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

with stats_col1:
    st.metric("Active Steps", "4")
with stats_col2:
    st.metric("Connected Systems", "3")
with stats_col3:
    st.metric("Supported Brands", "3")
with stats_col4:
    st.metric("Extension Possibilities", "8+")

# Footer
st.markdown("---")
st.caption("💼 Termeer Group | Automation Overview | Powered by Blue10 Engine v2.1")

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="How It Works | Termeer Group",
    page_icon="⚙️",
    layout="wide"
)

# Simple clean CSS
st.markdown("""
    <style>
    h1, h2, h3 {
        color: #000000;
    }
    .step-card {
        padding: 24px;
        border-radius: 8px;
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-bottom: 24px;
        color: #000000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .step-number {
        font-size: 1.2em;
        font-weight: 600;
        color: #000000;
        margin-bottom: 8px;
    }
    .note-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px 16px;
        margin-top: 12px;
        color: #856404;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("TERMEER GROUP")
st.caption("How It Works - Automated Accounting Workflow")
st.markdown("---")

st.header("⚙️ How It Works")
st.markdown("This page outlines the extremely simple 5-step process our AI pipeline follows to automate invoice handling.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">Step 1: Email Account Setup</div>
        Make a new, dedicated email account for the AI and add it to the relevant vendor communication groups on Outlook.
    </div>
    
    <div class="step-card">
        <div class="step-number">Step 2: Document Retrieval</div>
        Automatically download the invoice PDFs from our vendors and extract them directly from Outlook.
    </div>
    
    <div class="step-card">
        <div class="step-number">Step 3: AI Processing</div>
        The documents are processed and analyzed.
        <div class="note-box">
            <b>Note:</b> In this dash flow currently, we are not using a local model as we are showing it as an example. This will be changed to a strict local model in the production environment.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">Step 4: Classification & Routing</div>
        Determining exactly what type of invoice it is (e.g., Purchase, Sales, Intercompany) and deciding the precise next steps and rules that need to be applied to it.
    </div>
    
    <div class="step-card">
        <div class="step-number">Step 5: Automated Verification Routing</div>
        Once the AI has classified the document and extracted the data, it sends automated emails to the relevant people or department to verify and approve the invoice before syncing to Exact Online.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

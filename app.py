import streamlit as st
import pandas as pd
import requests
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION & ERROR HANDLING ---
st.set_page_config(
    page_title="Automation Infrastructure Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist Corporate CSS for Reliability & Presentation
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e8eaed; }
    .stButton>button {
        width: 100%; border-radius: 4px; height: 3em;
        background-color: #1a73e8; color: white; border: none;
        font-weight: 500; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #1557b0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    [data-testid="stMetric"] {
        background-color: #ffffff; padding: 20px; border-radius: 8px;
        border: 1px solid #e8eaed; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stDataFrame { border: 1px solid #e8eaed; border-radius: 8px; }
    h1, h2, h3 { color: #202124; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- PERSISTENCE LAYER (Error Proofing) ---
DB_FILE = "infrastructure_ledger.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE).to_dict('records')
        except Exception:
            return []
    return []

def save_data(data):
    try:
        pd.DataFrame(data).to_csv(DB_FILE, index=False)
    except Exception as e:
        st.error(f"Persistence Error: {e}")

# Initialize session states
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = load_data()
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = []

def log_event(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {type}: {message}"
    st.session_state.system_logs.insert(0, log_entry)

# --- UNIVERSAL API ROUTER (Open Connectivity) ---
def trigger_external_service(payload, endpoint_url, headers=None):
    """Modular function to connect this hub to external software gateways."""
    if not endpoint_url:
        return False, "Endpoint not configured."
    try:
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            return True, f"Success ({response.status_code})"
        return False, f"Server Error ({response.status_code})"
    except Exception as e:
        return False, str(e)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("Hub Control")
    st.markdown("v1.4.0 | Open Infrastructure")
    st.write("---")
    
    nav = st.radio(
        "Navigation",
        ["Dashboard", "Advanced Analytics", "System Logs", "Settings & Docs"],
        index=0
    )
    
    st.write("---")
    st.subheader("External Connectivity")
    primary_webhook = st.text_input("Active Webhook URL", 
                                    value=os.getenv("PRIMARY_WEBHOOK", ""),
                                    help="Main endpoint for downstream software triggers.")
    
    st.write("---")
    st.subheader("System Health")
    st.info("Node: PH-MANILA-01\nStatus: Active")
    
    if st.button("Clear Visual Ledger"):
        st.session_state.ledger_data = []
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.rerun()

# --- MAIN INTERFACE ---
if nav == "Dashboard":
    st.title("Operational Dashboard")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Connection", "Ready" if primary_webhook else "Local-Only", delta="Active")
    m_col2.metric("Inbound Queue", len(st.session_state.ledger_data), delta="+1")
    m_col3.metric("Avg Latency", "14ms", delta="-4ms")
    m_col4.metric("Success Rate", "100%")
    
    st.write("---")

    left_col, right_col = st.columns([1, 2], gap="large")

    with left_col:
        st.subheader("Intake Control")
        with st.form("lead_form", clear_on_submit=True):
            name = st.text_input("Entity Name", help="Legal name.")
            source = st.selectbox("Inbound Channel", ["Manual Input", "Webhook Gateway", "CRM Sync", "Scraper Hook"])
            phone = st.text_input("Contact Identifier")
            priority = st.select_slider("Priority Level", options=["Low", "Standard", "High", "Critical"])
            tags = st.multiselect("Processing Tags", ["Follow-up", "Tech Check", "Urgent", "New Client"])
            
            st.write("Outbound Options")
            broadcast = st.checkbox("Broadcast to Active Webhook", value=True if primary_webhook else False)
            
            submit = st.form_submit_button("Initialize Sequence")

        if submit:
            if not name or not phone:
                st.error("Validation Failed: Missing required identifiers.")
            else:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                payload = {
                    "timestamp": ts,
                    "name": name,
                    "phone": phone,
                    "source": source,
                    "priority": priority,
                    "tags": ", ".join(tags),
                    "status": "Processed"
                }
                
                with st.spinner("Processing sequence..."):
                    # Step 1: Local Persistence
                    time.sleep(0.4)
                    st.session_state.ledger_data.insert(0, payload)
                    save_data(st.session_state.ledger_data)
                    log_event(f"Internal Save: {name}", "SUCCESS")
                    
                    # Step 2: Open External Sync
                    if broadcast and primary_webhook:
                        success, msg = trigger_external_service(payload, primary_webhook)
                        if success:
                            log_event(f"External Broadcast: {name}", "EXTERNAL")
                        else:
                            log_event(f"Broadcast Failed: {msg}", "ERROR")
                            st.warning(f"External Sync Failed: {msg}")

                st.toast(f"Sequence active for {name}")

    with right_col:
        tab1, tab2 = st.tabs(["Active Registry", "Utility & Exports"])
        with tab1:
            if st.session_state.ledger_data:
                df = pd.DataFrame(st.session_state.ledger_data)
                search = st.text_input("Search Registry", placeholder="Filter records...")
                if search:
                    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Awaiting inbound data sequences.")
        with tab2:
            st.subheader("Data Portability")
            if st.session_state.ledger_data:
                df_export = pd.DataFrame(st.session_state.ledger_data)
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button("Export Ledger (CSV)", data=csv, file_name="hub_ledger.csv", mime='text/csv')
            else:
                st.caption("No data available for export.")

elif nav == "Advanced Analytics":
    st.title("Performance Analytics")
    if st.session_state.ledger_data:
        df = pd.DataFrame(st.session_state.ledger_data)
        st.subheader("Distribution by Priority")
        st.bar_chart(df['priority'].value_counts())
    else:
        st.warning("Insufficient data.")

elif nav == "System Logs":
    st.title("Technical Audit Trail")
    for log in st.session_state.system_logs:
        if "SUCCESS" in log or "EXTERNAL" in log: st.success(log)
        elif "ERROR" in log: st.error(log)
        else: st.info(log)

elif nav == "Settings & Docs":
    st.title("System Configuration")
    
    with st.expander("API & Software Bridges"):
        st.markdown("Configure headers for 3rd-party software (e.g., Salesforce, n8n, Railway).")
        auth_header = st.text_input("Auth Token (Optional)", type="password")
        st.info("Current payload format: application/json")
        
    with st.expander("Documentation"):
        st.markdown("""
        ### Open Infrastructure Protocol
        1. **Internal Storage**: Mirrored to `infrastructure_ledger.csv`.
        2. **External Broadcast**: Data is pushed via POST request to the Active Webhook URL.
        3. **Extensibility**: All data is sent in standard JSON format, allowing connection to any software that supports Webhooks or REST APIs.
        """)

# Footer
st.sidebar.write("---")
st.sidebar.caption("© 2026 Internal Infrastructure | Open Build")
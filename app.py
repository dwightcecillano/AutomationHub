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

# --- CONFIGURATION & ENHANCED UI ---
st.set_page_config(
    page_title="Automation Infrastructure Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Gradient UI & Custom Elements
st.markdown("""
    <style>
    /* Gradient Background for the entire app */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* High-Contrast Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a202c !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Elevated Metric Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    /* Form & Container Styling */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #e2e8f0;
    }
    
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 12px;
    }

    /* Typography */
    h1, h2, h3 {
        color: #1a202c;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    .stButton>button {
        width: 100%; border-radius: 6px; height: 3.5em;
        background-color: #1a73e8; color: white; border: none;
        font-weight: 600; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1557b0;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- PERSISTENCE LAYER ---
DB_FILE = "infrastructure_ledger.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE).to_dict('records')
        except: return []
    return []

def save_data(data):
    try: pd.DataFrame(data).to_csv(DB_FILE, index=False)
    except Exception as e: st.error(f"Persistence Error: {e}")

if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = load_data()
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = []

def log_event(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.system_logs.insert(0, f"[{timestamp}] {type}: {message}")

# --- API ROUTER ---
def trigger_external_service(payload, endpoint_url):
    if not endpoint_url: return False, "No endpoint."
    try:
        response = requests.post(endpoint_url, json=payload, timeout=10)
        return (True, "Success") if response.status_code in [200, 201, 202] else (False, f"Error {response.status_code}")
    except Exception as e: return False, str(e)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("Hub Control")
    st.markdown("v1.4.5 | Production")
    st.write("---")
    
    nav = st.radio("Navigation", ["Dashboard", "Analytics", "System Logs", "Settings"])
    
    st.write("---")
    st.subheader("Global Connector")
    primary_webhook = st.text_input("Active Webhook URL", value=os.getenv("PRIMARY_WEBHOOK", ""))
    
    if st.button("Reset Session Cache"):
        st.session_state.ledger_data = []
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

# --- MAIN INTERFACE ---
if nav == "Dashboard":
    st.title("Operational Dashboard")
    
    # Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("API Gateway", "Online" if primary_webhook else "Local", delta="Active")
    m_col2.metric("Total Records", len(st.session_state.ledger_data), delta="+1")
    m_col3.metric("Latency", "12ms", delta="-2ms")
    m_col4.metric("Node", "PH-MNL")
    
    st.write("---")

    left_col, right_col = st.columns([1, 2], gap="large")

    with left_col:
        st.subheader("Intake Control")
        # Visual filler for intake
        st.image("https://img.icons8.com/clouds/200/database.png", width=100)
        
        with st.form("lead_form", clear_on_submit=True):
            name = st.text_input("Entity Name")
            source = st.selectbox("Channel", ["Manual", "Webhook", "API Sync", "Scraper"])
            phone = st.text_input("Contact Identifier")
            priority = st.select_slider("Priority", options=["Low", "Standard", "High", "Critical"])
            broadcast = st.checkbox("Broadcast to Webhook", value=True if primary_webhook else False)
            
            submit = st.form_submit_button("Initialize Sequence")

        if submit:
            if name and phone:
                payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name, "phone": phone, "source": source, 
                    "priority": priority, "status": "Processed"
                }
                
                with st.spinner("Processing..."):
                    st.session_state.ledger_data.insert(0, payload)
                    save_data(st.session_state.ledger_data)
                    
                    if broadcast and primary_webhook:
                        success, msg = trigger_external_service(payload, primary_webhook)
                        log_event(f"Broadcast: {name}", "EXTERNAL" if success else "ERROR")
                    
                st.toast(f"Sequence active: {name}")
            else:
                st.error("Fields required.")

    with right_col:
        st.subheader("Operational Ledger")
        if st.session_state.ledger_data:
            df = pd.DataFrame(st.session_state.ledger_data)
            search = st.text_input("Filter Registry", placeholder="Search entries...")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Export Ledger (CSV)", data=csv, file_name="ledger_export.csv")
        else:
            st.info("No active records found.")
            st.image("https://img.icons8.com/clouds/400/opened-folder.png", use_container_width=True)

elif nav == "Analytics":
    st.title("System Analytics")
    if st.session_state.ledger_data:
        df = pd.DataFrame(st.session_state.ledger_data)
        st.bar_chart(df['priority'].value_counts())
        st.write("Source Distribution", df['source'].value_counts())
    else:
        st.warning("Insufficient data.")

elif nav == "System Logs":
    st.title("Audit Trail")
    for log in st.session_state.system_logs:
        st.caption(log)

elif nav == "Settings":
    st.title("Configuration")
    st.expander("API Gateway Documentation").markdown("""
    - **Method**: POST
    - **Format**: JSON
    - **Persistence**: Enabled via local CSV fallback.
    """)

# Footer
st.sidebar.write("---")
st.sidebar.caption("© 2026 Internal Infrastructure | PH-Node")
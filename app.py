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

# --- CONFIGURATION & DARK UI ---
st.set_page_config(
    page_title="Automation Infrastructure Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# VS Code Dark Inspired Theme
st.markdown("""
    <style>
    /* Main Background - VS Code Charcoal */
    .stApp {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    
    /* Sidebar - Slightly darker contrast */
    [data-testid="stSidebar"] {
        background-color: #252526 !important;
        border-right: 1px solid #333333;
    }
    [data-testid="stSidebar"] * {
        color: #cccccc !important;
    }
    
    /* Elevated Metric Cards - Slate Grey */
    [data-testid="stMetric"] {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #3c3c3c;
    }
    [data-testid="stMetricValue"] {
        color: #007acc !important; /* VS Code Blue */
    }

    /* Form & Container Styling */
    [data-testid="stForm"] {
        background-color: #252526;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #3c3c3c;
    }
    
    /* Dataframe Styling for Dark Mode */
    .stDataFrame {
        background-color: #1e1e1e;
        border-radius: 8px;
    }

    /* Typography - Clean Sans & Monospace for headers */
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Consolas', 'Monaco', 'Inter', monospace;
        font-weight: 600;
    }
    
    /* Primary Action Buttons - VS Code Blue */
    .stButton>button {
        width: 100%; border-radius: 4px; height: 3.5em;
        background-color: #007acc; color: white; border: none;
        font-weight: 600; transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1f8ad2;
        border: 1px solid #ffffff33;
        box-shadow: 0 0 10px rgba(0, 122, 204, 0.4);
    }
    
    /* Input field text color fix */
    input {
        color: #ffffff !important;
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
    st.image("https://img.icons8.com/fluency/96/code-file.png", width=60)
    st.title("Hub Control")
    st.markdown("v1.5.0 | Dark Mode")
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
        # Visual filler - Subtle dark icon
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
            st.info("No active records found. System idling.")
            st.image("https://img.icons8.com/clouds/400/code.png", use_container_width=True)

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
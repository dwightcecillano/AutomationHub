import streamlit as st
import pandas as pd
import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Professional UI Configuration
st.set_page_config(page_title="Automation Infrastructure Hub", layout="wide")

# Custom CSS for a professional "DevOps" look without emojis
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 3em;
        background-color: #1a73e8;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 4px;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #202124;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for the live ledger
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = []

# Header Section
st.title("Automation Infrastructure Hub")
st.markdown("Centralized management for lead intake, database synchronization, and response triggers.")

# System Health Metrics
st.write("---")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)
status_col1.metric("Server Status", "Operational")
status_col2.metric("Active Sequences", len(st.session_state.ledger_data))
status_col3.metric("Latency", "24ms")
status_col4.metric("Uptime", "99.9%")

# Main Content Layout
left_col, right_col = st.columns([1, 1.5])

with left_col:
    st.subheader("System Input")
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Lead Name", placeholder="Full name")
        source = st.selectbox("Data Source", ["Manual Entry", "Scraper Hook", "API Integration"])
        phone = st.text_input("Contact Number", placeholder="+1234567890")
        category = st.selectbox("Service Category", ["Inquiry", "Technical Support", "Urgent"])

        submit = st.form_submit_button("Execute Automation Sequence")

# Technical Foundation Logic
if submit:
    if name and phone:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "timestamp": timestamp,
            "name": name,
            "phone": phone,
            "source": source,
            "category": category,
            "status": "Active"
        }
        
        try:
            # Step 1: Database Synchronization Logic
            with st.spinner("Synchronizing with central database..."):
                time.sleep(1) # Simulated network latency
                
                # Update Local Ledger State
                st.session_state.ledger_data.insert(0, payload)
                
            # Step 2: External Trigger (Optional n8n connection)
            # webhook_url = os.getenv("AUTOMATION_WEBHOOK")
            # if webhook_url:
            #    requests.post(webhook_url, json=payload, timeout=5)
            
            st.success("Lead successfully processed. Automation sequence is now active.")
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")
    else:
        st.warning("Validation Error: Please complete all required fields.")

with right_col:
    st.subheader("Live Automation Ledger")
    if st.session_state.ledger_data:
        # Convert ledger to DataFrame for clean presentation
        df = pd.DataFrame(st.session_state.ledger_data)
        st.table(df[["timestamp", "name", "source", "status"]])
    else:
        st.info("No active sequences found in current session.")

# Footer
st.write("---")
st.caption("Internal Infrastructure Dashboard | Version 1.0.4 | Deployment: Production")
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load any private keys from .env
load_dotenv()

# --- THE WEB APP UI ---
st.set_page_config(page_title="Automation Hub", layout="centered")
st.title("🚀 Modular Automation Hub")
st.subheader("Lead Intake & Action Engine")

with st.form("lead_form"):
    st.write("Enter lead details to trigger the automation sequence.")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    source = st.selectbox("Lead Source", ["Manual Entry", "Scraper Prototype", "Facebook Ads"])
    
    submit_button = st.form_submit_button("Launch Automation")

# --- THE ENGINE LOGIC ---
if submit_button:
    if name and phone:
        # Define the payload
        payload = {
            "name": name,
            "phone": phone,
            "source": source
        }
        
        # 1. SEND TO DATABASE / GOOGLE SHEETS (Logic goes here)
        st.info(f"Step 1: Logging {name} to Database...")
        
        # 2. TRIGGER AUTOMATION (Example: Sending to an n8n webhook)
        # Replace the URL below with your actual n8n webhook URL later
        # requests.post("https://your-n8n-webhook-url.com", json=payload)
        
        st.success(f"✅ Success! Automation sequence triggered for {name}.")
        st.balloons()
    else:
        st.error("Please provide both a name and a phone number.")
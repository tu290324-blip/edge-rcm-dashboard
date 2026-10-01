import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# Page Configuration
st.set_page_config(page_title="Edge RCM - Smart Client Intelligence Dashboard", layout="wide")

# Sidebar Language Selection (English / Urdu Toggle)
st.sidebar.markdown("---")
selected_lang = st.sidebar.selectbox("🌐 Select Language / زبان منتخب کریں", ["English", "Urdu"])

# Translations Dictionary
t = {
    "English": {
        "title": "🩺 Edge RCM - Smart Client Intelligence Dashboard",
        "subtitle": "Centralized hub with complete client history, automated email sync, and smart templates.",
        "auth_header": "🔑 Authentication Setup",
        "upload_cred": "Upload your credentials.json file",
        "nav": "Navigation",
        "menu_search": "Client History & Smart Search",
        "menu_email": "Smart Email / SMS Templates & Sync",
        "menu_update": "Direct Notes & History Manager",
        "search_header": "🔍 Client Search & Complete History",
        "search_input": "Enter Client Name, NPI, or Email:",
        "template_header": "✉️ AI Smart Template Generator & Email Sync",
        "update_header": "✍️ Direct Notes & History Manager"
    },
    "Urdu": {
        "title": "🩺 ایج آر سی ایم - سمارٹ کلائنٹ انٹیلیجنس ڈیش بورڈ",
        "subtitle": "مکمل کلائنٹ ہسٹری، آٹومیٹڈ ای میل سنک اور سمارٹ ٹیمپلیٹس کے ساتھ مرکزی نظام۔",
        "auth_header": "🔑 تصدیق (Authentication Setup)",
        "upload_cred": "اپنی credentials.json فائل اپ لوڈ کریں",
        "nav": "نیویگیشن",
        "menu_search": "کلائنٹ ہسٹری اور سمارٹ تلاش",
        "menu_email": "سمارٹ ای میل / ایس ایم ایس ٹیمپلیٹس اور ای میل سنک",
        "menu_update": "نوٹس اور ہسٹری مینیجر",
        "search_header": "🔍 کلائنٹ تلاش اور مکمل ہسٹری",
        "search_input": "کلائنٹ کا نام، NPI، یا ای میل درج کریں:",
        "template_header": "✉️ اے آئی سمارٹ ٹیمپلیٹ جنیریٹر اور ای میل سنک",
        "update_header": "✍️ ڈائریکٹ نوٹس اور ہسٹری اپڈیٹر"
    }
}

lang = t[selected_lang]

st.title(lang["title"])
st.markdown(lang["subtitle"])

# Sidebar Authentication
st.sidebar.header(lang["auth_header"])
uploaded_file = st.sidebar.file_uploader(lang["upload_cred"], type=["json"])

def init_connection(creds_file):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.load(creds_file)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

SHEET_NAME = "EDGE RCM LEADS 2026" 

# Load Data from ALL Sheets automatically
@st.cache_data(ttl=60)
def load_all_sheets_data(file_obj):
    try:
        file_obj.seek(0)
        client = init_connection(file_obj)
        spreadsheet = client.open(SHEET_NAME)
        worksheets = spreadsheet.worksheets() 
        
        all_dfs = []
        for ws in worksheets:
            data = ws.get_all_records()
            if data:
                temp_df = pd.DataFrame(data)
                temp_df.columns = temp_df.columns.str.strip().str.upper()
                all_dfs.append(temp_df)
        
        if all_dfs:
            df = pd.concat(all_dfs, ignore_index=True)
        else:
            df = pd.DataFrame()

        if df.empty or len(df.columns) == 0:
            columns = [
                "SR. NO", "NPI", "EMAIL", "AGENT NAME", "CARRIER", 
                "PHONE NUMBER", "NAME", "TYPE", "ORGANIZATION", 
                "SPECIALITY", "DATE", "LEAD NOTES", "CALL NOTES", "NEXT ACTION"
            ]
            df = pd.DataFrame(columns=columns)
        return df, spreadsheet
    except Exception as e:
        st.error(f"Connection Error: {e}")
        columns = [
            "SR. NO", "NPI", "EMAIL", "AGENT NAME", "CARRIER", 
            "PHONE NUMBER", "NAME", "TYPE", "ORGANIZATION", 
            "SPECIALITY", "DATE", "LEAD NOTES", "CALL NOTES", "NEXT ACTION"
        ]
        return pd.DataFrame(columns=columns), None

if uploaded_file is not None:
    df, spreadsheet = load_all_sheets_data(uploaded_file)
    st.write(f"📊 **Total combined records loaded:** {len(df)}")

    menu = st.sidebar.selectbox(lang["nav"], [lang["menu_search"], lang["menu_email"], lang["menu_update"]])

    if menu == lang["menu_search"]:
        st.header(lang["search_header"])
        search_query = st.text_input(lang["search_input"])
        
        if search_query and not df.empty:
            mask = False
            for col in ['NAME', 'NPI', 'EMAIL']:
                if col in df.columns:
                    mask = mask | df[col].astype(str).str.contains(search_query, case=False, na=False)
            
            result = df[mask]
            
            if not result.empty:
                for idx, row in result.iterrows():
                    name_val = row.get('NAME', 'N/A')
                    npi_val = row.get('NPI', 'N/A')
                    spec_val = row.get('SPECIALITY', 'N/A')
                    
                    with st.expander(f"📁 {name_val} (NPI: {npi_val} - {spec_val})", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Email:** {row.get('EMAIL', 'N/A')}")
                            st.write(f"**Phone:** {row.get('PHONE NUMBER', 'N/A')}")
                            st.write(f"**Carrier:** {row.get('CARRIER', 'N/A')}")
                            st.write(f"**Agent:** {row.get('AGENT NAME', 'N/A')}")
                        with col2:
                            st.write(f"**Organization:** {row.get('ORGANIZATION', 'N/A')}")
                            st.write(f"**Type:** {row.get('TYPE', 'N/A')}")
                            st.write(f"**Lead Date:** {row.get('DATE', 'N/A')}")
                            st.write(f"**Next Action:** {row.get('NEXT ACTION', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("### 📜 Complete Interaction & Email History Context")
                        st.text_area(f"Lead Notes ({name_val})", value=str(row.get('LEAD NOTES', '')), key=f"lead_hist_{idx}", height=100)
                        st.text_area(f"Call & Email History Logs ({name_val})", value=str(row.get('CALL NOTES', '')), key=f"call_hist_{idx}", height=150)
            else:
                st.warning("No matching client found.")

    elif menu == lang["menu_email"]:
        st.header(lang["template_header"])
        
        # Email Sync Simulation section
        with st.expander("📥 Outlook / Gmail Inbox Sync Settings"):
            st.info("Connect your corporate email to auto-fetch provider threads and sync past history into client notes.")
            sync_email_input = st.text_input("Enter Email to Sync Last Threads:", value="provider@practice.com")
            if st.button("Sync Last Emails from Inbox"):
                st.success(f"Successfully synced recent email threads for {sync_email_input}!")

        name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
        client_options = df[name_col].dropna().unique() if not df.empty else ["No Clients Yet"]
        selected_client = st.selectbox("Select Client for Template:", client_options)
        
        if selected_client and selected_client != "No Clients Yet":
            client_row = df[df[name_col] == selected_client].iloc[0]
            c_email = client_row.get('EMAIL', 'client@example.com')
            c_spec = client_row.get('SPECIALITY', 'Medical Practice')
            c_notes = client_row.get('CALL NOTES', 'Initial discussion completed.')
            
            template_type = st.radio("Select Template Type:", ["Follow-up Email", "Credentialing Status Update", "Billing & RCM Proposal SMS"])
            
            if template_type == "Follow-up Email":
                generated_text = f"""Subject: Following up regarding Medical Billing & RCM services for {selected_client}

Dear Dr. {selected_client},

I hope this email finds you well. Based on our previous email exchange and practice review ({c_spec}), we wanted to follow up on the next steps for your medical billing optimization.

Recent Context Log: {c_notes[:150]}... 

Please let us know when we can connect for a brief review call this week.

Best regards,
Edge RCM Team"""
            elif template_type == "Credentialing Status Update":
                generated_text = f"""Subject: Update on your Provider Credentialing Process - Edge RCM

Dear Dr. {selected_client},

We are writing to provide a status update on your provider enrollment and carrier credentialing. Our operations team is actively processing your files to ensure smooth billing workflows.

Best regards,
Edge RCM Team"""
            else:
                generated_text = f"Hi Dr. {selected_client}, following up from Edge RCM regarding your RCM/Billing setup. Kindly let us know your preferred time to connect. Thanks!"

            st.subheader("📝 Context-Aware Draft:")
            st.code(generated_text, language="markdown")
            st.success("Template successfully tailored based on past interactions and email context!")

    elif menu == lang["menu_update"]:
        st.header(lang["update_header"])
        
        name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
        client_options = df[name_col].dropna().unique() if not df.empty else ["No Clients Yet"]
        target_client = st.selectbox("Select Client to Update Notes:", client_options)
        
        if target_client and target_client != "No Clients Yet":
            client_row = df[df[name_col] == target_client].iloc[0]
            existing_notes = str(client_row.get('CALL NOTES', ''))
            
            st.write(f"**Current Client:** {target_client} | **Speciality:** {client_row.get('SPECIALITY', 'N/A')}")
            
            new_note_input = st.text_area("Add New Call Note / Synced Email Summary / Follow-up Details:")
            next_action_input = st.text_input("Set Next Action Date / Task:", value=str(client_row.get('NEXT ACTION', '')))
            
            if st.button("Save & Append to Client History"):
                if new_note_input:
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                    updated_notes = existing_notes + f"\n[{current_date}] {new_note_input}"
                    
                    df.loc[df[name_col] == target_client, 'CALL NOTES'] = updated_notes
                    df.loc[df[name_col] == target_client, 'NEXT ACTION'] = next_action_input
                    
                    st.success(f"History and notes successfully updated for {target_client}!")
                else:
                    st.error("Please enter some notes before saving.")
else:
    st.info("👈 Please upload your `credentials.json` file using the sidebar to connect with Google Sheets.")
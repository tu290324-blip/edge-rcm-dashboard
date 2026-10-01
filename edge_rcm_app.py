import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

st.set_page_config(page_title="Edge RCM - Smart Client Intelligence Dashboard", layout="wide")

st.sidebar.markdown("---")
selected_lang = st.sidebar.selectbox("🌐 Select Language / زبان منتخب کریں", ["English", "Urdu"])

t = {
    "English": {
        "title": "🩺 Edge RCM - Smart Client Intelligence Dashboard",
        "subtitle": "Centralized hub with complete client history and Google Sheets synchronization.",
        "auth": "🔑 Authentication Setup",
        "upload": "Upload your credentials.json file",
        "nav": "Navigation",
        "menu_search": "Client History & Smart Search",
        "menu_email": "Outlook Sync & Smart Templates",
        "menu_update": "Direct Notes & History Manager",
        "search_header": "🔍 Client Search & Complete History",
        "search_input": "Enter Client Name, NPI, or Email:",
        "template_header": "✉️ Outlook Email Sync & Google Sheet Updater",
        "update_header": "✍️ Direct Notes & History Manager"
    },
    "Urdu": {
        "title": "🩺 ایج آر سی ایم - سمارٹ کلائنٹ انٹیلیجنس ڈیش بورڈ",
        "subtitle": "مکمل کلائنٹ ہسٹری اور گوگل شیٹس سنکرونाइजیشن کے ساتھ مرکزی نظام۔",
        "auth": "🔑 تصدیق (Authentication)",
        "upload": "اپنی credentials.json فائل اپ لوڈ کریں",
        "nav": "نیویگیشن",
        "menu_search": "کلائنٹ ہسٹری اور سمارٹ تلاش",
        "menu_email": "آؤٹ لُک سنک اور سمارٹ ٹیمپلیٹس",
        "menu_update": "نوٹس اور ہسٹری مینیجر",
        "search_header": "🔍 کلائنٹ تلاش اور مکمل ہسٹری",
        "search_input": "کلائنٹ کا نام، NPI، یا ای میل درج کریں:",
        "template_header": "✉️ آؤٹ لُک ای میل سنک اور گوگل شیٹ اپڈیٹر",
        "update_header": "✍ ڈائریکٹ نوٹس اور ہسٹری اپڈیٹر"
    }
}

lang = t[selected_lang]

st.title(lang["title"])
st.markdown(lang["subtitle"])

st.sidebar.header(lang["auth"])
uploaded_file = st.sidebar.file_uploader(lang["upload"], type=["json"])

def init_connection(creds_file):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.load(creds_file)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

SHEET_NAME = "EDGE RCM LEADS 2026" 

@st.cache_data(ttl=30)
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
    if not df.empty:
        st.write(f"📊 **Total combined records loaded:** {len(df)}")

        menu = st.sidebar.selectbox(lang["nav"], [lang["menu_search"], lang["menu_email"], lang["menu_update"]])

        if menu == lang["menu_search"]:
            st.header(lang["search_header"])
            search_query = st.text_input(lang["search_input"])
            
            if search_query:
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
            
            with st.expander("📥 Email Sync & Google Sheet Direct Logger", expanded=True):
                st.info("Paste your Outlook email thread summary below or log recent client discussions to instantly update your Google Sheet.")
                
                name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
                client_list = df[name_col].dropna().unique()
                target_client_sync = st.selectbox("Select Client for Email Sync:", client_list, key="sync_client_select")
                
                email_content_input = st.text_area("Paste Outlook Email Thread / Discussion Summary:", height=150, placeholder="Paste email details or conversation notes here...")
                
                if st.button("🚀 Sync & Save directly to Google Sheet CALL NOTES"):
                    if email_content_input:
                        try:
                            # Find client current row data
                            client_row = df[df[name_col] == target_client_sync].iloc[0]
                            existing_notes = str(client_row.get('CALL NOTES', ''))
                            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            
                            # Formulate updated notes
                            formatted_note = f"\n[{current_timestamp} - Synced Email/Note]:\n{email_content_input}"
                            updated_full_notes = existing_notes + formatted_note
                            
                            # Update Google Sheet Worksheet directly
                            ws_target = spreadsheet.worksheets()[0] # First worksheet
                            cell_match = ws_target.find(target_client_sync)
                            
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                if 'CALL NOTES' in header_vals:
                                    col_index = header_vals.index('CALL NOTES') + 1
                                    ws_target.update_cell(cell_match.row, col_index, updated_full_notes)
                                    st.success(f"Successfully updated Google Sheet! Email notes securely saved for {target_client_sync}.")
                                    st.text_area("Updated Google Sheet Notes Preview:", value=updated_full_notes, height=120)
                                else:
                                    st.error("Error: 'CALL NOTES' column header not found in the Google Sheet.")
                            else:
                                st.error(f"Could not locate client '{target_client_sync}' in the Google Sheet rows.")
                        except Exception as e:
                            st.error(f"Google Sheet Update Failed: {e}")
                    else:
                        st.warning("Please enter or paste email text before syncing.")

            st.markdown("---")
            st.subheader("✉️ AI Smart Template Generator")
            selected_client = st.selectbox("Select Client for Template:", client_list, key="template_client_select")
            
            if selected_client:
                client_row = df[df[name_col] == selected_client].iloc[0]
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

        elif menu == lang["menu_update"]:
            st.header(lang["update_header"])
            
            name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
            client_options = df[name_col].dropna().unique()
            target_client = st.selectbox("Select Client to Update Notes:", client_options)
            
            if target_client:
                client_row = df[df[name_col] == target_client].iloc[0]
                existing_notes = str(client_row.get('CALL NOTES', ''))
                
                st.write(f"**Current Client:** {target_client} | **Speciality:** {client_row.get('SPECIALITY', 'N/A')}")
                
                new_note_input = st.text_area("Add New Call Note / Synced Email Summary / Follow-up Details:")
                next_action_input = st.text_input("Set Next Action Date / Task:", value=str(client_row.get('NEXT ACTION', '')))
                
                if st.button("Save & Append to Client History"):
                    if new_note_input:
                        try:
                            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                            updated_notes = existing_notes + f"\n[{current_date}] {new_note_input}"
                            
                            ws_target = spreadsheet.worksheets()[0]
                            cell_match = ws_target.find(target_client)
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                col_index = header_vals.index('CALL NOTES') + 1
                                ws_target.update_cell(cell_match.row, col_index, updated_notes)
                                st.success(f"History and notes successfully updated in Google Sheet for {target_client}!")
                            else:
                                st.error("Client row not found in sheet.")
                        except Exception as e:
                            st.error(f"Failed to update sheet: {e}")
                    else:
                        st.error("Please enter some notes before saving.")
else:
    st.info("👈 Please upload your `credentials.json` file using the sidebar to load your Google Sheets data instantly and securely.")

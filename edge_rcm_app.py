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
        "title": "🩺 Edge RCM - Automated Client Intelligence & History Hub",
        "subtitle": "Automated Outlook Email Sync to LEAD NOTES & Audio Call Transcription to CALL NOTES.",
        "auth": "🔑 Authentication Setup",
        "upload": "Upload your credentials.json file",
        "nav": "Navigation",
        "menu_search": "Client History & Smart Search",
        "menu_auto_sync": "⚡ Fully Automated Email & Call Sync",
        "menu_update": "Direct Notes & History Manager",
        "search_header": "🔍 Client Search & Complete History",
        "auto_sync_header": "⚡ Fully Automated Outlook Email & Call Sync Hub",
        "update_header": "✍ Direct Notes & History Manager"
    },
    "Urdu": {
        "title": "🩺 ایج آر سی ایم - آٹومیٹڈ کلائنٹ انٹیلیجنس اینڈ ہسٹری ہب",
        "subtitle": "آٹومیٹڈ آؤٹ لُک ای میل سنک LEAD NOTES میں اور آڈیو کال ٹرانسکرپشن CALL NOTES میں۔",
        "auth": "🔑 تصدیق (Authentication)",
        "upload": "اپنی credentials.json فائل اپ لوڈ کریں",
        "nav": "نیویگیشن",
        "menu_search": "کلائنٹ ہسٹری اور سمارٹ تلاش",
        "menu_auto_sync": "⚡ مکمل آٹومیٹڈ ای میل اور کال سنک",
        "menu_update": "نوٹس اور ہسٹری مینیجر",
        "search_header": "🔍 کلائنٹ تلاش اور مکمل ہسٹری",
        "auto_sync_header": "⚡ مکمل آٹومیٹڈ آؤٹ لُک ای میل اور کال سنک حب",
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

@st.cache_data(ttl=15)
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

        menu = st.sidebar.selectbox(lang["nav"], [lang["menu_search"], lang["menu_auto_sync"], lang["menu_update"]])

        if menu == lang["menu_search"]:
            st.header(lang["search_header"])
            search_query = st.text_input("Enter Client Name, NPI, or Email:")
            
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
                            st.markdown("### 📜 Client History Logs")
                            st.text_area(f"Lead Notes (Emails & SMS) - ({name_val})", value=str(row.get('LEAD NOTES', '')), key=f"lead_hist_{idx}", height=120)
                            st.text_area(f"Call Notes (Recordings Only) - ({name_val})", value=str(row.get('CALL NOTES', '')), key=f"call_hist_{idx}", height=120)
                else:
                    st.warning("No matching client found.")

        elif menu == lang["menu_auto_sync"]:
            st.header(lang["auto_sync_header"])
            
            name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
            client_options = df[name_col].dropna().unique()
            
            tab_auto_email, tab_auto_call = st.tabs(["⚡ Automated Outlook Email Sync (➔ LEAD NOTES)", "🎙️ Call Recordings Audio Sync (➔ CALL NOTES)"])
            
            with tab_auto_email:
                st.info("💡 **Automated Email Sync:** Select the client, specify the correct email date (to maintain strict chronological order), paste the Outlook email thread, and click **'Auto-Sync to LEAD NOTES'**. It will instantly update your Google Sheet.")
                
                selected_client_email = st.selectbox("Select Client for Email Sync:", client_options, key="auto_email_client")
                email_date_val = st.date_input("Email Date (Chronological Order):", value=datetime.today(), key="auto_email_date")
                email_content_box = st.text_area("Paste Outlook Email Thread / Conversation:", height=150, placeholder="Paste email history here...")
                
                if st.button("⚡ Auto-Sync Email to Google Sheet LEAD NOTES"):
                    if email_content_box:
                        try:
                            client_row = df[df[name_col] == selected_client_email].iloc[0]
                            existing_lead = str(client_row.get('LEAD NOTES', ''))
                            
                            new_entry = f"\n[{email_date_val.strftime('%Y-%m-%d')} - Automated Outlook Email]:\n{email_content_box}"
                            updated_lead_notes = existing_lead + new_entry
                            
                            ws_target = spreadsheet.worksheets()[0]
                            cell_match = ws_target.find(selected_client_email)
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                col_index = header_vals.index('LEAD NOTES') + 1
                                ws_target.update_cell(cell_match.row, col_index, updated_lead_notes)
                                st.success(f"✅ Successfully auto-synced email to LEAD NOTES for {selected_client_email}!")
                                st.text_area("Updated LEAD NOTES Preview:", value=updated_lead_notes, height=130)
                            else:
                                st.error("Client row not found in Google Sheet.")
                        except Exception as e:
                            st.error(f"Sync error: {e}")
                    else:
                        st.warning("Please paste email text first.")

            with tab_auto_call:
                st.info("🎙️ **Automated Call Notes Sync:** Upload your call audio file or enter transcription notes. This will exclusively update the **CALL NOTES** column in Google Sheets while keeping LEAD NOTES untouched.")
                
                selected_client_call = st.selectbox("Select Client for Call Sync:", client_options, key="auto_call_client")
                call_date_val = st.date_input("Call Date:", value=datetime.today(), key="auto_call_date")
                audio_upload_file = st.file_uploader("Upload Call Recording Audio File (mp3/wav/m4a):", type=["mp3", "wav", "m4a", "aac"], key="auto_audio_file")
                call_transcription_box = st.text_area("Call Transcription Summary & Key Points:", height=130, placeholder="Enter call summary or transcription notes...")
                
                if st.button("🎙️ Auto-Sync Call Notes to Google Sheet CALL NOTES"):
                    try:
                        client_row = df[df[name_col] == selected_client_call].iloc[0]
                        existing_calls = str(client_row.get('CALL NOTES', ''))
                        
                        audio_filename = audio_upload_file.name if audio_upload_file else "Call Audio"
                        new_call_entry = f"\n[{call_date_val.strftime('%Y-%m-%d')} - Call Recording ({audio_filename})]:\n{call_transcription_box}"
                        updated_call_notes = existing_calls + new_call_entry
                        
                        ws_target = spreadsheet.worksheets()[0]
                        cell_match = ws_target.find(selected_client_call)
                        if cell_match:
                            header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                            col_index = header_vals.index('CALL NOTES') + 1
                            ws_target.update_cell(cell_match.row, col_index, updated_call_notes)
                            st.success(f"✅ Successfully auto-synced call recording notes to CALL NOTES for {selected_client_call}!")
                            st.text_area("Updated CALL NOTES Preview:", value=updated_call_notes, height=130)
                        else:
                            st.error("Client row not found in Google Sheet.")
                    except Exception as e:
                        st.error(f"Call sync error: {e}")

        elif menu == lang["menu_update"]:
            st.header(lang["update_header"])
            
            name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
            client_options = df[name_col].dropna().unique()
            target_client = st.selectbox("Select Client:", client_options)
            
            if target_client:
                client_row = df[df[name_col] == target_client].iloc[0]
                st.write(f"**Current Client:** {target_client}")
                
                target_column_choice = st.radio("Select Target Column to Update:", ["LEAD NOTES (Emails/SMS)", "CALL NOTES (Calls Only)"])
                manual_note_text = st.text_area("Enter Notes / Update Details:")
                
                if st.button("Save & Update Google Sheet"):
                    if manual_note_text:
                        try:
                            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            ws_target = spreadsheet.worksheets()[0]
                            cell_match = ws_target.find(target_client)
                            
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                if "CALL" in target_column_choice:
                                    col_name = 'CALL NOTES'
                                    current_val = str(client_row.get('CALL NOTES', ''))
                                else:
                                    col_name = 'LEAD NOTES'
                                    current_val = str(client_row.get('LEAD NOTES', ''))
                                    
                                final_updated_val = current_val + f"\n[{current_timestamp}] {manual_note_text}"
                                col_idx = header_vals.index(col_name) + 1
                                ws_target.update_cell(cell_match.row, col_idx, final_updated_val)
                                st.success(f"Successfully updated {col_name} for {target_client}!")
                            else:
                                st.error("Client not found in sheet.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Please enter some text.")
else:
    st.info("👈 Please upload your `credentials.json` file using the sidebar to load your Google Sheets data instantly and securely.")

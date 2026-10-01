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
        "subtitle": "Separated Lead Notes (Emails/SMS) and Call Notes (Audio/Calls) with Google Sheets Sync.",
        "auth": "🔑 Authentication Setup",
        "upload": "Upload your credentials.json file",
        "nav": "Navigation",
        "menu_search": "Client History & Smart Search",
        "menu_sync": "Automated Email (Lead) & Call Notes Sync",
        "menu_update": "Direct Notes & History Manager",
        "search_header": "🔍 Client Search & Complete History",
        "sync_header": "📥 Separate Lead Notes & Call Notes Automation",
        "update_header": "✍ Direct Notes & History Manager"
    },
    "Urdu": {
        "title": "🩺 ایج آر سی ایم - آٹومیٹڈ کلائنٹ انٹیلیجنس اینڈ ہسٹری ہب",
        "subtitle": "لیڈ نوٹس (ای میلز/ایس ایم ایس) اور کال نوٹس (آڈیو/کالز) کی الگ گوگل شیٹس سنک۔",
        "auth": "🔑 تصدیق (Authentication)",
        "upload": "اپنی credentials.json فائل اپ لوڈ کریں",
        "nav": "نیویگیشن",
        "menu_search": "کلائنٹ ہسٹری اور سمارٹ تلاش",
        "menu_sync": "ای میل (لیڈ) اور کال نوٹس آٹومیٹڈ سنک",
        "menu_update": "نوٹس اور ہسٹری مینیجر",
        "search_header": "🔍 کلائنٹ تلاش اور مکمل ہسٹری",
        "sync_header": "📥 لیڈ نوٹس اور کال نوٹس کی الگ آٹومیشن",
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

        menu = st.sidebar.selectbox(lang["nav"], [lang["menu_search"], lang["menu_sync"], lang["menu_update"]])

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

        elif menu == lang["menu_sync"]:
            st.header(lang["sync_header"])
            
            name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
            client_options = df[name_col].dropna().unique()
            selected_client_sync = st.selectbox("Select Client:", client_options)
            
            tab_email, tab_audio = st.tabs(["📧 Outlook Emails ➔ LEAD NOTES", "🎙️ Call Recordings ➔ CALL NOTES"])
            
            with tab_email:
                st.info("Paste your Outlook email threads or message exchanges here. This will automatically update the **LEAD NOTES** column in Google Sheets.")
                
                email_date_input = st.date_input("Select Email Date:", value=datetime.today())
                email_body_input = st.text_area("Paste Email Thread / Subject & Details:", height=140, placeholder="e.g., [12 Sep 2026] Discussed credentialing schedule...")
                
                if st.button("📥 Save Email to Google Sheet LEAD NOTES"):
                    if email_body_input:
                        try:
                            client_row = df[df[name_col] == selected_client_sync].iloc[0]
                            existing_lead_notes = str(client_row.get('LEAD NOTES', ''))
                            formatted_entry = f"\n[{email_date_input.strftime('%Y-%m-%d')} - Email]:\n{email_body_input}"
                            
                            updated_lead_notes = existing_lead_notes + formatted_entry
                            
                            ws_target = spreadsheet.worksheets()[0]
                            cell_match = ws_target.find(selected_client_sync)
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                col_index = header_vals.index('LEAD NOTES') + 1
                                ws_target.update_cell(cell_match.row, col_index, updated_lead_notes)
                                st.success(f"Email successfully saved to LEAD NOTES for {selected_client_sync}!")
                                st.text_area("Updated LEAD NOTES Preview:", value=updated_lead_notes, height=120)
                            else:
                                st.error("Client row not found in Google Sheet.")
                        except Exception as e:
                            st.error(f"Sync error: {e}")
                    else:
                        st.warning("Please enter email text.")

            with tab_audio:
                st.info("Upload your call recording audio file or type call summary notes. This will exclusively update the **CALL NOTES** column in Google Sheets.")
                
                audio_file = st.file_uploader("Upload Call Recording Audio File:", type=["mp3", "wav", "m4a", "aac"])
                call_date_input = st.date_input("Select Call Date:", value=datetime.today(), key="call_date_key")
                call_summary_notes = st.text_area("Call Transcription & Key Takeaways:", height=120, placeholder="e.g., Call completed with Dr. X. Provider confirmed agreement...")
                
                if st.button("🎙️ Save Call Recording to Google Sheet CALL NOTES"):
                    try:
                        client_row = df[df[name_col] == selected_client_sync].iloc[0]
                        existing_call_notes = str(client_row.get('CALL NOTES', ''))
                        
                        audio_name = audio_file.name if audio_file else "Call Audio"
                        formatted_call_note = f"\n[{call_date_input.strftime('%Y-%m-%d')} - Call Recording ({audio_name})]:\n{call_summary_notes}"
                        
                        updated_call_notes = existing_call_notes + formatted_call_note
                        
                        ws_target = spreadsheet.worksheets()[0]
                        cell_match = ws_target.find(selected_client_sync)
                        if cell_match:
                            header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                            col_index = header_vals.index('CALL NOTES') + 1
                            ws_target.update_cell(cell_match.row, col_index, updated_call_notes)
                            st.success(f"Call recording notes successfully saved to CALL NOTES for {selected_client_sync}!")
                            st.text_area("Updated CALL NOTES Preview:", value=updated_call_notes, height=120)
                        else:
                            st.error("Client row not found in Google Sheet.")
                    except Exception as e:
                        st.error(f"Audio processing error: {e}")

        elif menu == lang["menu_update"]:
            st.header(lang["update_header"])
            
            name_col = 'NAME' if 'NAME' in df.columns else df.columns[0]
            client_options = df[name_col].dropna().unique()
            target_client = st.selectbox("Select Client:", client_options)
            
            if target_client:
                client_row = df[df[name_col] == target_client].iloc[0]
                existing_call_notes = str(client_row.get('CALL NOTES', ''))
                
                st.write(f"**Current Client:** {target_client}")
                note_type_target = st.radio("Select Column to Update:", ["CALL NOTES (Calls Only)", "LEAD NOTES (Emails/General)"])
                
                manual_note_input = st.text_area("Enter Note Details:")
                
                if st.button("Save & Update Google Sheet"):
                    if manual_note_input:
                        try:
                            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                            ws_target = spreadsheet.worksheets()[0]
                            cell_match = ws_target.find(target_client)
                            
                            if cell_match:
                                header_vals = [h.strip().upper() for h in ws_target.row_values(1)]
                                if "CALL" in note_type_target:
                                    target_col_name = 'CALL NOTES'
                                    current_existing = str(client_row.get('CALL NOTES', ''))
                                else:
                                    target_col_name = 'LEAD NOTES'
                                    current_existing = str(client_row.get('LEAD NOTES', ''))
                                    
                                updated_text = current_existing + f"\n[{current_date}] {manual_note_input}"
                                col_index = header_vals.index(target_col_name) + 1
                                ws_target.update_cell(cell_match.row, col_index, updated_text)
                                st.success(f"{target_col_name} successfully updated for {target_client}!")
                            else:
                                st.error("Client row not found.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Please enter note text.")
else:
    st.info("👈 Please upload your `credentials.json` file using the sidebar to load your Google Sheets data instantly and securely.")

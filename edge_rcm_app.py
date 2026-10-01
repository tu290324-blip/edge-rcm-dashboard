def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    pk = creds_dict.get("private_key", "")
    if "\\n" in pk:
        pk = pk.replace("\\n", "\n")
    creds_dict["private_key"] = pk

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

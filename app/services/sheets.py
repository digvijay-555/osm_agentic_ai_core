# Google Sheets service

import gspread
from google.oauth2.service_account import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1DBZB2XmLUcYEprwXd0eJaxpIP-CB850jnRNpipZSPR8"

def get_sheet():
    creds_path = os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json")
    if not os.path.exists(creds_path):
        creds_path = "credentials.json"
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"credentials.json not found at {creds_path}")
    
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def append_row(row):
    try:
        sheet = get_sheet()
        sheet.append_row(row)
        print(f"✅ Successfully appended row to Google Sheets: {row[1] if len(row) > 1 else 'N/A'}")
        return True
    except Exception as e:
        print(f"❌ Error appending row to Google Sheets: {e}")
        print(f"   Row data: {row}")
        raise

def read_all():
    try:
        sheet = get_sheet()
        return sheet.get_all_records()
    except Exception as e:
        print(f"❌ Error reading from Google Sheets: {e}")
        return []

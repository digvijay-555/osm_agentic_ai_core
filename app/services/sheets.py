# Google Sheets service (optional export — SQLite is source of truth)

import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")


def sheets_export_enabled() -> bool:
    return os.getenv("ENABLE_SHEETS_EXPORT", "false").lower() in {"1", "true", "yes"}

def get_sheet():
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID is not set in environment")

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
    if not sheets_export_enabled():
        return False

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

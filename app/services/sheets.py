# Google Sheets service

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1DBZB2XmLUcYEprwXd0eJaxpIP-CB850jnRNpipZSPR8"

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def append_row(row):
    sheet = get_sheet()
    sheet.append_row(row)

def read_all():
    sheet = get_sheet()
    return sheet.get_all_records()

# src/update_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open("ExpenseTracker").sheet1

HEADERS = ['Date', 'Merchant', 'Amount', 'RawText', 'Category', 'Transaction_ID']

def initialize_sheet(sheet):
    """Ensure headers exist in row 1. If first row empty, insert headers."""
    try:
        first_row = sheet.row_values(1)
    except Exception:
        first_row = []
    if not first_row or all(cell == "" for cell in first_row):
        sheet.insert_row(HEADERS, index=1)
        print("Headers added to Google Sheet.")

def log_transactions(transactions):
    """Append new transactions while skipping duplicates by Transaction_ID."""
    initialize_sheet(sheet)

    # Get existing Transaction_IDs from column 6 (if any)
    try:
        col_vals = sheet.col_values(6)  # includes header if present
        existing_ids = set(col_vals[1:]) if len(col_vals) > 1 else set()
    except Exception:
        existing_ids = set()

    rows_to_append = []
    for tx in transactions:
        tid = str(tx.get('Transaction_ID', '')).strip()
        if not tid:
            # fallback to some generated id if none
            tid = tx.get('Date','') + "_" + str(tx.get('Amount',''))

        if tid in existing_ids:
            print("⏩ Skipped duplicate transaction:", tid)
            continue

        # Sanitize RawText: remove newlines to avoid odd cell behaviour
        raw = tx.get('RawText', '')
        if raw is None:
            raw = ''
        raw = raw.replace('\n', ' ').replace('\r', ' ')
        # Trim extremely long text to keep the sheet tidy
        if len(raw) > 1000:
            raw = raw[:1000] + '...' 

        row = [
            tx.get('Date', ''),
            tx.get('Merchant', ''),
            str(tx.get('Amount', '')),
            raw,
            tx.get('Category', ''),
            tid
        ]
        rows_to_append.append(row)
        existing_ids.add(tid)

    if rows_to_append:
        # Try batch append first (fewer API calls)
        try:
            sheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
            for r in rows_to_append:
                print("✅ Appended row:", r)
        except AttributeError:
            # Older gspread versions may not have append_rows -> fallback
            for r in rows_to_append:
                sheet.append_row(r)
                print("✅ Appended row:", r)
    else:
        print("No new transactions to append.")

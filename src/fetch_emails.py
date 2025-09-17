import os
import pickle
import re
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from merchant_dictionary import MERCHANT_CATEGORY_MAP

# ---------------------------
# Gmail API setup
# ---------------------------
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ---------------------------
# Load DistilBERT fine-tuned model
# ---------------------------
MODEL_PATH = "models/expense_classifier_bert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
bert_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

LABELS = ["Bills", "Credit", "Entertainment", "Food",
          "Miscellaneous", "Online Shopping", "Stationery",
          "Transfer", "Travel"]

def bert_categorize(raw_text):
    inputs = tokenizer(raw_text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    pred_idx = torch.argmax(probs).item()
    return LABELS[pred_idx]

# ---------------------------
# Gmail authentication
# ---------------------------
def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# ---------------------------
# Merchant extraction helper
# ---------------------------
def parse_merchant(raw_text):
    vpa_pattern = r'to VPA ([\w\.\-@]+)'
    name_pattern = r'to VPA [\w\.\-@]+\s+([A-Z][\w\s\-&]+?)(?:\s+on|\s+\d{2}-\d{2}-\d{2})'

    name_match = re.search(name_pattern, raw_text)
    if name_match:
        return name_match.group(1).strip()

    vpa_match = re.search(vpa_pattern, raw_text)
    if vpa_match:
        return vpa_match.group(1)

    return "Unknown"

# ---------------------------
# Category logic: Dictionary first, fallback to BERT
# ---------------------------
def categorize_with_dictionary(merchant, raw_text):
    merchant_upper = merchant.upper().strip()
    if merchant_upper in MERCHANT_CATEGORY_MAP:
        return MERCHANT_CATEGORY_MAP[merchant_upper]
    return bert_categorize(raw_text)

# ---------------------------
# Email parsing
# ---------------------------
def parse_email_to_transaction(msg):
    snippet = msg.get('snippet', '').replace("\n", " ").replace("\r", " ")
    if len(snippet) > 800:
        snippet = snippet[:800] + "..."

    # Date
    date = datetime.fromtimestamp(int(msg.get('internalDate', 0)) / 1000).strftime('%Y-%m-%d')

    # Amount
    amount_match = re.search(r'(?:Rs\.?|INR)\s?(\d+(?:\.\d{1,2})?)', snippet, re.IGNORECASE)
    amount = f"{float(amount_match.group(1)):.2f}" if amount_match else "0.00"

    # Merchant
    merchant = parse_merchant(snippet)
    if merchant == "Unknown":
        vpa_fallback = re.search(r'[\w\.\-]+@[\w\-]+', snippet)
        if vpa_fallback:
            merchant = vpa_fallback.group(0)

    # Transaction ID
    txid_match = re.search(
        r'(?:transaction reference number is|transaction ref no\.?|ref no\.?|reference number)\s*[:\-]?\s*([0-9A-Za-z]+)',
        snippet,
        re.IGNORECASE
    )
    transaction_id = txid_match.group(1) if txid_match else msg.get('id', '')

    # Category
    category = categorize_with_dictionary(merchant, snippet)

    return {
        'Date': date,
        'Merchant': merchant,
        'Amount': amount,
        'RawText': snippet,
        'Category': category,
        'Transaction_ID': transaction_id
    }

# ---------------------------
# Fetch transactions
# ---------------------------
def fetch_transaction_emails(service, max_results=100):
    results = service.users().messages().list(userId='me', q='transaction', maxResults=max_results).execute()
    messages = results.get('messages', [])

    transactions = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        tx = parse_email_to_transaction(msg)
        transactions.append(tx)

    return transactions

from fetch_emails import authenticate_gmail, fetch_transaction_emails
from update_sheets import log_transactions

if __name__ == "__main__":
    service = authenticate_gmail()
    # Fetch last 100 transactions
    transactions = fetch_transaction_emails(service, max_results=100)

    print(f"Fetched {len(transactions)} transactions:")
    for tx in transactions:
        print(tx)

    log_transactions(transactions)
    print("✅ All transactions processed and logged.")

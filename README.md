NAME- Abhyuday Kashyap
University- Indian Institute of Technology, Guwahati
Department: Chemistry

# Expense Agent 🚀  

An AI-powered **personal expense tracker** that integrates with Gmail and Google Sheets.  

## ✨ Features
- Fetches **transaction emails** from Gmail using Gmail API
- Extracts **merchant name, amount, transaction ID**
- Uses **fine-tuned DistilBERT** for automatic expense categorization
- Logs structured data into **Google Sheets**
- Supports **dictionary-based overrides** for local merchants
- Skips **duplicate transactions**

## 📂 Project Structure
expense-agent/
│
├── src/
│ ├── fetch_emails.py # Gmail parsing + BERT categorization
│ ├── update_sheets.py # Google Sheets integration
│ ├── pipeline.py # Full pipeline runner
│ └── models/
│ └── bert_finetuned/ # Fine-tuned DistilBERT model
│
├── data/
│ └── transactions.csv # Labeled dataset for fine-tuning
│
├── docs/
│ ├── architecture.png # System diagram
│ ├── report.md # Data science report
│ └── interactions.md # Logs of prompts & outputs
│
├── requirements.txt
├── README.md
└── .gitignore

Model Download (Required)

The fine-tuned DistilBERT model is too large for GitHub.
👉 Download it here: https://drive.google.com/drive/folders/147IpRDHg06S6Y56jUxwCpFmGt20iRutf?usp=sharing


bash
Copy code

## 🛠️ Setup
1. Clone the repo:
```bash
git clone <your_repo_url>
cd expense-agent
Create virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Add Google API credentials:

Place your credentials.json and service_account.json in the root directory.

Run once to generate token.pickle.

Run the agent:

bash
Copy code
python src/pipeline.py
📊 Architecture

Flow:
Gmail API → Parser → DistilBERT Classifier → Categorized Transaction → Google Sheets

🤖 AI Model
Baseline: Naive Bayes classifier (TF-IDF) for expense classification

Final: Fine-tuned DistilBERT on 950+ labeled transactions

Accuracy: ~90% on validation set

Handles unseen merchants with dictionary overrides

⚠️ Note
credentials.json, service_account.json, and token.pickle are private and excluded from GitHub.

Push your code but keep credentials safe.
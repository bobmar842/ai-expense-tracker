# Data Science Report

## Dataset
- Source: `transactions.csv` (950 real + synthetic rows)
- Columns: Date, Merchant, Amount, RawText, Category

## Fine-Tuning Setup
- Model: DistilBERT (parameter-efficient fine-tuning)
- Epochs: 3
- Optimizer: AdamW
- Loss: CrossEntropy
- Input: RawText
- Output: Categories (Bills, Food, Travel, Entertainment, Credit, etc.)

## Results
- Validation Accuracy: ~90%
- Issue: Bias toward frequent classes → mitigated with dictionary overrides

## Evaluation
- Metrics: Accuracy, F1-Score, Confusion Matrix
- Qualitative evaluation: Checked with real Gmail transaction emails
- Dictionary integration improved classification for local merchants

## Why Fine-Tuning?
- NB baseline was lightweight but missed contextual cues
- DistilBERT improved reliability on unseen text formats
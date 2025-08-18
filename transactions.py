from persistence import get_transactions, update_data
from utils import get_month_key
import pandas as pd

def add_transaction(year, month, category, amount, description=""):
    transactions = get_transactions()
    month_key = get_month_key(year, month)
    if month_key not in transactions:
        transactions[month_key] = []
    transactions[month_key].append({
        "category": category,
        "amount": amount,
        "description": description,
        "date": f"{year}-{month:02d}"
    })
    update_data("transactions", transactions)

def import_transactions_from_csv(file_path, year, month):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        cat = row.get("Category", "Uncategorized")
        amt = float(row.get("Amount", 0))
        desc = row.get("Description", "")
        add_transaction(year, month, cat, amt, desc)

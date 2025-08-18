import json
import os
from datetime import datetime

DATA_FILE = "budget_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"budgets": {}, "transactions": {}, "scenarios": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)

def get_month_key(year, month):
    return f"{year}-{month:02d}"

def calculate_remaining(budget, spent):
    return budget - spent

def format_currency(value):
    return f"₹{value:,}"

def get_alert_color(remaining, budget, threshold_percent=10):
    if budget == 0:
        return "green"
    if remaining <= 0:
        return "red"
    if remaining <= (budget * threshold_percent / 100):
        return "orange"
    return "green"

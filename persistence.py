from utils import load_data, save_data

data = load_data()

def get_budgets():
    return data.get("budgets", {})

def get_transactions():
    return data.get("transactions", {})

def get_scenarios():
    return data.get("scenarios", {})

def update_data(key, value):
    data[key] = value
    save_data(data)

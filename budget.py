from persistence import get_budgets, update_data

def set_budget(year, month, category, amount):
    budgets = get_budgets()
    month_key = f"{year}-{month:02d}"
    if month_key not in budgets:
        budgets[month_key] = {}
    budgets[month_key][category] = amount
    update_data("budgets", budgets)

def get_monthly_budget(year, month):
    budgets = get_budgets()
    month_key = f"{year}-{month:02d}"
    return budgets.get(month_key, {})

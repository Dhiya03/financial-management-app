from transactions import get_transactions
from budget import get_monthly_budget
from utils import format_currency, get_alert_color

try:
    import matplotlib.pyplot as plt
except:
    plt = None

def plot_category_breakdown(year, month, threshold_percent=10):
    if plt is None:
        print("Matplotlib not installed. Skipping plots.")
        return
    
    budgets = get_monthly_budget(year, month)
    transactions = get_transactions()
    month_key = f"{year}-{month:02d}"
    spent_per_category = {}
    for t in transactions.get(month_key, []):
        cat = t["category"]
        spent_per_category[cat] = spent_per_category.get(cat, 0) + t["amount"]
    
    categories = list(budgets.keys()) + ["Uncategorized"]
    spent = [spent_per_category.get(c, 0) for c in categories]
    planned = [budgets.get(c, 0) for c in categories]
    colors = [get_alert_color(planned[i]-spent[i], planned[i], threshold_percent) for i in range(len(categories))]
    
    plt.bar(categories, spent, color=colors)
    plt.title(f"Category Breakdown {year}-{month:02d}")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

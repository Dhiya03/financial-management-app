# config.py
# Configurable parameters for the Budget Tracker app

# File paths
DATA_FILE = "data.json"           # JSON file to store all monthly budgets & transactions
EXPORT_FOLDER = "exports"         # Folder to save Excel / PDF reports

# Categories
DEFAULT_CATEGORIES = [
    "Loan",
    "Mutual Fund",
    "Hospital",
    "Swiggy",
    "Petrol",
    "Day-to-day",
    "Uncategorized"
]

# Alert thresholds
CATEGORY_ALERT_THRESHOLD_PERCENT = 10  # Default threshold to warn if remaining budget is below this percent

# GUI Settings
WINDOW_TITLE = "Personal Budget Tracker"
WINDOW_SIZE = "1000x700"

# Misc
DATE_FORMAT = "%Y-%m-%d"

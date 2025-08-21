"""
Input validation functions
"""

from datetime import datetime
from typing import Tuple, List, Dict, Any
from config import MIN_AMOUNT, MAX_AMOUNT, PLANNING_MONTHS

def validate_amount(amount: Any) -> bool:
    """Validate if amount is a valid positive number"""
    try:
        float_amount = float(amount)
        return MIN_AMOUNT <= float_amount <= MAX_AMOUNT
    except (ValueError, TypeError):
        return False

def validate_date(date_str: str) -> bool:
    """Validate date string in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_month(month: str) -> bool:
    """Validate if month is in planning period"""
    return month in PLANNING_MONTHS

def validate_transaction(transaction_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate transaction data"""
    errors = []
    
    # Validate date
    date_str = transaction_data.get("date", "")
    if not date_str:
        errors.append("Date is required")
    elif not validate_date(date_str):
        errors.append("Date must be in YYYY-MM-DD format")
    
    # Validate category
    category = transaction_data.get("category", "")
    if not category or category.strip() == "":
        errors.append("Category is required")
    
    # Validate amount
    amount = transaction_data.get("amount", 0)
    if not validate_amount(amount):
        errors.append(f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT}")
    
    return len(errors) == 0, errors

def validate_budget(budget_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate budget data"""
    errors = []
    
    month = budget_data.get("month", "")
    if not validate_month(month):
        errors.append(f"Invalid month. Must be between Aug-25 and Jul-27")
    
    category = budget_data.get("category", "")
    if not category or category.strip() == "":
        errors.append("Category is required")
    
    amount = budget_data.get("amount", 0)
    try:
        amount_float = float(amount)
        if amount_float < 0:
            errors.append("Budget amount cannot be negative")
        elif amount_float > MAX_AMOUNT:
            errors.append(f"Budget amount cannot exceed {MAX_AMOUNT}")
    except (ValueError, TypeError):
        errors.append("Budget amount must be a valid number")
    
    return len(errors) == 0, errors

def validate_csv_headers(headers: List[str]) -> Tuple[bool, List[str]]:
    """Validate CSV file headers"""
    required_headers = ["date", "amount"]
    missing_headers = []
    
    headers_lower = [h.lower() for h in headers]
    
    for required in required_headers:
        if required not in headers_lower:
            missing_headers.append(required)
    
    if missing_headers:
        return False, [f"Missing required headers: {', '.join(missing_headers)}"]
    
    return True, []

def validate_scenario(scenario_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate scenario data"""
    errors = []
    
    name = scenario_data.get("name", "")
    if not name or name.strip() == "":
        errors.append("Scenario name is required")
    
    scenario_type = scenario_data.get("type", "")
    valid_types = ["budget_change", "one_time_event", "investment_adjustment"]
    if scenario_type not in valid_types:
        errors.append(f"Invalid scenario type. Must be one of: {', '.join(valid_types)}")
    
    changes = scenario_data.get("changes", [])
    if not changes:
        errors.append("At least one change is required")
    
    return len(errors) == 0, errors

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def validate_email(email: str) -> bool:
    """Validate email format (for future features)"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_percentage(value: Any) -> bool:
    """Validate percentage value (0-100)"""
    try:
        percentage = float(value)
        return 0 <= percentage <= 100
    except (ValueError, TypeError):
        return False

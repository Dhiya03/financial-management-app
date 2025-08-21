"""
Format currency, dates, and other data
"""

from datetime import datetime
from typing import Optional
from config import CURRENCY_SYMBOL

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1f}%"

def format_date(date_str: str, output_format: str = "%d-%m-%Y") -> str:
    """Format date string to specified format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str

def format_month_year(month: str) -> str:
    """Format month abbreviation to full month year"""
    try:
        # Convert "Aug-25" to "August 2025"
        month_names = {
            "Jan": "January", "Feb": "February", "Mar": "March",
            "Apr": "April", "May": "May", "Jun": "June",
            "Jul": "July", "Aug": "August", "Sep": "September",
            "Oct": "October", "Nov": "November", "Dec": "December"
        }
        
        parts = month.split("-")
        if len(parts) == 2:
            month_abbr = parts[0]
            year_short = parts[1]
            
            if month_abbr in month_names:
                full_month = month_names[month_abbr]
                full_year = f"20{year_short}"
                return f"{full_month} {full_year}"
        
        return month
    except Exception:
        return month

def format_number(number: float, decimal_places: int = 2) -> str:
    """Format number with thousand separators"""
    return f"{number:,.{decimal_places}f}"

def parse_currency(currency_str: str) -> Optional[float]:
    """Parse currency string to float"""
    try:
        # Remove currency symbol and commas
        cleaned = currency_str.replace(CURRENCY_SYMBOL, "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%b-%Y",
        "%d %B %Y"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def safe_divide(numerator: float, denominator: float) -> float:
    """Safe division with zero check"""
    return numerator / denominator if denominator != 0 else 0

def format_status(percentage: float) -> str:
    """Format status based on percentage"""
    if percentage < 80:
        return "On Track"
    elif percentage < 100:
        return "Warning"
    else:
        return "Over Budget"

def get_status_color(percentage: float) -> str:
    """Get color based on percentage"""
    if percentage < 80:
        return "green"
    elif percentage < 100:
        return "yellow"
    else:
        return "red"

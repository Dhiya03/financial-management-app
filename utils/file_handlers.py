"""
File import/export utilities
"""
import csv
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

def export_to_csv(data: List[Dict[str, Any]], file_path: str) -> bool:
    """Export data to CSV file"""
    try:
        if not data:
            logging.warning("No data to export")
            return False

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        logging.info(f"Exported {len(data)} rows to {file_path}")
        return True

    except Exception as e:
        logging.error(f"Failed to export CSV: {e}")
        return False

def export_to_json(data: Dict[str, Any], file_path: str) -> bool:
    """Export data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        logging.info(f"Exported data to {file_path}")
        return True

    except Exception as e:
        logging.error(f"Failed to export JSON: {e}")
        return False

def import_from_csv(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """Import data from CSV file"""
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(dict(row))

        logging.info(f"Imported {len(data)} rows from {file_path}")
        return data

    except Exception as e:
        logging.error(f"Failed to import CSV: {e}")
        return None

def import_from_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Import data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        logging.info(f"Imported data from {file_path}")
        return data

    except Exception as e:
        logging.error(f"Failed to import JSON: {e}")
        return None

def export_to_excel(data: Dict[str, List[Dict[str, Any]]], file_path: str) -> bool:
    """Export data to Excel file (requires pandas and openpyxl)"""
    try:
        import pandas as pd

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if sheet_data:
                    df = pd.DataFrame(sheet_data)
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        logging.info(f"Exported data to Excel: {file_path}")
        return True

    except ImportError:
        logging.warning("pandas/openpyxl not installed - Excel export unavailable")
        return False
    except Exception as e:
        logging.error(f"Failed to export Excel: {e}")
        return False

def generate_pdf_report(data: Dict[str, Any], file_path: str) -> bool:
    """Generate PDF report (placeholder - requires additional libraries)"""
    try:
        # TODO: Implement PDF generation
        # This would require libraries like reportlab or weasyprint
        logging.info("PDF generation not yet implemented")
        return False

    except Exception as e:
        logging.error(f"Failed to generate PDF: {e}")
        return False

def validate_csv_format(file_path: str, required_columns: List[str]) -> tuple[bool, str]:
    """Validate CSV file format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames or []

            missing_columns = [col for col in required_columns if col not in headers]

            if missing_columns:
                return False, f"Missing columns: {', '.join(missing_columns)}"

            return True, "Valid format"

    except Exception as e:
        return False, f"Error reading file: {str(e)}"

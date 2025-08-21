"""
Transaction operations manager
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import csv

from models.transaction import Transaction
from managers.category_manager import CategoryManager

class TransactionManager:
    """Manages transaction operations"""
    
    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
        self.category_manager = CategoryManager()
    
    def add_transaction(self, date: str, category: str, amount: float, 
                       description: str = "", source: str = "manual") -> Tuple[bool, str]:
        """Add a new transaction"""
        try:
            transaction = Transaction(
                date=date,
                category=category,
                amount=amount,
                description=description,
                source=source
            )
            
            # Validate transaction
            is_valid, errors = transaction.validate()
            if not is_valid:
                return False, "; ".join(errors)
            
            # Get month from date
            month = self.get_month_from_date(date)
            if not month:
                return False, "Invalid date format"
            
            # Add to data structure
            if month not in self.app_data.transactions:
                self.app_data.transactions[month] = []
            
            self.app_data.transactions[month].append(transaction.to_dict())
            
            # Save data
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Added transaction: {category} - {amount}")
                return True, "Transaction added successfully"
            else:
                return False, "Failed to save transaction"
                
        except Exception as e:
            logging.error(f"Error adding transaction: {e}")
            return False, f"Error adding transaction: {str(e)}"
    
    def get_month_from_date(self, date_str: str) -> Optional[str]:
        """Extract month from date string"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_abbr = month_names[date_obj.month - 1]
            year_short = str(date_obj.year)[2:]
            return f"{month_abbr}-{year_short}"
        except ValueError:
            return None
    
    def get_transactions_for_month(self, month: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific month"""
        return self.app_data.transactions.get(month, [])
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions across all months"""
        all_transactions = []
        for transactions in self.app_data.transactions.values():
            all_transactions.extend(transactions)
        return all_transactions
    
    def get_transactions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific category"""
        category_transactions = []
        for transactions in self.app_data.transactions.values():
            for transaction in transactions:
                if transaction.get('category') == category:
                    category_transactions.append(transaction)
        return category_transactions
    
    def calculate_spending_by_category(self, month: str = None) -> Dict[str, float]:
        """Calculate total spending by category"""
        spending = {}
        
        if month:
            transactions = self.get_transactions_for_month(month)
        else:
            transactions = self.get_all_transactions()
        
        for transaction in transactions:
            category = transaction.get('category', 'Uncategorized')
            amount = transaction.get('amount', 0)
            spending[category] = spending.get(category, 0) + amount
        
        return spending
    
    def import_from_csv(self, file_path: str) -> Tuple[bool, str, int]:
        """Import transactions from CSV file"""
        try:
            imported_count = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Map CSV columns to transaction fields
                        date = row.get('Date', row.get('date', ''))
                        description = row.get('Description', row.get('description', ''))
                        amount = float(row.get('Amount', row.get('amount', 0)))
                        category = row.get('Category', row.get('category', ''))
                        
                        # Auto-categorize if no category provided
                        if not category and description:
                            category = self.category_manager.auto_categorize_transaction(description)
                            if not category:
                                category = "Uncategorized"
                        
                        # Add transaction
                        success, message = self.add_transaction(
                            date, category, amount, description, "imported"
                        )
                        
                        if success:
                            imported_count += 1
                        else:
                            errors.append(f"Row {row_num}: {message}")
                            
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            if errors:
                error_msg = f"Imported {imported_count} transactions with {len(errors)} errors"
                return True, error_msg, imported_count
            else:
                return True, f"Successfully imported {imported_count} transactions", imported_count
                
        except Exception as e:
            logging.error(f"CSV import error: {e}")
            return False, f"Failed to import CSV: {str(e)}", 0
    
    def delete_transaction(self, transaction_id: str) -> Tuple[bool, str]:
        """Delete a transaction by ID"""
        try:
            for month, transactions in self.app_data.transactions.items():
                for i, transaction in enumerate(transactions):
                    if transaction.get('id') == transaction_id:
                        del self.app_data.transactions[month][i]
                        from managers.data_manager import data_manager
                        if data_manager.save():
                            return True, "Transaction deleted successfully"
                        else:
                            return False, "Failed to save after deletion"
            
            return False, "Transaction not found"
            
        except Exception as e:
            logging.error(f"Error deleting transaction: {e}")
            return False, f"Error deleting transaction: {str(e)}"
    
    def update_transaction(self, transaction_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update an existing transaction"""
        try:
            for month, transactions in self.app_data.transactions.items():
                for transaction in transactions:
                    if transaction.get('id') == transaction_id:
                        # Update fields
                        transaction.update(updates)
                        transaction['modified_at'] = datetime.now().isoformat()
                        
                        from managers.data_manager import data_manager
                        if data_manager.save():
                            return True, "Transaction updated successfully"
                        else:
                            return False, "Failed to save updates"
            
            return False, "Transaction not found"
            
        except Exception as e:
            logging.error(f"Error updating transaction: {e}")
            return False, f"Error updating transaction: {str(e)}"

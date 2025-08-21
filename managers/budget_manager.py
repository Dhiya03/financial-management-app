"""
Budget operations manager
"""

import logging
from typing import Dict, List, Tuple

from config import BUDGET_TEMPLATES, PLANNING_MONTHS

class BudgetManager:
    """Manages budget operations"""
    
    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
    
    def set_budget(self, month: str, category: str, amount: float) -> Tuple[bool, str]:
        """Set budget for a category in a specific month"""
        try:
            # Validate inputs
            if month not in PLANNING_MONTHS:
                return False, f"Invalid month. Must be one of: {', '.join(PLANNING_MONTHS[:3])}..."
            
            if amount < 0:
                return False, "Budget amount cannot be negative"
            
            # Initialize month budget if not exists
            if month not in self.app_data.budgets:
                self.app_data.budgets[month] = {}
            
            # Set budget amount
            self.app_data.budgets[month][category] = amount
            
            # Save changes
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Set budget for {month}/{category}: {amount}")
                return True, "Budget saved successfully"
            else:
                return False, "Failed to save budget"
                
        except Exception as e:
            logging.error(f"Error setting budget: {e}")
            return False, f"Error setting budget: {str(e)}"
    
    def get_budget(self, month: str, category: str) -> float:
        """Get budget amount for a category in a specific month"""
        return self.app_data.budgets.get(month, {}).get(category, 0.0)
    
    def get_month_budget(self, month: str) -> Dict[str, float]:
        """Get all budgets for a specific month"""
        return self.app_data.budgets.get(month, {})
    
    def get_total_budget(self, month: str) -> float:
        """Get total budget for a month"""
        month_budgets = self.get_month_budget(month)
        return sum(month_budgets.values())
    
    def copy_budget_from_month(self, source_month: str, target_month: str) -> Tuple[bool, str]:
        """Copy budget from one month to another"""
        try:
            if source_month not in self.app_data.budgets:
                return False, f"No budget data found for {source_month}"
            
            # Copy budget data
            source_budgets = self.app_data.budgets[source_month].copy()
            self.app_data.budgets[target_month] = source_budgets
            
            # Save changes
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Copied budget from {source_month} to {target_month}")
                return True, f"Budget copied from {source_month} to {target_month}"
            else:
                return False, "Failed to save budget"
                
        except Exception as e:
            logging.error(f"Error copying budget: {e}")
            return False, f"Error copying budget: {str(e)}"
    
    def apply_template(self, template_name: str, months: List[str]) -> Tuple[bool, str]:
        """Apply a budget template to specified months"""
        try:
            if template_name not in BUDGET_TEMPLATES:
                return False, f"Template '{template_name}' not found"
            
            template = BUDGET_TEMPLATES[template_name]
            applied_count = 0
            
            for month in months:
                if month in PLANNING_MONTHS:
                    self.app_data.budgets[month] = template.copy()
                    applied_count += 1
            
            if applied_count == 0:
                return False, "No valid months to apply template"
            
            # Save changes
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Applied template '{template_name}' to {applied_count} months")
                return True, f"Template applied to {applied_count} months"
            else:
                return False, "Failed to save budget"
                
        except Exception as e:
            logging.error(f"Error applying template: {e}")
            return False, f"Error applying template: {str(e)}"
    
    def auto_fill_all_months(self, base_template: str = "Conservative") -> Tuple[bool, str]:
        """Auto-fill all 24 months with a base template"""
        try:
            success, message = self.apply_template(base_template, PLANNING_MONTHS)
            if success:
                return True, f"Auto-filled all 24 months with {base_template} template"
            else:
                return False, message
                
        except Exception as e:
            logging.error(f"Error in auto-fill: {e}")
            return False, f"Error in auto-fill: {str(e)}"
    
    def calculate_budget_variance(self, month: str, actual_spending: Dict[str, float]) -> Dict[str, float]:
        """Calculate variance between budget and actual spending"""
        variances = {}
        budgets = self.get_month_budget(month)
        
        all_categories = set(budgets.keys()) | set(actual_spending.keys())
        
        for category in all_categories:
            budget_amount = budgets.get(category, 0)
            spent_amount = actual_spending.get(category, 0)
            variances[category] = budget_amount - spent_amount
        
        return variances
    
    def get_budget_adherence(self, month: str, actual_spending: Dict[str, float]) -> float:
        """Calculate overall budget adherence percentage"""
        total_budget = self.get_total_budget(month)
        total_spent = sum(actual_spending.values())
        
        if total_budget == 0:
            return 0
        
        return (total_spent / total_budget) * 100
    
    def identify_over_budget_categories(self, month: str, actual_spending: Dict[str, float]) -> List[str]:
        """Identify categories that are over budget"""
        over_budget = []
        budgets = self.get_month_budget(month)
        
        for category, budget_amount in budgets.items():
            spent_amount = actual_spending.get(category, 0)
            if spent_amount > budget_amount:
                over_budget.append(category)
        
        return over_budget
    
    def suggest_budget_adjustments(self, month: str, actual_spending: Dict[str, float]) -> Dict[str, float]:
        """Suggest budget adjustments based on spending patterns"""
        suggestions = {}
        budgets = self.get_month_budget(month)
        
        for category, budget_amount in budgets.items():
            spent_amount = actual_spending.get(category, 0)
            
            # Suggest increase if consistently overspending
            if spent_amount > budget_amount * 1.2:  # Over by 20%
                suggestions[category] = spent_amount * 1.1  # Add 10% buffer
            # Suggest decrease if consistently underspending
            elif spent_amount < budget_amount * 0.5:  # Under by 50%
                suggestions[category] = spent_amount * 1.2  # Add 20% buffer
        
        return suggestions

"""
Budget planning tab - Fixed for Python 3.13 compatibility
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys

from config import DEFAULT_CATEGORIES, PLANNING_MONTHS
from managers.budget_manager import BudgetManager

class BudgetTab:
    """Budget planning tab"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.current_month = "Aug-25"
        self.budget_manager = BudgetManager()
        self.budget_vars = {}
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup budget tab UI"""
        # Header with month selector and actions
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Month:").pack(side='left')
        self.month_var = tk.StringVar(value=self.current_month)
        month_combo = ttk.Combobox(header_frame, textvariable=self.month_var,
                                  values=PLANNING_MONTHS, state='readonly')
        month_combo.pack(side='left', padx=(10, 20))
        month_combo.bind('<<ComboboxSelected>>', self.on_month_changed)
        
        ttk.Button(header_frame, text="Copy from Previous", 
                  command=self.copy_from_previous).pack(side='right', padx=(10, 0))
        ttk.Button(header_frame, text="Apply Template", 
                  command=self.apply_template).pack(side='right', padx=(10, 0))
        ttk.Button(header_frame, text="Auto-fill 24 Months", 
                  command=self.auto_fill_months).pack(side='right', padx=(10, 0))
        ttk.Button(header_frame, text="Save Budget", 
                  command=self.save_budget).pack(side='right')
        
        # Create scrollable frame for budget entries
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create category group frames
        self.category_frames = {}
        
        for group_name, categories in DEFAULT_CATEGORIES.items():
            if group_name == "Custom":
                continue
            
            # Create group frame
            group_frame = ttk.LabelFrame(scrollable_frame, text=group_name, padding=15)
            group_frame.pack(fill='x', padx=10, pady=10)
            
            self.category_frames[group_name] = group_frame
            self.budget_vars[group_name] = {}
            
            # Create budget entry for each category
            for category in categories:
                cat_frame = ttk.Frame(group_frame)
                cat_frame.pack(fill='x', pady=2)
                
                ttk.Label(cat_frame, text=category, width=25).pack(side='left')
                
                var = tk.StringVar(value="0")
                self.budget_vars[group_name][category] = var
                entry = ttk.Entry(cat_frame, textvariable=var, width=15)
                entry.pack(side='right')
                
                # Add currency label
                ttk.Label(cat_frame, text="₹").pack(side='right', padx=(0, 5))
        
        # Add total display
        self.total_frame = ttk.LabelFrame(scrollable_frame, text="Monthly Total", padding=15)
        self.total_frame.pack(fill='x', padx=10, pady=10)
        
        self.total_label = ttk.Label(self.total_frame, text="Total: ₹0", font=('Arial', 12, 'bold'))
        self.total_label.pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind entry changes to update total - Fixed for Python 3.13
        for group_vars in self.budget_vars.values():
            for var in group_vars.values():
                # Check Python version and use appropriate method
                if sys.version_info >= (3, 13):
                    # Python 3.13+ uses trace_add
                    var.trace_add('write', lambda *args: self.update_total())
                else:
                    # Older versions use trace
                    var.trace('w', lambda *args: self.update_total())
    
    def on_month_changed(self, event=None):
        """Handle month selection change"""
        self.current_month = self.month_var.get()
        self.load_budget_data()
    
    def load_budget_data(self):
        """Load budget data for selected month"""
        try:
            budgets = self.budget_manager.get_month_budget(self.current_month)
            
            for group_name, group_vars in self.budget_vars.items():
                for category, var in group_vars.items():
                    amount = budgets.get(category, 0)
                    var.set(str(amount))
            
            self.update_total()
            
        except Exception as e:
            logging.error(f"Error loading budget data: {e}")
    
    def save_budget(self):
        """Save budget for current month"""
        try:
            errors = []
            
            for group_name, group_vars in self.budget_vars.items():
                for category, var in group_vars.items():
                    try:
                        amount = float(var.get() or 0)
                        success, message = self.budget_manager.set_budget(
                            self.current_month, category, amount
                        )
                        if not success:
                            errors.append(f"{category}: {message}")
                    except ValueError:
                        errors.append(f"{category}: Invalid amount")
            
            if errors:
                messagebox.showerror("Validation Errors", "\n".join(errors))
            else:
                messagebox.showinfo("Success", f"Budget saved for {self.current_month}")
                
        except Exception as e:
            logging.error(f"Error saving budget: {e}")
            messagebox.showerror("Error", f"Failed to save budget: {str(e)}")
    
    def copy_from_previous(self):
        """Copy budget from previous month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx > 0:
                previous_month = PLANNING_MONTHS[current_idx - 1]
                success, message = self.budget_manager.copy_budget_from_month(
                    previous_month, self.current_month
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.load_budget_data()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showwarning("Warning", "No previous month available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy budget: {str(e)}")
    
    def apply_template(self):
        """Open template dialog"""
        from gui.dialogs.template_dialog import TemplateDialog
        TemplateDialog(self.frame, self.current_month, callback=self.load_budget_data)
    
    def auto_fill_months(self):
        """Auto-fill all 24 months with template"""
        if messagebox.askyesno("Auto-fill", "Apply Conservative template to all 24 months?"):
            success, message = self.budget_manager.auto_fill_all_months("Conservative")
            if success:
                messagebox.showinfo("Success", message)
                self.load_budget_data()
            else:
                messagebox.showerror("Error", message)
    
    def update_total(self):
        """Update total budget display"""
        try:
            total = 0
            for group_vars in self.budget_vars.values():
                for var in group_vars.values():
                    try:
                        total += float(var.get() or 0)
                    except ValueError:
                        pass
            
            self.total_label.config(text=f"Total: ₹{total:,.2f}")
            
        except Exception as e:
            logging.error(f"Error updating total: {e}")
    
    def refresh(self):
        """Refresh budget display"""
        self.load_budget_data()
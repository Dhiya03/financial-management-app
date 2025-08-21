"""
Enhanced Budget Planning Tab - Complete Implementation
Implements User Story 3: 2-Year Budget Management with Lifecycle Support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

from config import DEFAULT_CATEGORIES, PLANNING_MONTHS, BUDGET_TEMPLATES, CURRENCY_SYMBOL
from managers.budget_manager import BudgetManager
from managers.transaction_manager import TransactionManager
from utils.formatters import format_currency, format_percentage

class BudgetTab:
    """Enhanced budget planning tab with 2-year planning and lifecycle management"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.current_month = "Aug-25"
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        self.budget_vars = {}
        
        # Track lifecycle events
        self.lifecycle_events = self.load_lifecycle_events()
        
        # Track budget changes for comparison
        self.original_budgets = {}
        
        # Alert threshold
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
        self.alert_threshold = self.app_data.settings.get('alert_threshold', 10)
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup enhanced budget tab UI"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Top control panel
        self.setup_control_panel(main_container)
        
        # Budget overview card
        self.setup_overview_card(main_container)
        
        # Create notebook for tabbed view
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Monthly budget tab
        monthly_frame = ttk.Frame(self.notebook)
        self.notebook.add(monthly_frame, text="Monthly Budget")
        self.setup_monthly_budget(monthly_frame)
        
        # Lifecycle events tab
        lifecycle_frame = ttk.Frame(self.notebook)
        self.notebook.add(lifecycle_frame, text="Lifecycle Events")
        self.setup_lifecycle_tab(lifecycle_frame)
        
        # Budget comparison tab
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Budget Analysis")
        self.setup_comparison_tab(comparison_frame)
        
        # Alert configuration tab
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alert Settings")
        self.setup_alerts_tab(alerts_frame)
    
    def setup_control_panel(self, parent):
        """Setup top control panel with month navigation and actions"""
        control_panel = ttk.LabelFrame(parent, text="Budget Controls", padding=10)
        control_panel.pack(fill='x', pady=(0, 10))
        
        # Month navigation
        nav_frame = ttk.Frame(control_panel)
        nav_frame.pack(side='left')
        
        ttk.Button(nav_frame, text="◀", command=self.previous_month).pack(side='left')
        
        ttk.Label(nav_frame, text="Month:").pack(side='left', padx=(10, 5))
        self.month_var = tk.StringVar(value=self.current_month)
        month_combo = ttk.Combobox(nav_frame, textvariable=self.month_var,
                                  values=PLANNING_MONTHS, state='readonly', width=10)
        month_combo.pack(side='left')
        month_combo.bind('<<ComboboxSelected>>', self.on_month_changed)
        
        ttk.Button(nav_frame, text="▶", command=self.next_month).pack(side='left', padx=(0, 20))
        
        # Quick navigation
        ttk.Button(nav_frame, text="Go to Current Month", 
                  command=self.go_to_current_month).pack(side='left')
        
        # Action buttons
        action_frame = ttk.Frame(control_panel)
        action_frame.pack(side='right')
        
        ttk.Button(action_frame, text="💾 Save Budget", 
                  command=self.save_budget).pack(side='left', padx=2)
        ttk.Button(action_frame, text="📋 Copy from Previous", 
                  command=self.copy_from_previous).pack(side='left', padx=2)
        ttk.Button(action_frame, text="📑 Apply Template", 
                  command=self.apply_template).pack(side='left', padx=2)
        ttk.Button(action_frame, text="🔄 Auto-fill 24 Months", 
                  command=self.auto_fill_months).pack(side='left', padx=2)
        ttk.Button(action_frame, text="📊 Analyze Budget", 
                  command=self.analyze_budget).pack(side='left', padx=2)
    
    def setup_overview_card(self, parent):
        """Setup budget overview card"""
        overview_frame = ttk.LabelFrame(parent, text="Budget Overview", padding=10)
        overview_frame.pack(fill='x', pady=(0, 10))
        
        # Create grid layout
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.columnconfigure(1, weight=1)
        overview_frame.columnconfigure(2, weight=1)
        overview_frame.columnconfigure(3, weight=1)
        
        # Total budget
        total_frame = ttk.Frame(overview_frame)
        total_frame.grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Label(total_frame, text="Total Budget:", font=('Arial', 9)).pack(anchor='w')
        self.total_budget_label = ttk.Label(total_frame, text=f"{CURRENCY_SYMBOL}0", 
                                          font=('Arial', 12, 'bold'))
        self.total_budget_label.pack(anchor='w')
        
        # Actual spending
        actual_frame = ttk.Frame(overview_frame)
        actual_frame.grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Label(actual_frame, text="Actual Spent:", font=('Arial', 9)).pack(anchor='w')
        self.actual_spent_label = ttk.Label(actual_frame, text=f"{CURRENCY_SYMBOL}0", 
                                          font=('Arial', 12, 'bold'))
        self.actual_spent_label.pack(anchor='w')
        
        # Variance
        variance_frame = ttk.Frame(overview_frame)
        variance_frame.grid(row=0, column=2, padx=5, sticky='ew')
        ttk.Label(variance_frame, text="Variance:", font=('Arial', 9)).pack(anchor='w')
        self.variance_label = ttk.Label(variance_frame, text=f"{CURRENCY_SYMBOL}0", 
                                      font=('Arial', 12, 'bold'))
        self.variance_label.pack(anchor='w')
        
        # Adherence
        adherence_frame = ttk.Frame(overview_frame)
        adherence_frame.grid(row=0, column=3, padx=5, sticky='ew')
        ttk.Label(adherence_frame, text="Adherence:", font=('Arial', 9)).pack(anchor='w')
        self.adherence_label = ttk.Label(adherence_frame, text="0%", 
                                       font=('Arial', 12, 'bold'))
        self.adherence_label.pack(anchor='w')
        
        # Lifecycle events indicator
        events_frame = ttk.Frame(overview_frame)
        events_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky='ew')
        self.lifecycle_label = ttk.Label(events_frame, text="", font=('Arial', 10))
        self.lifecycle_label.pack(anchor='w')
    
    def setup_monthly_budget(self, parent):
        """Setup monthly budget entry section"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Budget entry sections
        self.category_frames = {}
        self.budget_vars = {}
        
        for group_name, categories in DEFAULT_CATEGORIES.items():
            if group_name == "Custom":
                continue
            
            # Create collapsible group frame
            group_frame = ttk.LabelFrame(scrollable_frame, text=f"{group_name}", padding=15)
            group_frame.pack(fill='x', padx=10, pady=5)
            
            self.category_frames[group_name] = group_frame
            self.budget_vars[group_name] = {}
            
            # Group total label
            group_total_label = ttk.Label(group_frame, text="", font=('Arial', 10, 'bold'))
            group_total_label.pack(anchor='e', pady=(0, 10))
            
            # Create budget entries with comparison
            for category in categories:
                cat_frame = ttk.Frame(group_frame)
                cat_frame.pack(fill='x', pady=2)
                
                # Category name
                ttk.Label(cat_frame, text=category, width=25).pack(side='left')
                
                # Previous month amount (for reference)
                prev_label = ttk.Label(cat_frame, text="", width=12, foreground='gray')
                prev_label.pack(side='left', padx=(10, 5))
                
                # Budget entry
                var = tk.StringVar(value="0")
                self.budget_vars[group_name][category] = {
                    'var': var,
                    'prev_label': prev_label,
                    'entry': None
                }
                
                entry = ttk.Entry(cat_frame, textvariable=var, width=12)
                entry.pack(side='left')
                self.budget_vars[group_name][category]['entry'] = entry
                
                # Currency symbol
                ttk.Label(cat_frame, text=CURRENCY_SYMBOL).pack(side='left', padx=(2, 10))
                
                # Actual vs Budget indicator
                status_label = ttk.Label(cat_frame, text="", width=15)
                status_label.pack(side='left')
                self.budget_vars[group_name][category]['status_label'] = status_label
                
                # Bind for real-time validation and total update
                if sys.version_info >= (3, 13):
                    var.trace_add('write', lambda *args: self.update_totals())
                else:
                    var.trace('w', lambda *args: self.update_totals())
            
            # Store group total label
            self.budget_vars[group_name]['total_label'] = group_total_label
        
        # Monthly total section
        self.total_frame = ttk.LabelFrame(scrollable_frame, text="Monthly Total", padding=15)
        self.total_frame.pack(fill='x', padx=10, pady=10)
        
        self.monthly_total_label = ttk.Label(self.total_frame, 
                                            text=f"Total: {CURRENCY_SYMBOL}0", 
                                            font=('Arial', 14, 'bold'))
        self.monthly_total_label.pack()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_lifecycle_tab(self, parent):
        """Setup lifecycle events management tab"""
        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Configure financial lifecycle events (loan completions, new investments, etc.)",
                               font=('Arial', 10))
        instructions.pack(anchor='w', pady=(0, 10))
        
        # Add event button
        ttk.Button(main_frame, text="➕ Add Lifecycle Event", 
                  command=self.add_lifecycle_event).pack(anchor='w', pady=(0, 10))
        
        # Events list
        events_frame = ttk.LabelFrame(main_frame, text="Configured Events", padding=10)
        events_frame.pack(fill='both', expand=True)
        
        # Create treeview for events
        columns = ('Event', 'Category', 'Type', 'Month', 'Amount Change')
        self.events_tree = ttk.Treeview(events_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(events_frame, orient='vertical', command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load existing events
        self.refresh_lifecycle_events()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Edit Event", 
                  command=self.edit_lifecycle_event).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Delete Event", 
                  command=self.delete_lifecycle_event).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Apply Events", 
                  command=self.apply_lifecycle_events).pack(side='left', padx=2)
    
    def setup_comparison_tab(self, parent):
        """Setup budget comparison and analysis tab"""
        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Comparison controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(control_frame, text="Compare:").pack(side='left')
        
        self.compare_month1_var = tk.StringVar(value=PLANNING_MONTHS[0])
        month1_combo = ttk.Combobox(control_frame, textvariable=self.compare_month1_var,
                                   values=PLANNING_MONTHS, width=10, state='readonly')
        month1_combo.pack(side='left', padx=(5, 10))
        
        ttk.Label(control_frame, text="with").pack(side='left')
        
        self.compare_month2_var = tk.StringVar(value=PLANNING_MONTHS[1])
        month2_combo = ttk.Combobox(control_frame, textvariable=self.compare_month2_var,
                                   values=PLANNING_MONTHS, width=10, state='readonly')
        month2_combo.pack(side='left', padx=(10, 10))
        
        ttk.Button(control_frame, text="Compare", 
                  command=self.compare_budgets).pack(side='left', padx=10)
        
        ttk.Button(control_frame, text="Analyze All Months", 
                  command=self.analyze_all_months).pack(side='left')
        
        # Comparison results
        self.comparison_frame = ttk.LabelFrame(main_frame, text="Comparison Results", padding=10)
        self.comparison_frame.pack(fill='both', expand=True)
        
        # Create text widget for results
        self.comparison_text = tk.Text(self.comparison_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(self.comparison_frame, command=self.comparison_text.yview)
        self.comparison_text.configure(yscrollcommand=scrollbar.set)
        
        self.comparison_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_alerts_tab(self, parent):
        """Setup alert configuration tab"""
        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Global alert threshold
        global_frame = ttk.LabelFrame(main_frame, text="Global Alert Settings", padding=15)
        global_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(global_frame, text="Default Alert Threshold (%):").pack(side='left')
        
        self.global_threshold_var = tk.StringVar(value=str(self.alert_threshold))
        threshold_spinbox = ttk.Spinbox(global_frame, from_=1, to=100, 
                                       textvariable=self.global_threshold_var, width=10)
        threshold_spinbox.pack(side='left', padx=(10, 20))
        
        ttk.Button(global_frame, text="Apply", 
                  command=self.save_global_threshold).pack(side='left')
        
        # Category-specific thresholds
        category_frame = ttk.LabelFrame(main_frame, text="Category-Specific Thresholds", padding=15)
        category_frame.pack(fill='both', expand=True)
        
        # Create scrollable frame for categories
        canvas = tk.Canvas(category_frame, height=300)
        scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add category threshold controls
        self.category_threshold_vars = {}
        
        for group_name, categories in DEFAULT_CATEGORIES.items():
            if group_name == "Custom":
                continue
            
            group_label = ttk.Label(scrollable_frame, text=group_name, 
                                   font=('Arial', 10, 'bold'))
            group_label.pack(anchor='w', pady=(10, 5))
            
            for category in categories:
                cat_frame = ttk.Frame(scrollable_frame)
                cat_frame.pack(fill='x', pady=2)
                
                ttk.Label(cat_frame, text=category, width=30).pack(side='left')
                
                var = tk.StringVar(value=str(self.alert_threshold))
                self.category_threshold_vars[category] = var
                
                spinbox = ttk.Spinbox(cat_frame, from_=1, to=100, 
                                     textvariable=var, width=10)
                spinbox.pack(side='left', padx=(10, 5))
                
                ttk.Label(cat_frame, text="%").pack(side='left')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Save button
        ttk.Button(main_frame, text="Save All Thresholds", 
                  command=self.save_all_thresholds).pack(pady=10)
    
    # Navigation methods
    def on_month_changed(self, event=None):
        """Handle month selection change"""
        self.current_month = self.month_var.get()
        self.load_budget_data()
        self.check_lifecycle_events()
    
    def previous_month(self):
        """Navigate to previous month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx > 0:
                self.current_month = PLANNING_MONTHS[current_idx - 1]
                self.month_var.set(self.current_month)
                self.load_budget_data()
        except ValueError:
            pass
    
    def next_month(self):
        """Navigate to next month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx < len(PLANNING_MONTHS) - 1:
                self.current_month = PLANNING_MONTHS[current_idx + 1]
                self.month_var.set(self.current_month)
                self.load_budget_data()
        except ValueError:
            pass
    
    def go_to_current_month(self):
        """Navigate to current month"""
        now = datetime.now()
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_abbr = month_names[now.month - 1]
        year_short = str(now.year)[2:]
        current = f"{month_abbr}-{year_short}"
        
        if current in PLANNING_MONTHS:
            self.current_month = current
            self.month_var.set(current)
            self.load_budget_data()
    
    # Data management methods
    def load_budget_data(self):
        """Load budget data for selected month"""
        try:
            budgets = self.budget_manager.get_month_budget(self.current_month)
            self.original_budgets = budgets.copy()
            
            # Get previous month budgets for reference
            current_idx = PLANNING_MONTHS.index(self.current_month)
            prev_budgets = {}
            if current_idx > 0:
                prev_month = PLANNING_MONTHS[current_idx - 1]
                prev_budgets = self.budget_manager.get_month_budget(prev_month)
            
            # Get actual spending for comparison
            spending = self.transaction_manager.calculate_spending_by_category(self.current_month)
            
            # Update budget entries
            for group_name, group_vars in self.budget_vars.items():
                for category, var_dict in group_vars.items():
                    if category == 'total_label':
                        continue
                    
                    # Set budget amount
                    amount = budgets.get(category, 0)
                    var_dict['var'].set(str(amount))
                    
                    # Show previous month for reference
                    prev_amount = prev_budgets.get(category, 0)
                    if prev_amount > 0:
                        var_dict['prev_label'].config(text=f"(Prev: {format_currency(prev_amount)})")
                    else:
                        var_dict['prev_label'].config(text="")
                    
                    # Show actual vs budget
                    actual = spending.get(category, 0)
                    if amount > 0:
                        variance = actual - amount
                        percent = (actual / amount) * 100
                        
                        if percent < 80:
                            color = 'green'
                            status = "✓"
                        elif percent < 100:
                            color = 'orange'
                            status = "!"
                        else:
                            color = 'red'
                            status = "✗"
                        
                        var_dict['status_label'].config(
                            text=f"{status} {percent:.0f}% ({format_currency(variance)})",
                            foreground=color
                        )
                    else:
                        var_dict['status_label'].config(text="")
            
            self.update_totals()
            self.update_overview()
            
        except Exception as e:
            logging.error(f"Error loading budget data: {e}")
    
    def save_budget(self):
        """Save budget for current month"""
        try:
            errors = []
            changes = []
            
            for group_name, group_vars in self.budget_vars.items():
                for category, var_dict in group_vars.items():
                    if category == 'total_label':
                        continue
                    
                    try:
                        amount = float(var_dict['var'].get() or 0)
                        original = self.original_budgets.get(category, 0)
                        
                        if amount != original:
                            changes.append(f"{category}: {format_currency(original)} → {format_currency(amount)}")
                        
                        success, message = self.budget_manager.set_budget(
                            self.current_month, category, amount
                        )
                        if not success:
                            errors.append(f"{category}: {message}")
                    except ValueError:
                        errors.append(f"{category}: Invalid amount")
            
            if errors:
                messagebox.showerror("Validation Errors", "\n".join(errors[:10]))
            else:
                if changes:
                    details = "\n".join(changes[:10])
                    if len(changes) > 10:
                        details += f"\n... and {len(changes) - 10} more changes"
                    
                    messagebox.showinfo("Budget Saved", 
                                      f"Budget saved for {self.current_month}\n\nChanges:\n{details}")
                else:
                    messagebox.showinfo("Budget Saved", f"Budget saved for {self.current_month}")
                
                self.load_budget_data()
                
        except Exception as e:
            logging.error(f"Error saving budget: {e}")
            messagebox.showerror("Error", f"Failed to save budget: {str(e)}")
    
    def update_totals(self):
        """Update all totals displays"""
        try:
            monthly_total = 0
            
            for group_name, group_vars in self.budget_vars.items():
                group_total = 0
                
                for category, var_dict in group_vars.items():
                    if category == 'total_label':
                        continue
                    
                    try:
                        amount = float(var_dict['var'].get() or 0)
                        group_total += amount
                        monthly_total += amount
                        
                        # Highlight if changed from original
                        original = self.original_budgets.get(category, 0)
                        if amount != original:
                            var_dict['entry'].configure(style='Modified.TEntry')
                        else:
                            var_dict['entry'].configure(style='TEntry')
                            
                    except ValueError:
                        pass
                
                # Update group total
                if 'total_label' in group_vars:
                    group_vars['total_label'].config(text=f"Group Total: {format_currency(group_total)}")
            
            # Update monthly total
            self.monthly_total_label.config(text=f"Total: {format_currency(monthly_total)}")
            
        except Exception as e:
            logging.error(f"Error updating totals: {e}")
    
    def update_overview(self):
        """Update budget overview card"""
        try:
            # Get budget and spending data
            total_budget = self.budget_manager.get_total_budget(self.current_month)
            spending = self.transaction_manager.calculate_spending_by_category(self.current_month)
            total_spent = sum(spending.values())
            
            # Calculate variance and adherence
            variance = total_budget - total_spent
            adherence = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            # Update labels
            self.total_budget_label.config(text=format_currency(total_budget))
            self.actual_spent_label.config(text=format_currency(total_spent))
            
            # Color code variance
            if variance < 0:
                self.variance_label.config(text=format_currency(variance), foreground='red')
            else:
                self.variance_label.config(text=format_currency(variance), foreground='green')
            
            # Color code adherence
            if adherence > 100:
                self.adherence_label.config(text=f"{adherence:.1f}%", foreground='red')
            elif adherence > 90:
                self.adherence_label.config(text=f"{adherence:.1f}%", foreground='orange')
            else:
                self.adherence_label.config(text=f"{adherence:.1f}%", foreground='green')
            
        except Exception as e:
            logging.error(f"Error updating overview: {e}")
    
    # Template and automation methods
    def copy_from_previous(self):
        """Copy budget from previous month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx > 0:
                previous_month = PLANNING_MONTHS[current_idx - 1]
                
                if messagebox.askyesno("Copy Budget", 
                                      f"Copy budget from {previous_month} to {self.current_month}?"):
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
        dialog = BudgetTemplateDialog(self.frame, self.current_month, 
                                    callback=self.load_budget_data)
    
    def auto_fill_months(self):
        """Auto-fill all 24 months with template"""
        dialog = AutoFillDialog(self.frame, callback=self.refresh)
    
    # Lifecycle event methods
    def load_lifecycle_events(self) -> List[Dict]:
        """Load lifecycle events from settings"""
        return self.app_data.settings.get('lifecycle_events', [])
    
    def save_lifecycle_events(self):
        """Save lifecycle events to settings"""
        self.app_data.settings['lifecycle_events'] = self.lifecycle_events
        from managers.data_manager import data_manager
        data_manager.save()
    
    def refresh_lifecycle_events(self):
        """Refresh lifecycle events display"""
        # Clear tree
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Add events
        for event in self.lifecycle_events:
            self.events_tree.insert('', 'end', values=(
                event.get('name', ''),
                event.get('category', ''),
                event.get('type', ''),
                event.get('month', ''),
                format_currency(event.get('amount', 0))
            ))
    
    def check_lifecycle_events(self):
        """Check for lifecycle events in current month"""
        events_in_month = [e for e in self.lifecycle_events 
                          if e.get('month') == self.current_month]
        
        if events_in_month:
            event_names = [e.get('name', 'Event') for e in events_in_month]
            self.lifecycle_label.config(
                text=f"⚠️ Lifecycle events this month: {', '.join(event_names)}",
                foreground='orange'
            )
        else:
            self.lifecycle_label.config(text="")
    
    def add_lifecycle_event(self):
        """Add new lifecycle event"""
        LifecycleEventDialog(self.frame, callback=self.on_lifecycle_event_added)
    
    def on_lifecycle_event_added(self, event):
        """Handle new lifecycle event"""
        self.lifecycle_events.append(event)
        self.save_lifecycle_events()
        self.refresh_lifecycle_events()
        self.check_lifecycle_events()
    
    def edit_lifecycle_event(self):
        """Edit selected lifecycle event"""
        selection = self.events_tree.selection()
        if selection:
            # Implementation for editing
            messagebox.showinfo("Edit", "Edit lifecycle event functionality coming soon")
    
    def delete_lifecycle_event(self):
        """Delete selected lifecycle event"""
        selection = self.events_tree.selection()
        if selection and messagebox.askyesno("Delete", "Delete selected event?"):
            # Get index and remove
            item = selection[0]
            index = self.events_tree.index(item)
            if 0 <= index < len(self.lifecycle_events):
                del self.lifecycle_events[index]
                self.save_lifecycle_events()
                self.refresh_lifecycle_events()
    
    def apply_lifecycle_events(self):
        """Apply lifecycle events to budgets"""
        if messagebox.askyesno("Apply Events", 
                              "Apply all lifecycle events to affected months?"):
            applied = 0
            
            for event in self.lifecycle_events:
                month = event.get('month')
                category = event.get('category')
                event_type = event.get('type')
                amount = event.get('amount', 0)
                
                if event_type == 'end':
                    # End of payment - set to 0
                    self.budget_manager.set_budget(month, category, 0)
                    applied += 1
                elif event_type == 'start':
                    # Start of payment
                    self.budget_manager.set_budget(month, category, amount)
                    applied += 1
                elif event_type == 'change':
                    # Change in amount
                    self.budget_manager.set_budget(month, category, amount)
                    applied += 1
            
            if applied > 0:
                messagebox.showinfo("Success", f"Applied {applied} lifecycle events")
                self.load_budget_data()
    
    # Comparison and analysis methods
    def compare_budgets(self):
        """Compare two months' budgets"""
        month1 = self.compare_month1_var.get()
        month2 = self.compare_month2_var.get()
        
        if month1 == month2:
            messagebox.showwarning("Same Month", "Please select different months to compare")
            return
        
        budget1 = self.budget_manager.get_month_budget(month1)
        budget2 = self.budget_manager.get_month_budget(month2)
        
        # Clear text widget
        self.comparison_text.delete(1.0, tk.END)
        
        # Add comparison header
        self.comparison_text.insert(tk.END, f"Budget Comparison: {month1} vs {month2}\n", 'header')
        self.comparison_text.insert(tk.END, "="*60 + "\n\n")
        
        # Compare totals
        total1 = sum(budget1.values())
        total2 = sum(budget2.values())
        diff = total2 - total1
        percent = (diff / total1 * 100) if total1 > 0 else 0
        
        self.comparison_text.insert(tk.END, f"Total Budget:\n")
        self.comparison_text.insert(tk.END, f"  {month1}: {format_currency(total1)}\n")
        self.comparison_text.insert(tk.END, f"  {month2}: {format_currency(total2)}\n")
        self.comparison_text.insert(tk.END, f"  Difference: {format_currency(diff)} ({percent:+.1f}%)\n\n")
        
        # Compare by category
        all_categories = set(budget1.keys()) | set(budget2.keys())
        
        increases = []
        decreases = []
        new_items = []
        removed_items = []
        
        for category in sorted(all_categories):
            amt1 = budget1.get(category, 0)
            amt2 = budget2.get(category, 0)
            
            if amt1 == 0 and amt2 > 0:
                new_items.append(f"  + {category}: {format_currency(amt2)}")
            elif amt1 > 0 and amt2 == 0:
                removed_items.append(f"  - {category}: {format_currency(amt1)}")
            elif amt2 > amt1:
                increases.append(f"  ↑ {category}: {format_currency(amt1)} → {format_currency(amt2)} (+{format_currency(amt2-amt1)})")
            elif amt2 < amt1:
                decreases.append(f"  ↓ {category}: {format_currency(amt1)} → {format_currency(amt2)} ({format_currency(amt2-amt1)})")
        
        if increases:
            self.comparison_text.insert(tk.END, "Increased Budgets:\n")
            for item in increases:
                self.comparison_text.insert(tk.END, item + "\n")
            self.comparison_text.insert(tk.END, "\n")
        
        if decreases:
            self.comparison_text.insert(tk.END, "Decreased Budgets:\n")
            for item in decreases:
                self.comparison_text.insert(tk.END, item + "\n")
            self.comparison_text.insert(tk.END, "\n")
        
        if new_items:
            self.comparison_text.insert(tk.END, "New Categories:\n")
            for item in new_items:
                self.comparison_text.insert(tk.END, item + "\n")
            self.comparison_text.insert(tk.END, "\n")
        
        if removed_items:
            self.comparison_text.insert(tk.END, "Removed Categories:\n")
            for item in removed_items:
                self.comparison_text.insert(tk.END, item + "\n")
    
    def analyze_budget(self):
        """Analyze current month's budget"""
        BudgetAnalysisDialog(self.frame, self.current_month)
    
    def analyze_all_months(self):
        """Analyze all 24 months"""
        messagebox.showinfo("Analysis", "Full 24-month analysis coming soon")
    
    # Alert configuration methods
    def save_global_threshold(self):
        """Save global alert threshold"""
        try:
            threshold = int(self.global_threshold_var.get())
            if 1 <= threshold <= 100:
                self.alert_threshold = threshold
                self.app_data.settings['alert_threshold'] = threshold
                
                from managers.data_manager import data_manager
                data_manager.save()
                
                messagebox.showinfo("Success", f"Global threshold set to {threshold}%")
            else:
                messagebox.showerror("Error", "Threshold must be between 1 and 100")
        except ValueError:
            messagebox.showerror("Error", "Invalid threshold value")
    
    def save_all_thresholds(self):
        """Save all category-specific thresholds"""
        try:
            thresholds = {}
            for category, var in self.category_threshold_vars.items():
                thresholds[category] = int(var.get())
            
            self.app_data.settings['category_thresholds'] = thresholds
            
            from managers.data_manager import data_manager
            data_manager.save()
            
            messagebox.showinfo("Success", "All thresholds saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save thresholds: {str(e)}")
    
    def refresh(self):
        """Refresh budget display"""
        self.load_budget_data()
        self.check_lifecycle_events()


class BudgetTemplateDialog:
    """Dialog for applying budget templates"""
    
    def __init__(self, parent, current_month, callback=None):
        self.parent = parent
        self.current_month = current_month
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Apply Budget Template")
        self.dialog.geometry("400x350")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Select a budget template:",
                 font=('Arial', 12)).pack(pady=(0, 20))
        
        # Template selection
        self.template_var = tk.StringVar()
        
        for template_name in BUDGET_TEMPLATES.keys():
            rb = ttk.Radiobutton(main_frame, text=template_name, 
                               variable=self.template_var, value=template_name)
            rb.pack(anchor='w', pady=5)
        
        self.template_var.set("Conservative")
        
        # Options
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        self.apply_to_all_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Apply to all empty months",
                       variable=self.apply_to_all_var).pack(anchor='w')
        
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Overwrite existing budgets",
                       variable=self.overwrite_var).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', pady=20)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def apply_template(self):
        """Apply selected template"""
        template_name = self.template_var.get()
        
        if template_name in BUDGET_TEMPLATES:
            from managers.budget_manager import BudgetManager
            manager = BudgetManager()
            
            if self.apply_to_all_var.get():
                # Apply to multiple months
                months = []
                for month in PLANNING_MONTHS:
                    if self.overwrite_var.get() or not manager.get_month_budget(month):
                        months.append(month)
                
                if months:
                    success, message = manager.apply_template(template_name, months)
                    messagebox.showinfo("Applied", f"Template applied to {len(months)} months")
            else:
                # Apply to current month only
                success, message = manager.apply_template(template_name, [self.current_month])
                messagebox.showinfo("Applied", message)
            
            if self.callback:
                self.callback()
            
            self.dialog.destroy()


class AutoFillDialog:
    """Dialog for auto-filling all 24 months"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Auto-fill 24 Months")
        self.dialog.geometry("500x400")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Auto-fill Budget Configuration",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Base template
        template_frame = ttk.LabelFrame(main_frame, text="Base Template", padding=10)
        template_frame.pack(fill='x', pady=(0, 10))
        
        self.template_var = tk.StringVar(value="Conservative")
        for template in BUDGET_TEMPLATES.keys():
            ttk.Radiobutton(template_frame, text=template,
                          variable=self.template_var, value=template).pack(anchor='w')
        
        # Adjustments
        adjust_frame = ttk.LabelFrame(main_frame, text="Monthly Adjustments", padding=10)
        adjust_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(adjust_frame, text="Inflation adjustment (% per year):").pack(anchor='w')
        self.inflation_var = tk.StringVar(value="5")
        ttk.Spinbox(adjust_frame, from_=0, to=20, textvariable=self.inflation_var, width=10).pack(anchor='w')
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Overwrite existing budgets",
                       variable=self.overwrite_var).pack(anchor='w')
        
        self.apply_lifecycle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Apply lifecycle events",
                       variable=self.apply_lifecycle_var).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', pady=20)
        
        ttk.Button(button_frame, text="Auto-fill", command=self.auto_fill).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def auto_fill(self):
        """Perform auto-fill"""
        template = self.template_var.get()
        inflation = float(self.inflation_var.get()) / 100
        
        from managers.budget_manager import BudgetManager
        manager = BudgetManager()
        
        # Apply template with adjustments
        success, message = manager.auto_fill_all_months(template)
        
        if success:
            messagebox.showinfo("Success", "All 24 months filled with budget template")
            if self.callback:
                self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", message)


class LifecycleEventDialog:
    """Dialog for adding lifecycle events"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Lifecycle Event")
        self.dialog.geometry("400x350")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Event name
        ttk.Label(main_frame, text="Event Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # Event type
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var,
                                 values=["start", "end", "change"], width=27)
        type_combo.grid(row=1, column=1, pady=5)
        type_combo.set("end")
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=2, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        
        from managers.category_manager import CategoryManager
        categories = CategoryManager().get_flat_category_list()
        cat_combo = ttk.Combobox(main_frame, textvariable=self.category_var,
                                values=categories, width=27)
        cat_combo.grid(row=2, column=1, pady=5)
        
        # Month
        ttk.Label(main_frame, text="Month:").grid(row=3, column=0, sticky='w', pady=5)
        self.month_var = tk.StringVar()
        month_combo = ttk.Combobox(main_frame, textvariable=self.month_var,
                                  values=PLANNING_MONTHS, width=27)
        month_combo.grid(row=3, column=1, pady=5)
        
        # Amount
        ttk.Label(main_frame, text="Amount:").grid(row=4, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.amount_var, width=30).grid(row=4, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.add_event).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def add_event(self):
        """Add the lifecycle event"""
        event = {
            'name': self.name_var.get(),
            'type': self.type_var.get(),
            'category': self.category_var.get(),
            'month': self.month_var.get(),
            'amount': float(self.amount_var.get() or 0)
        }
        
        if event['name'] and event['category'] and event['month']:
            if self.callback:
                self.callback(event)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please fill all required fields")


class BudgetAnalysisDialog:
    """Dialog for budget analysis"""
    
    def __init__(self, parent, month):
        self.parent = parent
        self.month = month
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Budget Analysis - {month}")
        self.dialog.geometry("600x500")
        
        self.setup_ui()
        self.analyze()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Budget Analysis for {self.month}",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Analysis text
        self.text = tk.Text(main_frame, height=20, width=70)
        scrollbar = ttk.Scrollbar(main_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        self.text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=10)
    
    def analyze(self):
        """Perform budget analysis"""
        from managers.budget_manager import BudgetManager
        from managers.transaction_manager import TransactionManager
        
        budget_mgr = BudgetManager()
        trans_mgr = TransactionManager()
        
        budgets = budget_mgr.get_month_budget(self.month)
        spending = trans_mgr.calculate_spending_by_category(self.month)
        
        total_budget = sum(budgets.values())
        total_spent = sum(spending.values())
        
        self.text.insert(tk.END, f"BUDGET ANALYSIS - {self.month}\n")
        self.text.insert(tk.END, "="*50 + "\n\n")
        
        self.text.insert(tk.END, f"Total Budget: {format_currency(total_budget)}\n")
        self.text.insert(tk.END, f"Total Spent: {format_currency(total_spent)}\n")
        self.text.insert(tk.END, f"Variance: {format_currency(total_budget - total_spent)}\n")
        self.text.insert(tk.END, f"Utilization: {(total_spent/total_budget*100) if total_budget > 0 else 0:.1f}%\n\n")
        
        # Category analysis
        self.text.insert(tk.END, "CATEGORY ANALYSIS\n")
        self.text.insert(tk.END, "-"*50 + "\n\n")
        
        over_budget = []
        under_utilized = []
        on_track = []
        
        for category in sorted(budgets.keys()):
            budget = budgets[category]
            spent = spending.get(category, 0)
            
            if budget > 0:
                utilization = (spent / budget) * 100
                
                if utilization > 100:
                    over_budget.append((category, budget, spent, utilization))
                elif utilization < 50:
                    under_utilized.append((category, budget, spent, utilization))
                else:
                    on_track.append((category, budget, spent, utilization))
        
        if over_budget:
            self.text.insert(tk.END, "⚠️ OVER BUDGET:\n")
            for cat, budget, spent, util in over_budget:
                self.text.insert(tk.END, f"  • {cat}: {format_currency(spent)}/{format_currency(budget)} ({util:.0f}%)\n")
            self.text.insert(tk.END, "\n")
        
        if under_utilized:
            self.text.insert(tk.END, "💰 UNDER-UTILIZED:\n")
            for cat, budget, spent, util in under_utilized[:5]:  # Show top 5
                self.text.insert(tk.END, f"  • {cat}: {format_currency(spent)}/{format_currency(budget)} ({util:.0f}%)\n")
            self.text.insert(tk.END, "\n")
        
        if on_track:
            self.text.insert(tk.END, "✅ ON TRACK:\n")
            for cat, budget, spent, util in on_track[:5]:  # Show top 5
                self.text.insert(tk.END, f"  • {cat}: {format_currency(spent)}/{format_currency(budget)} ({util:.0f}%)\n")
        
        # Recommendations
        self.text.insert(tk.END, "\n" + "="*50 + "\n")
        self.text.insert(tk.END, "RECOMMENDATIONS\n")
        self.text.insert(tk.END, "-"*50 + "\n\n")
        
        if over_budget:
            self.text.insert(tk.END, "• Review and adjust budgets for over-spending categories\n")
        if under_utilized:
            self.text.insert(tk.END, "• Consider reallocating under-utilized budgets\n")
        if total_spent > total_budget:
            self.text.insert(tk.END, "• Overall spending exceeds budget - immediate attention needed\n")

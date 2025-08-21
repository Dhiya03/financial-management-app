"""
Dashboard tab for financial overview - Complete Implementation
Implements User Story 1: Financial Command Center
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple

from config import PLANNING_MONTHS, CURRENCY_SYMBOL
from managers.budget_manager import BudgetManager
from managers.transaction_manager import TransactionManager
from utils.formatters import format_currency, format_percentage, get_status_color

class DashboardTab:
    """Dashboard tab for financial overview"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.current_month = self.get_current_month()
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        
        # Get alert threshold from settings
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
        self.alert_threshold = self.app_data.settings.get('alert_threshold', 10)
        
        self.setup_ui()
        self.refresh()
    
    def get_current_month(self) -> str:
        """Get current month in format 'Aug-25'"""
        now = datetime.now()
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_abbr = month_names[now.month - 1]
        year_short = str(now.year)[2:]
        current = f"{month_abbr}-{year_short}"
        
        # Return current month if it's in planning period, otherwise return first month
        return current if current in PLANNING_MONTHS else PLANNING_MONTHS[0]
    
    def setup_ui(self):
        """Setup dashboard UI components"""
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Month selector and navigation
        self.setup_month_navigation(main_container)
        
        # Alert frame
        self.alert_frame = ttk.Frame(main_container)
        self.alert_frame.pack(fill='x', pady=(10, 20))
        
        # Summary cards container
        summary_container = ttk.Frame(main_container)
        summary_container.pack(fill='x', pady=(0, 20))
        
        # Configure grid for two columns
        summary_container.columnconfigure(0, weight=1)
        summary_container.columnconfigure(1, weight=1)
        
        # Left summary card - Monthly Financial Status
        self.setup_financial_status_card(summary_container)
        
        # Right quick actions card
        self.setup_quick_actions_card(summary_container)
        
        # Spending projection card
        self.setup_projection_card(main_container)
        
        # Category breakdown table
        self.setup_category_table(main_container)
    
    def setup_month_navigation(self, parent):
        """Setup month navigation controls"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Previous button
        self.prev_btn = ttk.Button(nav_frame, text="◀ Previous", 
                                  command=self.previous_month)
        self.prev_btn.pack(side='left')
        
        # Month label and selector
        ttk.Label(nav_frame, text="Month:", font=('Arial', 10, 'bold')).pack(side='left', padx=(20, 5))
        
        self.month_var = tk.StringVar(value=self.current_month)
        self.month_combo = ttk.Combobox(nav_frame, textvariable=self.month_var, 
                                       values=PLANNING_MONTHS, state='readonly', width=10)
        self.month_combo.pack(side='left')
        self.month_combo.bind('<<ComboboxSelected>>', self.on_month_changed)
        
        # Next button
        self.next_btn = ttk.Button(nav_frame, text="Next ▶", 
                                  command=self.next_month)
        self.next_btn.pack(side='left', padx=(5, 20))
        
        # Days remaining (only for current month)
        self.days_label = ttk.Label(nav_frame, text="", font=('Arial', 10))
        self.days_label.pack(side='left')
        
        # Update navigation buttons state
        self.update_navigation_buttons()
    
    def setup_financial_status_card(self, parent):
        """Setup monthly financial status card"""
        left_card = ttk.LabelFrame(parent, text="📊 Monthly Financial Status", padding=20)
        left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Create status indicator
        self.status_indicator = ttk.Label(left_card, text="●", font=('Arial', 20))
        self.status_indicator.pack(anchor='e', pady=(0, 10))
        
        # Financial metrics
        metrics_frame = ttk.Frame(left_card)
        metrics_frame.pack(fill='both', expand=True)
        
        # Total Budget
        budget_frame = ttk.Frame(metrics_frame)
        budget_frame.pack(fill='x', pady=5)
        ttk.Label(budget_frame, text="Total Budget:", width=20, anchor='w').pack(side='left')
        self.total_budget_label = ttk.Label(budget_frame, text=f"{CURRENCY_SYMBOL}0", 
                                           font=('Arial', 12, 'bold'))
        self.total_budget_label.pack(side='right')
        
        # Amount Spent
        spent_frame = ttk.Frame(metrics_frame)
        spent_frame.pack(fill='x', pady=5)
        ttk.Label(spent_frame, text="Amount Spent:", width=20, anchor='w').pack(side='left')
        self.spent_amount_label = ttk.Label(spent_frame, text=f"{CURRENCY_SYMBOL}0", 
                                           font=('Arial', 12, 'bold'))
        self.spent_amount_label.pack(side='right')
        
        # Remaining Budget
        remaining_frame = ttk.Frame(metrics_frame)
        remaining_frame.pack(fill='x', pady=5)
        ttk.Label(remaining_frame, text="Remaining:", width=20, anchor='w').pack(side='left')
        self.remaining_label = ttk.Label(remaining_frame, text=f"{CURRENCY_SYMBOL}0", 
                                       font=('Arial', 12, 'bold'))
        self.remaining_label.pack(side='right')
        
        # Percentage Used
        percentage_frame = ttk.Frame(metrics_frame)
        percentage_frame.pack(fill='x', pady=5)
        ttk.Label(percentage_frame, text="Spent:", width=20, anchor='w').pack(side='left')
        self.percentage_label = ttk.Label(percentage_frame, text="0%", 
                                         font=('Arial', 12, 'bold'))
        self.percentage_label.pack(side='right')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(metrics_frame, variable=self.progress_var, 
                                           maximum=100, length=250)
        self.progress_bar.pack(fill='x', pady=(10, 5))
    
    def setup_quick_actions_card(self, parent):
        """Setup quick actions card"""
        right_card = ttk.LabelFrame(parent, text="⚡ Quick Actions", padding=20)
        right_card.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        # Action buttons
        actions = [
            ("Add Transaction", self.add_transaction),
            ("Set Budget", self.set_budget),
            ("Import Data", self.import_data),
            ("View Analytics", self.view_analytics),
            ("Export Month", self.export_month)
        ]
        
        for text, command in actions:
            btn = ttk.Button(right_card, text=text, command=command)
            btn.pack(fill='x', pady=5)
    
    def setup_projection_card(self, parent):
        """Setup spending projection card"""
        projection_frame = ttk.LabelFrame(parent, text="📈 Spending Projections", padding=15)
        projection_frame.pack(fill='x', pady=(0, 20))
        
        # Projection metrics container
        metrics_container = ttk.Frame(projection_frame)
        metrics_container.pack(fill='x')
        
        # Daily spending rate
        daily_frame = ttk.Frame(metrics_container)
        daily_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(daily_frame, text="Daily Rate:", anchor='w').pack(side='left')
        self.daily_rate_label = ttk.Label(daily_frame, text=f"{CURRENCY_SYMBOL}0", 
                                         font=('Arial', 11, 'bold'))
        self.daily_rate_label.pack(side='left', padx=(10, 0))
        
        # Projected month-end
        projected_frame = ttk.Frame(metrics_container)
        projected_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
        ttk.Label(projected_frame, text="Projected Month-End:", anchor='w').pack(side='left')
        self.projected_label = ttk.Label(projected_frame, text=f"{CURRENCY_SYMBOL}0", 
                                        font=('Arial', 11, 'bold'))
        self.projected_label.pack(side='left', padx=(10, 0))
        
        # Projection status
        status_frame = ttk.Frame(metrics_container)
        status_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
        ttk.Label(status_frame, text="Status:", anchor='w').pack(side='left')
        self.projection_status_label = ttk.Label(status_frame, text="On Track", 
                                                font=('Arial', 11, 'bold'))
        self.projection_status_label.pack(side='left', padx=(10, 0))
    
    def setup_category_table(self, parent):
        """Setup category breakdown table"""
        table_frame = ttk.LabelFrame(parent, text="📋 Category Breakdown", padding=15)
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview with columns
        columns = ('Category', 'Planned', 'Spent', 'Remaining', 'Status', 'Performance')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {
            'Category': 200,
            'Planned': 100,
            'Spent': 100,
            'Remaining': 100,
            'Status': 100,
            'Performance': 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configure tags for row colors
        self.tree.tag_configure('green', foreground='green')
        self.tree.tag_configure('yellow', foreground='orange')
        self.tree.tag_configure('red', foreground='red')
    
    def on_month_changed(self, event=None):
        """Handle month selection change"""
        self.current_month = self.month_var.get()
        self.update_navigation_buttons()
        self.refresh()
    
    def previous_month(self):
        """Navigate to previous month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx > 0:
                self.current_month = PLANNING_MONTHS[current_idx - 1]
                self.month_var.set(self.current_month)
                self.refresh()
        except ValueError:
            pass
    
    def next_month(self):
        """Navigate to next month"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            if current_idx < len(PLANNING_MONTHS) - 1:
                self.current_month = PLANNING_MONTHS[current_idx + 1]
                self.month_var.set(self.current_month)
                self.refresh()
        except ValueError:
            pass
    
    def update_navigation_buttons(self):
        """Update state of navigation buttons"""
        try:
            current_idx = PLANNING_MONTHS.index(self.current_month)
            self.prev_btn['state'] = 'normal' if current_idx > 0 else 'disabled'
            self.next_btn['state'] = 'normal' if current_idx < len(PLANNING_MONTHS) - 1 else 'disabled'
        except ValueError:
            self.prev_btn['state'] = 'disabled'
            self.next_btn['state'] = 'disabled'
    
    def refresh(self):
        """Refresh dashboard data"""
        try:
            # Update summary
            self.update_summary()
            
            # Update category table
            self.update_category_table()
            
            # Update alerts
            self.update_alerts()
            
            # Update projections
            self.update_projections()
            
            # Update days remaining
            self.update_days_remaining()
            
        except Exception as e:
            logging.error(f"Error refreshing dashboard: {e}")
    
    def update_summary(self):
        """Update summary display"""
        try:
            # Get budget and spending data
            total_budget = self.budget_manager.get_total_budget(self.current_month)
            spending_by_category = self.transaction_manager.calculate_spending_by_category(self.current_month)
            total_spent = sum(spending_by_category.values())
            remaining = total_budget - total_spent
            
            # Calculate percentage
            percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
            
            # Update labels
            self.total_budget_label.config(text=format_currency(total_budget))
            self.spent_amount_label.config(text=format_currency(total_spent))
            self.remaining_label.config(text=format_currency(remaining))
            self.percentage_label.config(text=format_percentage(percentage))
            
            # Update progress bar
            self.progress_var.set(min(percentage, 100))
            
            # Update status indicator color
            self.update_status_indicator(percentage)
            
            # Color code remaining amount
            if remaining < 0:
                self.remaining_label.config(foreground='red')
            elif percentage > (100 - self.alert_threshold):
                self.remaining_label.config(foreground='orange')
            else:
                self.remaining_label.config(foreground='green')
                
        except Exception as e:
            logging.error(f"Error updating summary: {e}")
    
    def update_status_indicator(self, percentage):
        """Update status indicator based on spending percentage"""
        if percentage < 80:
            self.status_indicator.config(text="● On Track", foreground='green')
        elif percentage < 100:
            self.status_indicator.config(text="● Warning", foreground='orange')
        else:
            self.status_indicator.config(text="● Over Budget", foreground='red')
    
    def update_category_table(self):
        """Update category breakdown table"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get budget and spending data
            budgets = self.budget_manager.get_month_budget(self.current_month)
            spending = self.transaction_manager.calculate_spending_by_category(self.current_month)
            
            # Get all categories (union of budgeted and spent)
            all_categories = set(budgets.keys()) | set(spending.keys())
            
            # Add rows for each category
            for category in sorted(all_categories):
                planned = budgets.get(category, 0)
                spent = spending.get(category, 0)
                remaining = planned - spent
                
                # Calculate performance percentage
                if planned > 0:
                    performance = (spent / planned) * 100
                    performance_text = f"{performance:.0f}%"
                else:
                    performance = 100 if spent > 0 else 0
                    performance_text = "N/A" if planned == 0 else f"{performance:.0f}%"
                
                # Determine status
                if performance < 80:
                    status = "On Track"
                    tag = 'green'
                elif performance < 100:
                    status = "Warning"
                    tag = 'yellow'
                else:
                    status = "Over Budget"
                    tag = 'red'
                
                # Insert row
                self.tree.insert('', 'end', values=(
                    category,
                    format_currency(planned),
                    format_currency(spent),
                    format_currency(remaining),
                    status,
                    performance_text
                ), tags=(tag,))
                
        except Exception as e:
            logging.error(f"Error updating category table: {e}")
    
    def update_alerts(self):
        """Update alerts display"""
        try:
            # Clear existing alerts
            for widget in self.alert_frame.winfo_children():
                widget.destroy()
            
            # Get budget and spending data
            total_budget = self.budget_manager.get_total_budget(self.current_month)
            spending_by_category = self.transaction_manager.calculate_spending_by_category(self.current_month)
            total_spent = sum(spending_by_category.values())
            
            if total_budget == 0:
                alert = ttk.Label(self.alert_frame, 
                                text="⚠️ No budget set for this month", 
                                foreground='orange', font=('Arial', 10, 'bold'))
                alert.pack(anchor='w')
                return
            
            percentage = (total_spent / total_budget) * 100
            
            # Check for alerts based on threshold
            if percentage > 100:
                alert = ttk.Label(self.alert_frame, 
                                text=f"🚨 Budget exceeded by {format_currency(total_spent - total_budget)}", 
                                foreground='red', font=('Arial', 10, 'bold'))
                alert.pack(anchor='w')
            elif percentage > (100 - self.alert_threshold):
                remaining_percent = 100 - percentage
                alert = ttk.Label(self.alert_frame, 
                                text=f"⚠️ Only {remaining_percent:.1f}% of budget remaining", 
                                foreground='orange', font=('Arial', 10, 'bold'))
                alert.pack(anchor='w')
            
            # Check for over-budget categories
            budgets = self.budget_manager.get_month_budget(self.current_month)
            over_budget_categories = []
            
            for category, budget in budgets.items():
                if budget > 0:
                    spent = spending_by_category.get(category, 0)
                    if spent > budget:
                        over_budget_categories.append(category)
            
            if over_budget_categories:
                categories_text = ", ".join(over_budget_categories[:3])
                if len(over_budget_categories) > 3:
                    categories_text += f" and {len(over_budget_categories) - 3} more"
                
                alert = ttk.Label(self.alert_frame, 
                                text=f"📊 Categories over budget: {categories_text}", 
                                foreground='red', font=('Arial', 10))
                alert.pack(anchor='w')
                
        except Exception as e:
            logging.error(f"Error updating alerts: {e}")
    
    def update_projections(self):
        """Update spending projections"""
        try:
            # Get current date and month info
            now = datetime.now()
            
            # Parse current month
            month_parts = self.current_month.split('-')
            if len(month_parts) == 2:
                month_abbr = month_parts[0]
                year_short = month_parts[1]
                
                # Convert to full date
                month_names = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                
                if month_abbr in month_names:
                    month_num = month_names[month_abbr]
                    year = 2000 + int(year_short)
                    
                    # Calculate days in month
                    if month_num == 12:
                        days_in_month = 31
                    else:
                        next_month = datetime(year, month_num + 1, 1)
                        this_month = datetime(year, month_num, 1)
                        days_in_month = (next_month - this_month).days
                    
                    # Get spending data
                    spending_by_category = self.transaction_manager.calculate_spending_by_category(self.current_month)
                    total_spent = sum(spending_by_category.values())
                    
                    # Calculate daily rate (assume halfway through month if not current)
                    if now.month == month_num and now.year == year:
                        days_elapsed = now.day
                    else:
                        days_elapsed = days_in_month // 2  # Assume halfway for non-current months
                    
                    if days_elapsed > 0:
                        daily_rate = total_spent / days_elapsed
                        projected_total = daily_rate * days_in_month
                    else:
                        daily_rate = 0
                        projected_total = 0
                    
                    # Update projection labels
                    self.daily_rate_label.config(text=format_currency(daily_rate))
                    self.projected_label.config(text=format_currency(projected_total))
                    
                    # Determine projection status
                    total_budget = self.budget_manager.get_total_budget(self.current_month)
                    
                    if total_budget > 0:
                        projected_percentage = (projected_total / total_budget) * 100
                        
                        if projected_percentage < 90:
                            self.projection_status_label.config(text="On Track", foreground='green')
                        elif projected_percentage < 110:
                            self.projection_status_label.config(text="Caution", foreground='orange')
                        else:
                            over_amount = projected_total - total_budget
                            self.projection_status_label.config(
                                text=f"Over by {format_currency(over_amount)}", 
                                foreground='red'
                            )
                    else:
                        self.projection_status_label.config(text="No Budget", foreground='gray')
                        
        except Exception as e:
            logging.error(f"Error updating projections: {e}")
            self.daily_rate_label.config(text=f"{CURRENCY_SYMBOL}0")
            self.projected_label.config(text=f"{CURRENCY_SYMBOL}0")
            self.projection_status_label.config(text="N/A")
    
    def update_days_remaining(self):
        """Update days remaining in current month"""
        try:
            now = datetime.now()
            
            # Parse current month
            month_parts = self.current_month.split('-')
            if len(month_parts) == 2:
                month_abbr = month_parts[0]
                year_short = month_parts[1]
                
                month_names = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                
                if month_abbr in month_names:
                    month_num = month_names[month_abbr]
                    year = 2000 + int(year_short)
                    
                    # Check if this is the current month
                    if now.month == month_num and now.year == year:
                        # Calculate days remaining
                        if month_num == 12:
                            days_in_month = 31
                        else:
                            next_month = datetime(year, month_num + 1, 1)
                            this_month = datetime(year, month_num, 1)
                            days_in_month = (next_month - this_month).days
                        
                        days_remaining = days_in_month - now.day
                        self.days_label.config(text=f"📅 {days_remaining} days remaining")
                    else:
                        self.days_label.config(text="")
                        
        except Exception as e:
            logging.error(f"Error updating days remaining: {e}")
            self.days_label.config(text="")
    
    # Quick action methods
    def add_transaction(self):
        """Open add transaction dialog"""
        from gui.dialogs.transaction_dialog import TransactionDialog
        TransactionDialog(self.frame, callback=self.refresh)
    
    def set_budget(self):
        """Navigate to budget tab"""
        # Get the notebook widget and select budget tab
        notebook = self.parent.master
        notebook.select(2)  # Budget tab is typically at index 2
    
    def import_data(self):
        """Open import dialog"""
        from tkinter import messagebox
        messagebox.showinfo("Import", "Navigate to Transactions tab to import CSV files")
    
    def view_analytics(self):
        """Navigate to analytics tab"""
        notebook = self.parent.master
        notebook.select(3)  # Analytics tab
    
    def export_month(self):
        """Export current month data"""
        from tkinter import messagebox, filedialog
        import json
        
        # Get month data
        month_data = {
            'month': self.current_month,
            'budgets': self.budget_manager.get_month_budget(self.current_month),
            'transactions': self.transaction_manager.get_transactions_for_month(self.current_month),
            'spending_by_category': self.transaction_manager.calculate_spending_by_category(self.current_month)
        }
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"financial_data_{self.current_month}.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(month_data, f, indent=2)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
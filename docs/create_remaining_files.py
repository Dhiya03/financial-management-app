#!/usr/bin/env python3
"""
Complete set of remaining placeholder files for Financial Management Tool
Run this script to create all missing files in your project structure
"""

import os
import textwrap

def create_file(filepath, content):
    """Create a file with the given content"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(textwrap.dedent(content).strip() + '\n')
    print(f"Created: {filepath}")

def create_placeholder_files():
    """Create all remaining placeholder files"""
    
    # Create __init__.py files for all packages
    init_files = [
        "financial_management_tool/__init__.py",
        "financial_management_tool/models/__init__.py",
        "financial_management_tool/managers/__init__.py",
        "financial_management_tool/gui/__init__.py",
        "financial_management_tool/gui/tabs/__init__.py",
        "financial_management_tool/gui/dialogs/__init__.py",
        "financial_management_tool/utils/__init__.py",
        "financial_management_tool/resources/__init__.py",
    ]
    
    for init_file in init_files:
        create_file(init_file, '"""Package initialization"""')
    
    # models/budget.py
    create_file("financial_management_tool/models/budget.py", '''
    """
    Budget data model
    """
    from dataclasses import dataclass
    from typing import Dict, Any
    
    @dataclass
    class Budget:
        """Budget data model"""
        month: str
        category: str
        amount: float
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary for JSON serialization"""
            return {
                "month": self.month,
                "category": self.category,
                "amount": self.amount
            }
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
            """Create instance from dictionary"""
            return cls(**data)
        
        def validate(self) -> tuple[bool, list[str]]:
            """Validate budget data"""
            errors = []
            
            if not self.month:
                errors.append("Month is required")
            
            if not self.category:
                errors.append("Category is required")
            
            if self.amount < 0:
                errors.append("Amount cannot be negative")
            
            return len(errors) == 0, errors
    ''')
    
    # gui/tabs/analysis_tab.py
    create_file("financial_management_tool/gui/tabs/analysis_tab.py", '''
    """
    Category analysis tab with visualization and insights
    """
    import tkinter as tk
    from tkinter import ttk
    import logging
    
    class AnalysisTab:
        """Category analysis tab with analytics"""
        
        def __init__(self, parent):
            self.parent = parent
            self.frame = ttk.Frame(parent)
            self.setup_ui()
        
        def setup_ui(self):
            """Setup analysis tab UI"""
            # Title
            title_label = ttk.Label(self.frame, text="Category Analysis", 
                                   font=('Arial', 16, 'bold'))
            title_label.pack(pady=10)
            
            # Placeholder content
            placeholder_frame = ttk.LabelFrame(self.frame, text="Analysis Features Coming Soon", 
                                             padding=20)
            placeholder_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            features = [
                "• Spending trends over 2 years",
                "• Category performance metrics",
                "• Visual charts and graphs",
                "• Seasonal pattern detection",
                "• Budget vs Actual analysis",
                "• Category comparison tools"
            ]
            
            for feature in features:
                ttk.Label(placeholder_frame, text=feature).pack(anchor='w', pady=2)
            
            # Sample chart area
            chart_frame = ttk.LabelFrame(self.frame, text="Chart Area", padding=20)
            chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            ttk.Label(chart_frame, text="[Charts will appear here]", 
                     font=('Arial', 12, 'italic')).pack(expand=True)
        
        def refresh(self):
            """Refresh analysis data"""
            logging.info("Refreshing analysis tab")
            # TODO: Implement data refresh logic
    ''')
    
    # gui/tabs/simulator_tab.py
    create_file("financial_management_tool/gui/tabs/simulator_tab.py", '''
    """
    What-if simulator tab for scenario planning
    """
    import tkinter as tk
    from tkinter import ttk
    import logging
    
    class SimulatorTab:
        """What-if simulator tab"""
        
        def __init__(self, parent):
            self.parent = parent
            self.frame = ttk.Frame(parent)
            self.setup_ui()
        
        def setup_ui(self):
            """Setup simulator tab UI"""
            # Title
            title_label = ttk.Label(self.frame, text="What-If Simulator", 
                                   font=('Arial', 16, 'bold'))
            title_label.pack(pady=10)
            
            # Scenario list frame
            scenario_frame = ttk.LabelFrame(self.frame, text="Scenarios", padding=15)
            scenario_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Buttons
            button_frame = ttk.Frame(scenario_frame)
            button_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Button(button_frame, text="Create New Scenario").pack(side='left', padx=5)
            ttk.Button(button_frame, text="Run Simulation").pack(side='left', padx=5)
            ttk.Button(button_frame, text="Compare Scenarios").pack(side='left', padx=5)
            
            # Placeholder list
            list_frame = ttk.Frame(scenario_frame)
            list_frame.pack(fill='both', expand=True)
            
            ttk.Label(list_frame, text="Scenario Types:", font=('Arial', 12, 'bold')).pack(anchor='w')
            ttk.Label(list_frame, text="• Budget Changes").pack(anchor='w', padx=20)
            ttk.Label(list_frame, text="• One-time Events").pack(anchor='w', padx=20)
            ttk.Label(list_frame, text="• Investment Adjustments").pack(anchor='w', padx=20)
            
            # Results frame
            results_frame = ttk.LabelFrame(self.frame, text="Simulation Results", padding=15)
            results_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            ttk.Label(results_frame, text="[Simulation results will appear here]",
                     font=('Arial', 12, 'italic')).pack(expand=True)
        
        def refresh(self):
            """Refresh simulator data"""
            logging.info("Refreshing simulator tab")
            # TODO: Implement scenario refresh logic
    ''')
    
    # gui/tabs/reports_tab.py
    create_file("financial_management_tool/gui/tabs/reports_tab.py", '''
    """
    Reports and export tab
    """
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import logging
    
    class ReportsTab:
        """Reports and export tab"""
        
        def __init__(self, parent):
            self.parent = parent
            self.frame = ttk.Frame(parent)
            self.setup_ui()
        
        def setup_ui(self):
            """Setup reports tab UI"""
            # Title
            title_label = ttk.Label(self.frame, text="Reports & Export", 
                                   font=('Arial', 16, 'bold'))
            title_label.pack(pady=10)
            
            # Export options
            export_frame = ttk.LabelFrame(self.frame, text="Export Options", padding=20)
            export_frame.pack(fill='x', padx=20, pady=10)
            
            # Export buttons grid
            button_configs = [
                ("Export to JSON", self.export_json, "Complete data backup"),
                ("Export to Excel", self.export_excel, "Formatted spreadsheet with charts"),
                ("Export to CSV", self.export_csv, "Simple data format"),
                ("Generate PDF Report", self.generate_pdf, "Professional report with charts")
            ]
            
            for i, (text, command, desc) in enumerate(button_configs):
                row_frame = ttk.Frame(export_frame)
                row_frame.pack(fill='x', pady=5)
                
                ttk.Button(row_frame, text=text, command=command, width=20).pack(side='left')
                ttk.Label(row_frame, text=f" - {desc}").pack(side='left', padx=10)
            
            # Report customization
            custom_frame = ttk.LabelFrame(self.frame, text="Report Customization", padding=20)
            custom_frame.pack(fill='x', padx=20, pady=10)
            
            ttk.Label(custom_frame, text="Date Range:").grid(row=0, column=0, sticky='w', pady=5)
            date_combo = ttk.Combobox(custom_frame, values=["Last 6 Months", "Current Year", "All Data"])
            date_combo.grid(row=0, column=1, padx=10, pady=5)
            date_combo.set("All Data")
            
            ttk.Label(custom_frame, text="Categories:").grid(row=1, column=0, sticky='w', pady=5)
            cat_combo = ttk.Combobox(custom_frame, values=["All Categories", "Loans & EMIs", "Investments", "Lifestyle"])
            cat_combo.grid(row=1, column=1, padx=10, pady=5)
            cat_combo.set("All Categories")
            
            # Backup section
            backup_frame = ttk.LabelFrame(self.frame, text="Data Management", padding=20)
            backup_frame.pack(fill='x', padx=20, pady=10)
            
            ttk.Button(backup_frame, text="Create Backup", command=self.create_backup).pack(side='left', padx=5)
            ttk.Button(backup_frame, text="Restore from Backup", command=self.restore_backup).pack(side='left', padx=5)
        
        def export_json(self):
            """Export to JSON"""
            messagebox.showinfo("Export", "JSON export functionality coming soon")
        
        def export_excel(self):
            """Export to Excel"""
            messagebox.showinfo("Export", "Excel export functionality coming soon")
        
        def export_csv(self):
            """Export to CSV"""
            messagebox.showinfo("Export", "CSV export functionality coming soon")
        
        def generate_pdf(self):
            """Generate PDF report"""
            messagebox.showinfo("Export", "PDF generation functionality coming soon")
        
        def create_backup(self):
            """Create data backup"""
            messagebox.showinfo("Backup", "Backup functionality coming soon")
        
        def restore_backup(self):
            """Restore from backup"""
            messagebox.showinfo("Restore", "Restore functionality coming soon")
        
        def refresh(self):
            """Refresh reports data"""
            logging.info("Refreshing reports tab")
            # TODO: Implement report refresh logic
    ''')
    
    # gui/dialogs/template_dialog.py
    create_file("financial_management_tool/gui/dialogs/template_dialog.py", '''
    """
    Budget template dialog
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    class TemplateDialog:
        """Dialog for applying budget templates"""
        
        def __init__(self, parent, current_month, callback=None):
            self.parent = parent
            self.current_month = current_month
            self.callback = callback
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Apply Budget Template")
            self.dialog.geometry("400x300")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            self.setup_ui()
            self.center_dialog()
        
        def setup_ui(self):
            """Setup dialog UI"""
            main_frame = ttk.Frame(self.dialog, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Instructions
            ttk.Label(main_frame, text="Select a budget template to apply:",
                     font=('Arial', 12)).pack(pady=(0, 20))
            
            # Template selection
            self.template_var = tk.StringVar()
            templates = ["Conservative", "Moderate", "Aggressive"]
            
            for template in templates:
                ttk.Radiobutton(main_frame, text=template, variable=self.template_var,
                               value=template).pack(anchor='w', pady=5)
            
            self.template_var.set("Conservative")
            
            # Apply to multiple months option
            self.multi_month_var = tk.BooleanVar()
            ttk.Checkbutton(main_frame, text="Apply to all 24 months",
                           variable=self.multi_month_var).pack(pady=20)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(side='bottom', pady=20)
            
            ttk.Button(button_frame, text="Apply", command=self.apply_template).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
        
        def apply_template(self):
            """Apply selected template"""
            template = self.template_var.get()
            apply_all = self.multi_month_var.get()
            
            # TODO: Implement template application logic
            messagebox.showinfo("Success", f"Applied {template} template")
            
            if self.callback:
                self.callback()
            
            self.dialog.destroy()
        
        def center_dialog(self):
            """Center dialog on screen"""
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - 200
            y = (self.dialog.winfo_screenheight() // 2) - 150
            self.dialog.geometry(f"400x300+{x}+{y}")
    ''')
    
    # gui/dialogs/analytics_dialog.py
    create_file("financial_management_tool/gui/dialogs/analytics_dialog.py", '''
    """
    Analytics details dialog
    """
    import tkinter as tk
    from tkinter import ttk
    
    class AnalyticsDialog:
        """Dialog for detailed analytics view"""
        
        def __init__(self, parent, category=None):
            self.parent = parent
            self.category = category
            self.dialog = tk.Toplevel(parent)
            self.dialog.title(f"Analytics: {category or 'All Categories'}")
            self.dialog.geometry("600x500")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            self.setup_ui()
            self.center_dialog()
        
        def setup_ui(self):
            """Setup dialog UI"""
            main_frame = ttk.Frame(self.dialog, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Title
            title = f"Detailed Analysis: {self.category or 'All Categories'}"
            ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
            
            # Placeholder content
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill='both', expand=True)
            
            # Trends tab
            trends_frame = ttk.Frame(notebook)
            notebook.add(trends_frame, text="Trends")
            ttk.Label(trends_frame, text="[Trend analysis will appear here]",
                     font=('Arial', 12, 'italic')).pack(expand=True)
            
            # Statistics tab
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="Statistics")
            ttk.Label(stats_frame, text="[Statistical analysis will appear here]",
                     font=('Arial', 12, 'italic')).pack(expand=True)
            
            # Insights tab
            insights_frame = ttk.Frame(notebook)
            notebook.add(insights_frame, text="Insights")
            ttk.Label(insights_frame, text="[AI-generated insights will appear here]",
                     font=('Arial', 12, 'italic')).pack(expand=True)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=10)
        
        def center_dialog(self):
            """Center dialog on screen"""
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - 300
            y = (self.dialog.winfo_screenheight() // 2) - 250
            self.dialog.geometry(f"600x500+{x}+{y}")
    ''')
    
    # gui/dialogs/scenario_dialog.py
    create_file("financial_management_tool/gui/dialogs/scenario_dialog.py", '''
    """
    Create scenario dialog for what-if simulations
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    class ScenarioDialog:
        """Dialog for creating what-if scenarios"""
        
        def __init__(self, parent, callback=None):
            self.parent = parent
            self.callback = callback
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Create New Scenario")
            self.dialog.geometry("500x400")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            self.setup_ui()
            self.center_dialog()
        
        def setup_ui(self):
            """Setup dialog UI"""
            main_frame = ttk.Frame(self.dialog, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Scenario name
            ttk.Label(main_frame, text="Scenario Name:").grid(row=0, column=0, sticky='w', pady=5)
            self.name_var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
            
            # Scenario type
            ttk.Label(main_frame, text="Type:").grid(row=1, column=0, sticky='w', pady=5)
            self.type_var = tk.StringVar()
            type_combo = ttk.Combobox(main_frame, textvariable=self.type_var,
                                     values=["Budget Change", "One-time Event", "Investment Adjustment"],
                                     width=37)
            type_combo.grid(row=1, column=1, pady=5)
            type_combo.set("Budget Change")
            
            # Description
            ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=5)
            self.desc_text = tk.Text(main_frame, width=40, height=4)
            self.desc_text.grid(row=2, column=1, pady=5)
            
            # Parameters frame
            param_frame = ttk.LabelFrame(main_frame, text="Scenario Parameters", padding=10)
            param_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')
            
            ttk.Label(param_frame, text="Category:").grid(row=0, column=0, sticky='w', pady=5)
            self.category_var = tk.StringVar()
            ttk.Combobox(param_frame, textvariable=self.category_var, width=25).grid(row=0, column=1, pady=5)
            
            ttk.Label(param_frame, text="Amount Change:").grid(row=1, column=0, sticky='w', pady=5)
            self.amount_var = tk.StringVar()
            ttk.Entry(param_frame, textvariable=self.amount_var, width=27).grid(row=1, column=1, pady=5)
            
            ttk.Label(param_frame, text="Start Month:").grid(row=2, column=0, sticky='w', pady=5)
            self.start_var = tk.StringVar()
            ttk.Combobox(param_frame, textvariable=self.start_var, width=25).grid(row=2, column=1, pady=5)
            
            ttk.Label(param_frame, text="End Month:").grid(row=3, column=0, sticky='w', pady=5)
            self.end_var = tk.StringVar()
            ttk.Combobox(param_frame, textvariable=self.end_var, width=25).grid(row=3, column=1, pady=5)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            ttk.Button(button_frame, text="Create", command=self.create_scenario).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
        
        def create_scenario(self):
            """Create the scenario"""
            # TODO: Implement scenario creation logic
            messagebox.showinfo("Success", "Scenario created successfully")
            
            if self.callback:
                self.callback()
            
            self.dialog.destroy()
        
        def center_dialog(self):
            """Center dialog on screen"""
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - 250
            y = (self.dialog.winfo_screenheight() // 2) - 200
            self.dialog.geometry(f"500x400+{x}+{y}")
    ''')
    
    # managers/analytics_engine.py
    create_file("financial_management_tool/managers/analytics_engine.py", '''
    """
    Analytics and insights engine
    """
    import logging
    from typing import Dict, List, Any, Optional
    from datetime import datetime, timedelta
    
    class AnalyticsEngine:
        """Provides advanced analytics and insights"""
        
        def __init__(self):
            from managers.data_manager import data_manager
            self.app_data = data_manager.get_data()
        
        def get_spending_trends(self, months: List[str], category: Optional[str] = None) -> Dict[str, Any]:
            """Get spending trends over time"""
            try:
                trends = {
                    'data': {},
                    'trend_direction': 'stable',
                    'average': 0,
                    'total': 0,
                    'min': 0,
                    'max': 0
                }
                
                spending_data = []
                
                for month in months:
                    transactions = self.app_data.transactions.get(month, [])
                    
                    if category:
                        month_spending = sum(t['amount'] for t in transactions 
                                           if t.get('category') == category)
                    else:
                        month_spending = sum(t['amount'] for t in transactions)
                    
                    trends['data'][month] = month_spending
                    spending_data.append(month_spending)
                
                if spending_data:
                    trends['average'] = sum(spending_data) / len(spending_data)
                    trends['total'] = sum(spending_data)
                    trends['min'] = min(spending_data)
                    trends['max'] = max(spending_data)
                    
                    # Determine trend direction
                    if len(spending_data) >= 3:
                        recent_avg = sum(spending_data[-3:]) / 3
                        older_avg = sum(spending_data[:3]) / 3
                        
                        if recent_avg > older_avg * 1.1:
                            trends['trend_direction'] = 'increasing'
                        elif recent_avg < older_avg * 0.9:
                            trends['trend_direction'] = 'decreasing'
                
                return trends
                
            except Exception as e:
                logging.error(f"Error calculating trends: {e}")
                return {'data': {}, 'trend_direction': 'unknown', 'average': 0}
        
        def get_category_performance(self) -> List[Dict[str, Any]]:
            """Get performance analysis for all categories"""
            try:
                performance = []
                
                # Get all categories
                all_categories = set()
                for group_categories in self.app_data.categories.values():
                    all_categories.update(group_categories)
                
                for category in all_categories:
                    cat_data = self.analyze_category(category)
                    performance.append(cat_data)
                
                # Sort by total spending
                performance.sort(key=lambda x: x['total_spent'], reverse=True)
                
                return performance
                
            except Exception as e:
                logging.error(f"Error analyzing category performance: {e}")
                return []
        
        def analyze_category(self, category: str) -> Dict[str, Any]:
            """Analyze a specific category"""
            analysis = {
                'category': category,
                'total_spent': 0,
                'total_budget': 0,
                'adherence_rate': 0,
                'months_over_budget': 0,
                'months_with_data': 0,
                'average_monthly': 0
            }
            
            monthly_spending = []
            
            for month in self.app_data.transactions.keys():
                transactions = self.app_data.transactions[month]
                month_spending = sum(t['amount'] for t in transactions 
                                   if t.get('category') == category)
                
                if month_spending > 0:
                    analysis['months_with_data'] += 1
                    monthly_spending.append(month_spending)
                    analysis['total_spent'] += month_spending
                    
                    # Check budget
                    month_budget = self.app_data.budgets.get(month, {}).get(category, 0)
                    if month_budget > 0:
                        analysis['total_budget'] += month_budget
                        if month_spending > month_budget:
                            analysis['months_over_budget'] += 1
            
            if analysis['months_with_data'] > 0:
                analysis['average_monthly'] = analysis['total_spent'] / analysis['months_with_data']
            
            if analysis['total_budget'] > 0:
                analysis['adherence_rate'] = (analysis['total_spent'] / analysis['total_budget']) * 100
            
            return analysis
        
        def detect_anomalies(self, category: str = None) -> List[Dict[str, Any]]:
            """Detect spending anomalies"""
            anomalies = []
            
            # TODO: Implement anomaly detection algorithm
            # This would analyze spending patterns and identify unusual transactions
            
            return anomalies
        
        def get_insights(self) -> List[str]:
            """Generate actionable insights"""
            insights = []
            
            # Analyze overall spending
            total_spending = sum(
                sum(t['amount'] for t in transactions)
                for transactions in self.app_data.transactions.values()
            )
            
            total_budget = sum(
                sum(budgets.values())
                for budgets in self.app_data.budgets.values()
            )
            
            if total_budget > 0:
                adherence = (total_spending / total_budget) * 100
                if adherence > 110:
                    insights.append("⚠️ Overall spending exceeds budget by more than 10%")
                elif adherence < 90:
                    insights.append("✅ Good job! You're under budget by more than 10%")
            
            # Category-specific insights
            performance = self.get_category_performance()
            for cat_perf in performance[:3]:  # Top 3 spending categories
                if cat_perf['adherence_rate'] > 120:
                    insights.append(f"💰 {cat_perf['category']} is significantly over budget")
            
            return insights
    ''')
    
    # utils/file_handlers.py
    create_file("financial_management_tool/utils/file_handlers.py", '''
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
    ''')
    
    # resources/templates/budget_templates.json
    create_file("financial_management_tool/resources/templates/budget_templates.json", '''
    {
      "Conservative": {
        "Credit Card EMI 1": 15000,
        "Credit Card EMI 2": 12000,
        "Personal Loan EMI 1": 8000,
        "Personal Loan EMI 2": 6000,
        "Home Loan EMI": 25000,
        "Mutual Fund SIP": 5000,
        "PPF": 2000,
        "RD": 3000,
        "Ponmagan Policy": 1500,
        "Gold Investment": 2000,
        "Bitcoin Investment": 1000,
        "Baby Health Policy": 800,
        "Baby Education Policy": 1200,
        "OTT Subscriptions": 500,
        "Hospital": 8000,
        "Swiggy/Food": 3000,
        "Petrol": 3000,
        "General Expenses": 5000,
        "Shopping": 5000
      },
      "Moderate": {
        "Credit Card EMI 1": 15000,
        "Credit Card EMI 2": 12000,
        "Personal Loan EMI 1": 8000,
        "Personal Loan EMI 2": 6000,
        "Home Loan EMI": 25000,
        "Mutual Fund SIP": 7000,
        "PPF": 2000,
        "RD": 3000,
        "Ponmagan Policy": 1500,
        "Gold Investment": 3000,
        "Bitcoin Investment": 2000,
        "Baby Health Policy": 800,
        "Baby Education Policy": 1200,
        "OTT Subscriptions": 800,
        "Hospital": 10000,
        "Swiggy/Food": 5000,
        "Petrol": 4000,
        "General Expenses": 8000,
        "Shopping": 8000
      },
      "Aggressive": {
        "Credit Card EMI 1": 15000,
        "Credit Card EMI 2": 12000,
        "Personal Loan EMI 1": 8000,
        "Personal Loan EMI 2": 6000,
        "Home Loan EMI": 25000,
        "Mutual Fund SIP": 10000,
        "PPF": 2000,
        "RD": 5000,
        "Ponmagan Policy": 1500,
        "Gold Investment": 5000,
        "Bitcoin Investment": 3000,
        "Baby Health Policy": 1000,
        "Baby Education Policy": 1500,
        "OTT Subscriptions": 1000,
        "Hospital": 12000,
        "Swiggy/Food": 8000,
        "Petrol": 5000,
        "General Expenses": 10000,
        "Shopping": 12000
      }
    }
    ''')
    
    # resources/sample_data/sample_transactions.csv
    create_file("financial_management_tool/resources/sample_data/sample_transactions.csv", '''
    Date,Category,Amount,Description,Source
    2025-08-01,Credit Card EMI 1,15000,Monthly EMI Payment,manual
    2025-08-05,Mutual Fund SIP,5000,SIP Investment,manual
    2025-08-10,Hospital,8500,Medical Consultation,imported
    2025-08-12,Swiggy/Food,1250,Food Delivery,imported
    2025-08-15,Petrol,3000,Fuel,manual
    2025-08-18,Shopping,5500,Amazon Purchase,imported
    2025-08-20,General Expenses,2000,Miscellaneous,manual
    2025-08-22,OTT Subscriptions,500,Netflix,manual
    2025-08-25,PPF,2000,PPF Deposit,manual
    2025-08-28,Gold Investment,2000,Gold SIP,manual
    ''')
    
    print("\n" + "="*60)
    print("✅ All placeholder files created successfully!")
    print("="*60)
    print("\nProject structure is now complete. You can run:")
    print("  cd financial_management_tool")
    print("  python main.py")
    print("\nNote: The application will create the data directory")
    print("and app_data.json file automatically on first run.")

if __name__ == "__main__":
    create_placeholder_files()

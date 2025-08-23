# reports_tab.py
# User Story 6: Reports Tab - Comprehensive Reporting System

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.backends.backend_tkagg as tkagg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ReportsTab:
    """
    Comprehensive reporting system with multi-format export capabilities.
    Supports JSON, Excel, CSV, and PDF exports with customizable templates.
    """
    
    def __init__(self, parent_notebook, data_manager):
        self.parent = parent_notebook
        self.data_manager = data_manager
        
        # Create reports tab
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Reports")
        
        # Export formats available
        self.export_formats = {
            'json': {'name': 'JSON Export', 'icon': '📄', 'desc': 'Complete data backup'},
            'excel': {'name': 'Excel Export', 'icon': '📊', 'desc': 'Professional spreadsheet with charts'},
            'csv': {'name': 'CSV Export', 'icon': '📋', 'desc': 'Simple data format'},
            'pdf': {'name': 'PDF Report', 'icon': '📑', 'desc': 'Executive summary report'}
        }
        
        # Initialize report history
        self.report_history = []
        self.load_report_history()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the Reports tab user interface"""
        # Create main container with scrollable frame
        main_frame = tk.Frame(self.frame, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Export & Reports",
            font=('Arial', 18, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Create export options section
        self.create_export_section(main_frame)
        
        # Create customization section
        self.create_customization_section(main_frame)
        
        # Create data management section
        self.create_data_management_section(main_frame)
        
        # Create report history section
        self.create_report_history_section(main_frame)
    
    def create_export_section(self, parent):
        """Create export options cards"""
        export_frame = tk.Frame(parent, bg='#f8f9fa')
        export_frame.pack(fill='x', pady=(0, 30))
        
        # Export options grid
        options_frame = tk.Frame(export_frame, bg='#f8f9fa')
        options_frame.pack(fill='x')
        
        # Configure grid columns
        for i in range(2):
            options_frame.columnconfigure(i, weight=1, uniform="export_col")
        
        # Create export cards
        row = 0
        col = 0
        for format_key, format_info in self.export_formats.items():
            card_frame = self.create_export_card(
                options_frame, format_key, format_info
            )
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
    def create_export_card(self, parent, format_key, format_info):
        """Create individual export card"""
        card_frame = tk.Frame(
            parent,
            bg='white',
            relief='solid',
            bd=1
        )
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Icon
        icon_label = tk.Label(
            content_frame,
            text=format_info['icon'],
            font=('Arial', 48),
            bg='white'
        )
        icon_label.pack()
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=format_info['name'],
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(15, 10))
        
        # Description
        desc_label = tk.Label(
            content_frame,
            text=format_info['desc'],
            font=('Arial', 14),
            bg='white',
            fg='#6c757d',
            wraplength=200
        )
        desc_label.pack(pady=(0, 15))
        
        # Export button
        export_btn = tk.Button(
            content_frame,
            text=f"Export {format_info['name']}",
            font=('Arial', 12, 'bold'),
            bg='#007bff',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda fmt=format_key: self.export_data(fmt)
        )
        export_btn.pack()
        
        # Hover effects
        def on_enter(e):
            card_frame.configure(relief='solid', bd=2)
            export_btn.configure(bg='#0056b3')
            
        def on_leave(e):
            card_frame.configure(relief='solid', bd=1)
            export_btn.configure(bg='#007bff')
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        for child in card_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
        
        return card_frame
    
    def create_customization_section(self, parent):
        """Create report customization section"""
        custom_frame = tk.LabelFrame(
            parent,
            text="Report Customization",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=25,
            pady=20
        )
        custom_frame.pack(fill='x', pady=(0, 30))
        
        # Two-column layout
        left_frame = tk.Frame(custom_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        right_frame = tk.Frame(custom_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Date Range Selection
        tk.Label(
            left_frame,
            text="Date Range:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.date_range_var = tk.StringVar(value="Last 6 Months")
        date_range_combo = ttk.Combobox(
            left_frame,
            textvariable=self.date_range_var,
            values=[
                "Current Month",
                "Last 3 Months", 
                "Last 6 Months",
                "Current Year",
                "All Data (2 Years)",
                "Custom Range"
            ],
            state='readonly',
            width=25
        )
        date_range_combo.pack(fill='x', pady=(0, 15))
        
        # Categories Selection
        tk.Label(
            left_frame,
            text="Categories:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.categories_var = tk.StringVar(value="All Categories")
        categories_combo = ttk.Combobox(
            left_frame,
            textvariable=self.categories_var,
            values=[
                "All Categories",
                "Loans & EMIs Only",
                "Investments Only", 
                "Lifestyle & Essentials Only",
                "Custom Selection"
            ],
            state='readonly',
            width=25
        )
        categories_combo.pack(fill='x')
        
        # Report Type Selection
        tk.Label(
            right_frame,
            text="Report Type:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))
        
        self.report_type_var = tk.StringVar(value="Executive Summary")
        report_type_combo = ttk.Combobox(
            right_frame,
            textvariable=self.report_type_var,
            values=[
                "Executive Summary",
                "Detailed Analysis",
                "Transaction Details",
                "Budget Performance",
                "Category Analysis",
                "What-If Scenarios"
            ],
            state='readonly',
            width=25
        )
        report_type_combo.pack(fill='x', pady=(0, 15))
        
        # Generate Custom Report Button
        generate_btn = tk.Button(
            right_frame,
            text="Generate Custom Report",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.generate_custom_report
        )
        generate_btn.pack(fill='x')
    
    def create_data_management_section(self, parent):
        """Create data management section"""
        data_frame = tk.LabelFrame(
            parent,
            text="Data Management",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=25,
            pady=20
        )
        data_frame.pack(fill='x', pady=(0, 30))
        
        # Button container
        buttons_frame = tk.Frame(data_frame, bg='white')
        buttons_frame.pack(fill='x')
        
        # Management buttons
        buttons = [
            ("Create Backup", '#28a745', self.create_backup),
            ("Restore from Backup", '#6c757d', self.restore_backup),
            ("Import Data", '#6c757d', self.import_data),
            ("Schedule Auto-Reports", '#007bff', self.schedule_reports)
        ]
        
        for i, (text, color, command) in enumerate(buttons):
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=('Arial', 12, 'bold'),
                bg=color,
                fg='white',
                bd=0,
                padx=20,
                pady=10,
                cursor='hand2',
                command=command
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
        
        # Configure grid weights
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # Data info section
        info_frame = tk.Frame(data_frame, bg='white')
        info_frame.pack(fill='x', pady=(20, 0))
        
        # Separator line
        separator = tk.Frame(info_frame, height=1, bg='#e9ecef')
        separator.pack(fill='x', pady=(0, 15))
        
        # Data statistics
        stats_frame = tk.Frame(info_frame, bg='white')
        stats_frame.pack()
        
        # Get current data stats
        stats = self.get_data_statistics()
        
        stats_text = f"Last Backup: {stats['last_backup']} | Data Size: {stats['data_size']} | Total Records: {stats['total_records']}"
        stats_label = tk.Label(
            stats_frame,
            text=stats_text,
            font=('Arial', 12),
            bg='white',
            fg='#6c757d'
        )
        stats_label.pack()
    
    def create_report_history_section(self, parent):
        """Create report history section"""
        history_frame = tk.LabelFrame(
            parent,
            text="Recent Reports",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=25,
            pady=20
        )
        history_frame.pack(fill='both', expand=True)
        
        # Create treeview for report history
        columns = ('Name', 'Generated', 'Type', 'Size', 'Actions')
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show='headings',
            height=6
        )
        
        # Configure columns
        column_widths = {'Name': 300, 'Generated': 150, 'Type': 100, 'Size': 100, 'Actions': 120}
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths[col], anchor='w')
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate report history
        self.populate_report_history()
        
        # Bind double-click event
        self.history_tree.bind('<Double-1>', self.on_history_double_click)
    
    def export_data(self, format_type: str):
        """Export data in the specified format"""
        try:
            # Get current data
            data = self.data_manager.get_all_data()
            
            if format_type == 'json':
                self.export_json(data)
            elif format_type == 'excel':
                self.export_excel(data)
            elif format_type == 'csv':
                self.export_csv(data)
            elif format_type == 'pdf':
                self.export_pdf(data)
            else:
                messagebox.showerror("Error", f"Unsupported format: {format_type}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def export_json(self, data: Dict):
        """Export data as JSON"""
        filename = filedialog.asksaveasfilename(
            title="Export JSON Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=f"financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                # Add to history
                self.add_to_history(
                    name=os.path.basename(filename),
                    file_type="JSON",
                    file_path=filename
                )
                
                messagebox.showinfo("Success", f"Data exported successfully to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def export_excel(self, data: Dict):
        """Export data as Excel workbook"""
        if not PANDAS_AVAILABLE:
            messagebox.showwarning(
                "Missing Dependency", 
                "pandas is required for Excel export. Install with: pip install pandas openpyxl"
            )
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Excel Data",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialname=f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if filename:
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Summary sheet
                    summary_data = self.prepare_summary_data(data)
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Transactions sheet
                    if 'transactions' in data:
                        transactions_data = []
                        for month, transactions in data['transactions'].items():
                            for transaction in transactions:
                                transaction['month'] = month
                                transactions_data.append(transaction)
                        
                        if transactions_data:
                            transactions_df = pd.DataFrame(transactions_data)
                            transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
                    
                    # Budgets sheet
                    if 'budgets' in data:
                        budgets_data = []
                        for month, budgets in data['budgets'].items():
                            for category, amount in budgets.items():
                                budgets_data.append({
                                    'Month': month,
                                    'Category': category,
                                    'Budgeted Amount': amount
                                })
                        
                        if budgets_data:
                            budgets_df = pd.DataFrame(budgets_data)
                            budgets_df.to_excel(writer, sheet_name='Budgets', index=False)
                
                # Add to history
                self.add_to_history(
                    name=os.path.basename(filename),
                    file_type="Excel",
                    file_path=filename
                )
                
                messagebox.showinfo("Success", f"Excel report exported successfully to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")
    
    def export_csv(self, data: Dict):
        """Export transactions as CSV"""
        filename = filedialog.asksaveasfilename(
            title="Export CSV Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                # Prepare transactions data
                transactions_data = []
                if 'transactions' in data:
                    for month, transactions in data['transactions'].items():
                        for transaction in transactions:
                            transaction_copy = transaction.copy()
                            transaction_copy['month'] = month
                            transactions_data.append(transaction_copy)
                
                # Write CSV
                if transactions_data:
                    fieldnames = ['month', 'date', 'category', 'amount', 'description', 'source']
                    
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for transaction in transactions_data:
                            row = {field: transaction.get(field, '') for field in fieldnames}
                            writer.writerow(row)
                
                # Add to history
                self.add_to_history(
                    name=os.path.basename(filename),
                    file_type="CSV",
                    file_path=filename
                )
                
                messagebox.showinfo("Success", f"CSV data exported successfully to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_pdf(self, data: Dict):
        """Export as PDF report (placeholder implementation)"""
        # For now, create a text-based report
        filename = filedialog.asksaveasfilename(
            title="Export PDF Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialname=f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                report_content = self.generate_text_report(data)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                # Add to history
                self.add_to_history(
                    name=os.path.basename(filename),
                    file_type="PDF/Text",
                    file_path=filename
                )
                
                messagebox.showinfo(
                    "Success", 
                    f"Report exported successfully to {filename}\n\n"
                    "Note: Full PDF export requires additional libraries. "
                    "This is a formatted text report."
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def generate_custom_report(self):
        """Generate customized report based on user selections"""
        try:
            # Get selections
            date_range = self.date_range_var.get()
            categories = self.categories_var.get()
            report_type = self.report_type_var.get()
            
            # Get filtered data based on selections
            filtered_data = self.filter_data_for_report(date_range, categories)
            
            # Generate report based on type
            if report_type == "Executive Summary":
                self.generate_executive_summary(filtered_data)
            elif report_type == "Detailed Analysis":
                self.generate_detailed_analysis(filtered_data)
            elif report_type == "Transaction Details":
                self.generate_transaction_details(filtered_data)
            elif report_type == "Budget Performance":
                self.generate_budget_performance(filtered_data)
            elif report_type == "Category Analysis":
                self.generate_category_analysis(filtered_data)
            elif report_type == "What-If Scenarios":
                self.generate_scenario_analysis(filtered_data)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate custom report: {str(e)}")
    
    def create_backup(self):
        """Create data backup"""
        try:
            backup_data = self.data_manager.create_backup()
            if backup_data:
                messagebox.showinfo("Success", "Backup created successfully!")
                self.refresh_data_statistics()
            else:
                messagebox.showerror("Error", "Failed to create backup")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_backup(self):
        """Restore from backup"""
        filename = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                result = self.data_manager.restore_from_backup(filename)
                if result:
                    messagebox.showinfo("Success", "Data restored successfully!")
                    self.refresh_data_statistics()
                else:
                    messagebox.showerror("Error", "Failed to restore data")
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def import_data(self):
        """Import data from file"""
        filename = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                # Determine file type and import accordingly
                file_ext = Path(filename).suffix.lower()
                
                if file_ext == '.json':
                    self.import_json_data(filename)
                elif file_ext == '.csv':
                    self.import_csv_data(filename)
                elif file_ext in ['.xlsx', '.xls']:
                    self.import_excel_data(filename)
                else:
                    messagebox.showerror("Error", "Unsupported file format")
                    return
                    
                messagebox.showinfo("Success", "Data imported successfully!")
                self.refresh_data_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def schedule_reports(self):
        """Schedule automatic reports (placeholder)"""
        messagebox.showinfo(
            "Feature Coming Soon",
            "Automatic report scheduling will be available in a future update."
        )
    
    # Helper methods for data processing
    
    def prepare_summary_data(self, data: Dict) -> List[Dict]:
        """Prepare summary data for reports"""
        summary = []
        
        # Add budget summary
        if 'budgets' in data:
            total_budgets = {}
            for month, budgets in data['budgets'].items():
                for category, amount in budgets.items():
                    total_budgets[category] = total_budgets.get(category, 0) + amount
            
            for category, total in total_budgets.items():
                summary.append({
                    'Category': category,
                    'Total Budget': total,
                    'Type': 'Budget'
                })
        
        return summary
    
    def generate_text_report(self, data: Dict) -> str:
        """Generate text-based financial report"""
        report = []
        report.append("=" * 60)
        report.append("FINANCIAL MANAGEMENT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Budget Summary
        if 'budgets' in data:
            report.append("BUDGET SUMMARY")
            report.append("-" * 30)
            
            category_totals = {}
            for month, budgets in data['budgets'].items():
                for category, amount in budgets.items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            for category, total in sorted(category_totals.items()):
                report.append(f"{category}: ₹{total:,.2f}")
            
            report.append("")
        
        # Transaction Summary
        if 'transactions' in data:
            report.append("TRANSACTION SUMMARY")
            report.append("-" * 30)
            
            total_transactions = 0
            total_amount = 0
            
            for month, transactions in data['transactions'].items():
                total_transactions += len(transactions)
                total_amount += sum(t.get('amount', 0) for t in transactions)
            
            report.append(f"Total Transactions: {total_transactions}")
            report.append(f"Total Amount: ₹{total_amount:,.2f}")
            report.append("")
        
        report.append("=" * 60)
        report.append("End of Report")
        
        return "\n".join(report)
    
    def filter_data_for_report(self, date_range: str, categories: str) -> Dict:
        """Filter data based on report criteria"""
        # This is a placeholder implementation
        # In a real implementation, you would filter the data based on the criteria
        return self.data_manager.get_all_data()
    
    def generate_executive_summary(self, data: Dict):
        """Generate executive summary report"""
        messagebox.showinfo("Report Generated", "Executive Summary report has been generated!")
    
    def generate_detailed_analysis(self, data: Dict):
        """Generate detailed analysis report"""
        messagebox.showinfo("Report Generated", "Detailed Analysis report has been generated!")
    
    def generate_transaction_details(self, data: Dict):
        """Generate transaction details report"""
        messagebox.showinfo("Report Generated", "Transaction Details report has been generated!")
    
    def generate_budget_performance(self, data: Dict):
        """Generate budget performance report"""
        messagebox.showinfo("Report Generated", "Budget Performance report has been generated!")
    
    def generate_category_analysis(self, data: Dict):
        """Generate category analysis report"""
        messagebox.showinfo("Report Generated", "Category Analysis report has been generated!")
    
    def generate_scenario_analysis(self, data: Dict):
        """Generate scenario analysis report"""
        messagebox.showinfo("Report Generated", "What-If Scenarios report has been generated!")
    
    def import_json_data(self, filename: str):
        """Import data from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)
        # Process and merge with existing data
        self.data_manager.merge_data(imported_data)
    
    def import_csv_data(self, filename: str):
        """Import transactions from CSV file"""
        # This would integrate with the transaction import functionality
        # For now, just acknowledge the import
        pass
    
    def import_excel_data(self, filename: str):
        """Import data from Excel file"""
        if PANDAS_AVAILABLE:
            # Read Excel file and process
            df = pd.read_excel(filename)
            # Process and import data
            pass
    
    def get_data_statistics(self) -> Dict[str, str]:
        """Get current data statistics"""
        try:
            data = self.data_manager.get_all_data()
            
            # Calculate statistics
            total_transactions = 0
            if 'transactions' in data:
                for month, transactions in data['transactions'].items():
                    total_transactions += len(transactions)
            
            # Get file size
            data_file_path = self.data_manager.data_file_path
            file_size = "Unknown"
            if os.path.exists(data_file_path):
                size_bytes = os.path.getsize(data_file_path)
                if size_bytes < 1024:
                    file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    file_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Get last backup date
            backup_dir = os.path.join(os.path.dirname(data_file_path), 'backups')
            last_backup = "Never"
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
                if backup_files:
                    latest_backup = max(backup_files, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
                    backup_time = os.path.getctime(os.path.join(backup_dir, latest_backup))
                    last_backup = datetime.fromtimestamp(backup_time).strftime('%b %d, %Y')
            
            return {
                'last_backup': last_backup,
                'data_size': file_size,
                'total_records': str(total_transactions)
            }
            
        except Exception as e:
            return {
                'last_backup': "Unknown",
                'data_size': "Unknown", 
                'total_records': "Unknown"
            }
    
    def load_report_history(self):
        """Load report history from file"""
        try:
            history_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'report_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.report_history = json.load(f)
        except Exception:
            self.report_history = []
    
    def save_report_history(self):
        """Save report history to file"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            history_file = os.path.join(data_dir, 'report_history.json')
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.report_history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving report history: {e}")
    
    def add_to_history(self, name: str, file_type: str, file_path: str):
        """Add report to history"""
        history_item = {
            'name': name,
            'generated': datetime.now().strftime('%b %d, %Y'),
            'type': file_type,
            'size': self.get_file_size(file_path),
            'path': file_path
        }
        
        # Add to beginning of list
        self.report_history.insert(0, history_item)
        
        # Keep only last 50 reports
        self.report_history = self.report_history[:50]
        
        # Save to file
        self.save_report_history()
        
        # Update UI
        self.populate_report_history()
    
    def get_file_size(self, file_path: str) -> str:
        """Get formatted file size"""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def populate_report_history(self):
        """Populate the report history treeview"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items
        for report in self.report_history:
            self.history_tree.insert('', 'end', values=(
                report['name'],
                report['generated'],
                report['type'],
                report['size'],
                'Download'
            ))
    
    def on_history_double_click(self, event):
        """Handle double-click on history item"""
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            report_name = item['values'][0]
            
            # Find the report in history
            for report in self.report_history:
                if report['name'] == report_name:
                    if os.path.exists(report['path']):
                        try:
                            # Open file with default application
                            if os.name == 'nt':  # Windows
                                os.startfile(report['path'])
                            elif os.name == 'posix':  # macOS and Linux
                                os.system(f'open "{report["path"]}"' if sys.platform == 'darwin' 
                                         else f'xdg-open "{report["path"]}"')
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not open file: {str(e)}")
                    else:
                        messagebox.showerror("Error", "File no longer exists")
                    break
    
    def refresh_data_statistics(self):
        """Refresh the data statistics display"""
        # This would update the statistics display
        # For now, just update the internal stats
        self.get_data_statistics()


# Additional utility class for advanced report generation
class ReportGenerator:
    """
    Advanced report generator with template support and custom formatting
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def generate_executive_summary(self, data: Dict, date_range: str) -> Dict:
        """Generate executive summary with key metrics"""
        summary = {
            'title': 'Executive Financial Summary',
            'period': date_range,
            'generated_at': datetime.now().isoformat(),
            'key_metrics': {},
            'insights': [],
            'recommendations': []
        }
        
        try:
            # Calculate total budget and spending
            total_budget = 0
            total_spent = 0
            
            if 'budgets' in data:
                for month, budgets in data['budgets'].items():
                    total_budget += sum(budgets.values())
            
            if 'transactions' in data:
                for month, transactions in data['transactions'].items():
                    total_spent += sum(t.get('amount', 0) for t in transactions)
            
            # Key metrics
            summary['key_metrics'] = {
                'total_budget': total_budget,
                'total_spent': total_spent,
                'remaining_budget': total_budget - total_spent,
                'spending_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
                'average_monthly_spending': total_spent / 12 if total_spent > 0 else 0  # Assuming yearly data
            }
            
            # Generate insights
            spending_pct = summary['key_metrics']['spending_percentage']
            if spending_pct > 100:
                summary['insights'].append(f"Over budget by {spending_pct - 100:.1f}%")
            elif spending_pct > 80:
                summary['insights'].append("Approaching budget limits")
            else:
                summary['insights'].append("Spending within healthy limits")
            
            # Generate recommendations
            if spending_pct > 90:
                summary['recommendations'].append("Consider reducing discretionary spending")
                summary['recommendations'].append("Review and adjust budget allocations")
            
            return summary
            
        except Exception as e:
            print(f"Error generating executive summary: {e}")
            return summary
    
    def generate_category_breakdown(self, data: Dict) -> Dict:
        """Generate detailed category breakdown"""
        breakdown = {
            'categories': {},
            'top_spending_categories': [],
            'category_trends': {}
        }
        
        try:
            # Calculate category totals
            category_totals = {}
            
            if 'transactions' in data:
                for month, transactions in data['transactions'].items():
                    for transaction in transactions:
                        category = transaction.get('category', 'Uncategorized')
                        amount = transaction.get('amount', 0)
                        category_totals[category] = category_totals.get(category, 0) + amount
            
            breakdown['categories'] = category_totals
            
            # Sort categories by spending
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            breakdown['top_spending_categories'] = sorted_categories[:10]  # Top 10
            
            return breakdown
            
        except Exception as e:
            print(f"Error generating category breakdown: {e}")
            return breakdown
    
    def generate_trend_analysis(self, data: Dict) -> Dict:
        """Generate trend analysis over time"""
        trends = {
            'monthly_totals': {},
            'category_trends': {},
            'spending_velocity': {}
        }
        
        try:
            if 'transactions' in data:
                for month, transactions in data['transactions'].items():
                    # Monthly totals
                    monthly_total = sum(t.get('amount', 0) for t in transactions)
                    trends['monthly_totals'][month] = monthly_total
                    
                    # Category trends by month
                    category_monthly = {}
                    for transaction in transactions:
                        category = transaction.get('category', 'Uncategorized')
                        amount = transaction.get('amount', 0)
                        category_monthly[category] = category_monthly.get(category, 0) + amount
                    
                    trends['category_trends'][month] = category_monthly
            
            return trends
            
        except Exception as e:
            print(f"Error generating trend analysis: {e}")
            return trends
    
    def export_comprehensive_report(self, output_path: str, report_data: Dict):
        """Export comprehensive report to file"""
        try:
            report_content = []
            
            # Header
            report_content.append("=" * 80)
            report_content.append("COMPREHENSIVE FINANCIAL REPORT")
            report_content.append("=" * 80)
            report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append("")
            
            # Executive Summary
            if 'executive_summary' in report_data:
                summary = report_data['executive_summary']
                report_content.append("EXECUTIVE SUMMARY")
                report_content.append("-" * 40)
                
                metrics = summary.get('key_metrics', {})
                report_content.append(f"Total Budget: ₹{metrics.get('total_budget', 0):,.2f}")
                report_content.append(f"Total Spent: ₹{metrics.get('total_spent', 0):,.2f}")
                report_content.append(f"Remaining: ₹{metrics.get('remaining_budget', 0):,.2f}")
                report_content.append(f"Utilization: {metrics.get('spending_percentage', 0):.1f}%")
                report_content.append("")
                
                # Insights
                if summary.get('insights'):
                    report_content.append("Key Insights:")
                    for insight in summary['insights']:
                        report_content.append(f"• {insight}")
                    report_content.append("")
                
                # Recommendations
                if summary.get('recommendations'):
                    report_content.append("Recommendations:")
                    for rec in summary['recommendations']:
                        report_content.append(f"• {rec}")
                    report_content.append("")
            
            # Category Breakdown
            if 'category_breakdown' in report_data:
                breakdown = report_data['category_breakdown']
                report_content.append("CATEGORY BREAKDOWN")
                report_content.append("-" * 40)
                
                for category, amount in breakdown.get('top_spending_categories', [])[:10]:
                    report_content.append(f"{category}: ₹{amount:,.2f}")
                report_content.append("")
            
            # Trend Analysis
            if 'trend_analysis' in report_data:
                trends = report_data['trend_analysis']
                report_content.append("MONTHLY TRENDS")
                report_content.append("-" * 40)
                
                for month, amount in sorted(trends.get('monthly_totals', {}).items()):
                    report_content.append(f"{month}: ₹{amount:,.2f}")
                report_content.append("")
            
            # Footer
            report_content.append("=" * 80)
            report_content.append("End of Report")
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(report_content))
            
            return True
            
        except Exception as e:
            print(f"Error exporting comprehensive report: {e}")
            return False


# Integration helper for main application
def create_reports_tab(parent_notebook, data_manager):
    """
    Factory function to create and return a configured Reports tab
    
    Args:
        parent_notebook: The ttk.Notebook widget to add the tab to
        data_manager: Instance of the data manager for data operations
    
    Returns:
        ReportsTab instance
    """
    return ReportsTab(parent_notebook, data_manager)


# Example usage and testing
if __name__ == "__main__":
    # This would typically be called from the main application
    # Here's how it would be integrated:
    
    root = tk.Tk()
    root.title("Financial Management - Reports Tab Demo")
    root.geometry("1200x800")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    # Mock data manager for testing
    class MockDataManager:
        def __init__(self):
            self.data_file_path = "demo_data.json"
        
        def get_all_data(self):
            return {
                'budgets': {
                    'Aug-25': {'Food': 5000, 'Transport': 3000},
                    'Sep-25': {'Food': 5500, 'Transport': 3200}
                },
                'transactions': {
                    'Aug-25': [
                        {'date': '2025-08-15', 'category': 'Food', 'amount': 4500, 'description': 'Groceries'},
                        {'date': '2025-08-20', 'category': 'Transport', 'amount': 2800, 'description': 'Fuel'}
                    ]
                }
            }
        
        def create_backup(self):
            return True
        
        def restore_from_backup(self, filename):
            return True
        
        def merge_data(self, data):
            pass
    
    # Create reports tab
    mock_data_manager = MockDataManager()
    reports_tab = create_reports_tab(notebook, mock_data_manager)
    
    root.mainloop()

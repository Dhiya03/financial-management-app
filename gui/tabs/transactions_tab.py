"""
Transactions tab for comprehensive transaction management
Implements User Story 2: Complete Transaction Lifecycle Management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import csv

from managers.transaction_manager import TransactionManager
from managers.category_manager import CategoryManager
from utils.formatters import format_currency, format_date
from utils.validators import validate_amount, validate_date

class TransactionsTab:
    """Complete transaction management with import and auto-categorization"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.transaction_manager = TransactionManager()
        self.category_manager = CategoryManager()
        
        # Search and filter variables
        self.search_var = tk.StringVar()
        self.category_filter_var = tk.StringVar(value="All")
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.source_filter_var = tk.StringVar(value="All")
        self.amount_min_var = tk.StringVar()
        self.amount_max_var = tk.StringVar()
        
        # Track selected items
        self.selected_transactions = []
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup comprehensive transaction UI"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Action buttons bar
        self.setup_action_bar(main_container)
        
        # Search and filters section
        self.setup_filters(main_container)
        
        # Uncategorized alert
        self.alert_frame = ttk.Frame(main_container)
        self.alert_frame.pack(fill='x', pady=(10, 5))
        
        # Transaction statistics
        self.setup_statistics(main_container)
        
        # Transactions table
        self.setup_transaction_table(main_container)
        
        # Bulk operations bar
        self.setup_bulk_operations(main_container)
    
    def setup_action_bar(self, parent):
        """Setup main action buttons"""
        action_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        action_frame.pack(fill='x', pady=(0, 10))
        
        # Primary actions
        primary_frame = ttk.Frame(action_frame)
        primary_frame.pack(side='left')
        
        ttk.Button(primary_frame, text="➕ Add Transaction", 
                  command=self.add_transaction).pack(side='left', padx=2)
        ttk.Button(primary_frame, text="📥 Import CSV/Excel", 
                  command=self.import_transactions).pack(side='left', padx=2)
        ttk.Button(primary_frame, text="📤 Export", 
                  command=self.export_transactions).pack(side='left', padx=2)
        
        # Separator
        ttk.Separator(action_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Secondary actions
        secondary_frame = ttk.Frame(action_frame)
        secondary_frame.pack(side='left')
        
        ttk.Button(secondary_frame, text="🔄 Auto-Categorize All", 
                  command=self.auto_categorize_all).pack(side='left', padx=2)
        ttk.Button(secondary_frame, text="🗑️ Delete Selected", 
                  command=self.delete_selected).pack(side='left', padx=2)
    
    def setup_filters(self, parent):
        """Setup advanced search and filter controls"""
        filter_frame = ttk.LabelFrame(parent, text="Search & Filters", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1: Search and category filter
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill='x', pady=2)
        
        ttk.Label(row1, text="Search:").pack(side='left')
        search_entry = ttk.Entry(row1, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(5, 20))
        search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Label(row1, text="Category:").pack(side='left')
        categories = ["All", "Uncategorized"] + self.category_manager.get_flat_category_list()
        category_combo = ttk.Combobox(row1, textvariable=self.category_filter_var, 
                                     values=categories, width=20, state='readonly')
        category_combo.pack(side='left', padx=(5, 20))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        ttk.Label(row1, text="Source:").pack(side='left')
        source_combo = ttk.Combobox(row1, textvariable=self.source_filter_var,
                                   values=["All", "Manual", "Imported", "Auto-categorized"],
                                   width=15, state='readonly')
        source_combo.pack(side='left', padx=(5, 0))
        source_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Row 2: Date and amount filters
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill='x', pady=2)
        
        ttk.Label(row2, text="Date From:").pack(side='left')
        date_from = ttk.Entry(row2, textvariable=self.date_from_var, width=12)
        date_from.pack(side='left', padx=(5, 10))
        date_from.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Label(row2, text="To:").pack(side='left')
        date_to = ttk.Entry(row2, textvariable=self.date_to_var, width=12)
        date_to.pack(side='left', padx=(5, 20))
        date_to.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Label(row2, text="Amount Min:").pack(side='left')
        amount_min = ttk.Entry(row2, textvariable=self.amount_min_var, width=10)
        amount_min.pack(side='left', padx=(5, 10))
        amount_min.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        ttk.Label(row2, text="Max:").pack(side='left')
        amount_max = ttk.Entry(row2, textvariable=self.amount_max_var, width=10)
        amount_max.pack(side='left', padx=(5, 20))
        amount_max.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Clear filters button
        ttk.Button(row2, text="Clear Filters", 
                  command=self.clear_filters).pack(side='left', padx=10)
    
    def setup_statistics(self, parent):
        """Setup transaction statistics display"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        # Statistics labels
        self.stats_labels = {
            'total': ttk.Label(stats_frame, text="Total: 0 transactions"),
            'amount': ttk.Label(stats_frame, text="Sum: ₹0"),
            'filtered': ttk.Label(stats_frame, text="Showing: 0 transactions"),
            'uncategorized': ttk.Label(stats_frame, text="Uncategorized: 0", foreground='orange')
        }
        
        for label in self.stats_labels.values():
            label.pack(side='left', padx=15)
    
    def setup_transaction_table(self, parent):
        """Setup transaction table with sorting and selection"""
        table_frame = ttk.LabelFrame(parent, text="Transactions", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview with columns
        columns = ('Date', 'Category', 'Amount', 'Description', 'Source', 'ID')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                selectmode='extended', height=15)
        
        # Configure columns
        column_config = {
            'Date': {'width': 100, 'anchor': 'center'},
            'Category': {'width': 150, 'anchor': 'w'},
            'Amount': {'width': 100, 'anchor': 'e'},
            'Description': {'width': 250, 'anchor': 'w'},
            'Source': {'width': 100, 'anchor': 'center'},
            'ID': {'width': 0, 'stretch': False}  # Hidden column
        }
        
        for col in columns:
            config = column_config.get(col, {})
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, **config)
        
        # Hide ID column
        self.tree['displaycolumns'] = columns[:-1]
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.edit_transaction)
        self.tree.bind('<Delete>', lambda e: self.delete_selected())
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        
        # Context menu
        self.setup_context_menu()
        
        # Configure tags for styling
        self.tree.tag_configure('uncategorized', background='#fff3cd')
        self.tree.tag_configure('imported', foreground='blue')
        self.tree.tag_configure('auto_categorized', foreground='green')
    
    def setup_bulk_operations(self, parent):
        """Setup bulk operations bar"""
        bulk_frame = ttk.Frame(parent)
        bulk_frame.pack(fill='x', pady=(10, 0))
        
        self.selection_label = ttk.Label(bulk_frame, text="No transactions selected")
        self.selection_label.pack(side='left')
        
        # Bulk operation buttons (initially disabled)
        self.bulk_buttons = []
        
        btn = ttk.Button(bulk_frame, text="Categorize Selected", 
                        command=self.categorize_selected, state='disabled')
        btn.pack(side='right', padx=2)
        self.bulk_buttons.append(btn)
        
        btn = ttk.Button(bulk_frame, text="Delete Selected", 
                        command=self.delete_selected, state='disabled')
        btn.pack(side='right', padx=2)
        self.bulk_buttons.append(btn)
        
        btn = ttk.Button(bulk_frame, text="Export Selected", 
                        command=self.export_selected, state='disabled')
        btn.pack(side='right', padx=2)
        self.bulk_buttons.append(btn)
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit Transaction", command=self.edit_transaction)
        self.context_menu.add_command(label="📝 Change Category", command=self.change_category)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Auto-Categorize", command=self.auto_categorize_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy", command=self.copy_transaction)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        if tk.sys.platform == 'darwin':  # macOS
            self.tree.bind("<Button-2>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            # Select item under cursor if not already selected
            item = self.tree.identify_row(event.y)
            if item and item not in self.tree.selection():
                self.tree.selection_set(item)
            
            if self.tree.selection():
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def refresh(self):
        """Refresh transaction list with filters"""
        self.apply_filters()
        self.update_uncategorized_alert()
    
    def apply_filters(self):
        """Apply all active filters to transaction list"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get all transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            
            # Apply filters
            filtered = self.filter_transactions(all_transactions)
            
            # Sort by date (newest first)
            filtered.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Update statistics
            self.update_statistics(all_transactions, filtered)
            
            # Add to table
            for transaction in filtered:
                self.insert_transaction_row(transaction)
                
        except Exception as e:
            logging.error(f"Error applying filters: {e}")
    
    def filter_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Filter transactions based on current filter settings"""
        filtered = []
        
        search_term = self.search_var.get().lower()
        category_filter = self.category_filter_var.get()
        source_filter = self.source_filter_var.get()
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()
        amount_min = self.amount_min_var.get()
        amount_max = self.amount_max_var.get()
        
        for transaction in transactions:
            # Search filter
            if search_term:
                searchable = f"{transaction.get('description', '')} {transaction.get('category', '')}".lower()
                if search_term not in searchable:
                    continue
            
            # Category filter
            if category_filter == "Uncategorized":
                if transaction.get('category') and transaction.get('category') != 'Uncategorized':
                    continue
            elif category_filter != "All":
                if transaction.get('category') != category_filter:
                    continue
            
            # Source filter
            if source_filter != "All":
                source_map = {
                    "Manual": "manual",
                    "Imported": "imported", 
                    "Auto-categorized": "auto_categorized"
                }
                if transaction.get('source') != source_map.get(source_filter, '').lower():
                    continue
            
            # Date range filter
            trans_date = transaction.get('date', '')
            if date_from and trans_date < date_from:
                continue
            if date_to and trans_date > date_to:
                continue
            
            # Amount range filter
            amount = transaction.get('amount', 0)
            try:
                if amount_min and amount < float(amount_min):
                    continue
                if amount_max and amount > float(amount_max):
                    continue
            except ValueError:
                pass
            
            filtered.append(transaction)
        
        return filtered
    
    def insert_transaction_row(self, transaction: Dict):
        """Insert a transaction row into the table"""
        # Determine tags for styling
        tags = []
        if not transaction.get('category') or transaction.get('category') == 'Uncategorized':
            tags.append('uncategorized')
        if transaction.get('source') == 'imported':
            tags.append('imported')
        elif transaction.get('source') == 'auto_categorized':
            tags.append('auto_categorized')
        
        # Format values
        date = transaction.get('date', '')
        category = transaction.get('category', 'Uncategorized')
        amount = format_currency(transaction.get('amount', 0))
        description = transaction.get('description', '')
        source = transaction.get('source', 'manual').title()
        trans_id = transaction.get('id', '')
        
        # Insert row
        self.tree.insert('', 'end', values=(
            date, category, amount, description, source, trans_id
        ), tags=tags)
    
    def update_statistics(self, all_transactions: List[Dict], filtered: List[Dict]):
        """Update transaction statistics display"""
        # Count uncategorized
        uncategorized = sum(1 for t in all_transactions 
                          if not t.get('category') or t.get('category') == 'Uncategorized')
        
        # Calculate sums
        total_amount = sum(t.get('amount', 0) for t in all_transactions)
        filtered_amount = sum(t.get('amount', 0) for t in filtered)
        
        # Update labels
        self.stats_labels['total'].config(text=f"Total: {len(all_transactions)} transactions")
        self.stats_labels['amount'].config(text=f"Sum: {format_currency(total_amount)}")
        self.stats_labels['filtered'].config(text=f"Showing: {len(filtered)} transactions")
        self.stats_labels['uncategorized'].config(text=f"Uncategorized: {uncategorized}")
    
    def update_uncategorized_alert(self):
        """Update alert for uncategorized transactions"""
        # Clear existing alerts
        for widget in self.alert_frame.winfo_children():
            widget.destroy()
        
        # Count uncategorized
        all_transactions = self.transaction_manager.get_all_transactions()
        uncategorized = [t for t in all_transactions 
                        if not t.get('category') or t.get('category') == 'Uncategorized']
        
        if uncategorized:
            alert_container = ttk.Frame(self.alert_frame)
            alert_container.pack(fill='x')
            
            alert_label = ttk.Label(alert_container,
                                  text=f"⚠️ {len(uncategorized)} uncategorized transactions need attention",
                                  foreground='orange', font=('Arial', 10, 'bold'))
            alert_label.pack(side='left')
            
            ttk.Button(alert_container, text="Auto-Categorize Now",
                      command=self.auto_categorize_uncategorized).pack(side='left', padx=20)
            
            ttk.Button(alert_container, text="Show Only Uncategorized",
                      command=self.show_uncategorized).pack(side='left')
    
    def on_selection_change(self, event=None):
        """Handle selection change in tree"""
        selection = self.tree.selection()
        count = len(selection)
        
        if count == 0:
            self.selection_label.config(text="No transactions selected")
            for btn in self.bulk_buttons:
                btn.config(state='disabled')
        elif count == 1:
            self.selection_label.config(text="1 transaction selected")
            for btn in self.bulk_buttons:
                btn.config(state='normal')
        else:
            self.selection_label.config(text=f"{count} transactions selected")
            for btn in self.bulk_buttons:
                btn.config(state='normal')
    
    def sort_by_column(self, column):
        """Sort treeview by column"""
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Determine sort order
        reverse = False
        if hasattr(self, '_last_sort_column') and self._last_sort_column == column:
            reverse = not getattr(self, '_last_sort_reverse', False)
        
        # Sort items
        if column == 'Amount':
            # Special handling for currency amounts
            items.sort(key=lambda x: float(x[0].replace('₹', '').replace(',', '') or 0), reverse=reverse)
        else:
            items.sort(reverse=reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Save sort state
        self._last_sort_column = column
        self._last_sort_reverse = reverse
    
    # Action methods
    def add_transaction(self):
        """Open add transaction dialog"""
        from gui.dialogs.transaction_dialog import TransactionDialog
        TransactionDialog(self.frame, callback=self.refresh)
    
    def edit_transaction(self, event=None):
        """Edit selected transaction"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            trans_id = values[5]  # ID is in hidden column
            
            from gui.dialogs.transaction_dialog import TransactionDialog
            TransactionDialog(self.frame, transaction_id=trans_id, callback=self.refresh)
    
    def delete_selected(self):
        """Delete selected transactions"""
        selection = self.tree.selection()
        if not selection:
            return
        
        count = len(selection)
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete {count} selected transaction(s)?"):
            deleted = 0
            for item in selection:
                values = self.tree.item(item, 'values')
                trans_id = values[5]
                success, _ = self.transaction_manager.delete_transaction(trans_id)
                if success:
                    deleted += 1
            
            if deleted > 0:
                messagebox.showinfo("Success", f"Deleted {deleted} transaction(s)")
                self.refresh()
    
    def import_transactions(self):
        """Import transactions from CSV/Excel"""
        file_path = filedialog.askopenfilename(
            title="Select file to import",
            filetypes=[
                ("Supported files", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Show import preview dialog
            ImportPreviewDialog(self.frame, file_path, callback=self.refresh)
    
    def export_transactions(self):
        """Export all transactions"""
        file_path = filedialog.asksaveasfilename(
            title="Export transactions",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(self.transaction_manager.get_all_transactions(), file_path)
    
    def export_selected(self):
        """Export selected transactions"""
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_transactions = []
        for item in selection:
            values = self.tree.item(item, 'values')
            trans_id = values[5]
            # Find transaction by ID
            for trans in self.transaction_manager.get_all_transactions():
                if trans.get('id') == trans_id:
                    selected_transactions.append(trans)
                    break
        
        if selected_transactions:
            file_path = filedialog.asksaveasfilename(
                title="Export selected transactions",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            
            if file_path:
                self.perform_export(selected_transactions, file_path)
    
    def perform_export(self, transactions: List[Dict], file_path: str):
        """Perform the actual export"""
        try:
            if file_path.endswith('.xlsx'):
                # Excel export (requires pandas)
                try:
                    import pandas as pd
                    df = pd.DataFrame(transactions)
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", f"Exported {len(transactions)} transactions to Excel")
                except ImportError:
                    messagebox.showerror("Error", "pandas/openpyxl required for Excel export")
            else:
                # CSV export
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    if transactions:
                        writer = csv.DictWriter(file, fieldnames=transactions[0].keys())
                        writer.writeheader()
                        writer.writerows(transactions)
                messagebox.showinfo("Success", f"Exported {len(transactions)} transactions to CSV")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def auto_categorize_all(self):
        """Auto-categorize all transactions"""
        if messagebox.askyesno("Auto-Categorize All", 
                              "Auto-categorize ALL transactions based on description?"):
            self.perform_auto_categorization()
    
    def auto_categorize_uncategorized(self):
        """Auto-categorize only uncategorized transactions"""
        self.perform_auto_categorization(uncategorized_only=True)
    
    def auto_categorize_selected(self):
        """Auto-categorize selected transactions"""
        selection = self.tree.selection()
        if selection:
            self.perform_auto_categorization(selection=selection)
    
    def perform_auto_categorization(self, uncategorized_only=False, selection=None):
        """Perform auto-categorization"""
        try:
            categorized = 0
            total = 0
            
            from managers.data_manager import data_manager
            
            if selection:
                # Categorize selected transactions
                for item in selection:
                    values = self.tree.item(item, 'values')
                    trans_id = values[5]
                    description = values[3]
                    
                    suggested = self.category_manager.auto_categorize_transaction(description)
                    if suggested:
                        self.transaction_manager.update_transaction(
                            trans_id, {'category': suggested, 'source': 'auto_categorized'}
                        )
                        categorized += 1
                    total += 1
            else:
                # Categorize all or uncategorized
                for month_transactions in self.app_data.transactions.values():
                    for transaction in month_transactions:
                        if uncategorized_only:
                            if transaction.get('category') and transaction.get('category') != 'Uncategorized':
                                continue
                        
                        description = transaction.get('description', '')
                        suggested = self.category_manager.auto_categorize_transaction(description)
                        
                        if suggested and suggested != transaction.get('category'):
                            transaction['category'] = suggested
                            transaction['source'] = 'auto_categorized'
                            categorized += 1
                        total += 1
            
            if categorized > 0:
                data_manager.save()
                messagebox.showinfo("Auto-Categorization", 
                                  f"Categorized {categorized} out of {total} transactions")
                self.refresh()
            else:
                messagebox.showinfo("Auto-Categorization", 
                                  "No transactions could be auto-categorized")
                
        except Exception as e:
            messagebox.showerror("Error", f"Auto-categorization failed: {str(e)}")
    
    def categorize_selected(self):
        """Open dialog to categorize selected transactions"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Create category selection dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title("Categorize Transactions")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text=f"Select category for {len(selection)} transaction(s):").pack(pady=10)
        
        category_var = tk.StringVar()
        categories = self.category_manager.get_flat_category_list()
        combo = ttk.Combobox(dialog, textvariable=category_var, values=categories, width=30)
        combo.pack(pady=10)
        
        def apply_category():
            category = category_var.get()
            if category:
                for item in selection:
                    values = self.tree.item(item, 'values')
                    trans_id = values[5]
                    self.transaction_manager.update_transaction(trans_id, {'category': category})
                
                dialog.destroy()
                self.refresh()
                messagebox.showinfo("Success", f"Categorized {len(selection)} transaction(s)")
        
        ttk.Button(dialog, text="Apply", command=apply_category).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def change_category(self):
        """Change category of selected transaction"""
        self.categorize_selected()
    
    def copy_transaction(self):
        """Copy selected transaction to clipboard"""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], 'values')
            text = f"Date: {values[0]}, Category: {values[1]}, Amount: {values[2]}, Description: {values[3]}"
            self.frame.clipboard_clear()
            self.frame.clipboard_append(text)
            messagebox.showinfo("Copied", "Transaction copied to clipboard")
    
    def show_uncategorized(self):
        """Filter to show only uncategorized transactions"""
        self.category_filter_var.set("Uncategorized")
        self.apply_filters()
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_var.set("")
        self.category_filter_var.set("All")
        self.source_filter_var.set("All")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.amount_min_var.set("")
        self.amount_max_var.set("")
        self.apply_filters()


class ImportPreviewDialog:
    """Dialog for previewing and configuring CSV/Excel import"""
    
    def __init__(self, parent, file_path, callback=None):
        self.parent = parent
        self.file_path = file_path
        self.callback = callback
        self.transaction_manager = TransactionManager()
        self.category_manager = CategoryManager()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import Preview")
        self.dialog.geometry("800x600")
        
        self.setup_ui()
        self.load_file()
    
    def setup_ui(self):
        """Setup import preview UI"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # File info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        self.file_label = ttk.Label(info_frame, text=f"File: {self.file_path}")
        self.file_label.pack(anchor='w')
        
        self.status_label = ttk.Label(info_frame, text="Loading file...")
        self.status_label.pack(anchor='w')
        
        # Column mapping
        mapping_frame = ttk.LabelFrame(main_frame, text="Column Mapping", padding=10)
        mapping_frame.pack(fill='x', pady=(0, 10))
        
        self.column_mappings = {}
        required_fields = ['Date', 'Amount', 'Description', 'Category (Optional)']
        
        for i, field in enumerate(required_fields):
            ttk.Label(mapping_frame, text=f"{field}:").grid(row=i, column=0, sticky='w', pady=2)
            combo = ttk.Combobox(mapping_frame, width=30)
            combo.grid(row=i, column=1, pady=2, padx=(10, 0))
            self.column_mappings[field.split()[0].lower()] = combo
        
        # Preview table
        preview_frame = ttk.LabelFrame(main_frame, text="Preview (First 10 rows)", padding=10)
        preview_frame.pack(fill='both', expand=True)
        
        self.preview_tree = ttk.Treeview(preview_frame, height=10)
        scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preview_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill='x', pady=(10, 0))
        
        self.auto_categorize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-categorize transactions",
                       variable=self.auto_categorize_var).pack(anchor='w')
        
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Skip duplicate transactions",
                       variable=self.skip_duplicates_var).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Import", command=self.perform_import).pack(side='right', padx=2)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='right', padx=2)
    
    def load_file(self):
        """Load and preview file"""
        try:
            if self.file_path.endswith('.csv'):
                self.load_csv()
            elif self.file_path.endswith(('.xlsx', '.xls')):
                self.load_excel()
            else:
                self.status_label.config(text="Unsupported file format", foreground='red')
        except Exception as e:
            self.status_label.config(text=f"Error loading file: {str(e)}", foreground='red')
    
    def load_csv(self):
        """Load CSV file"""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.headers = reader.fieldnames or []
            self.data = list(reader)[:10]  # Preview first 10 rows
            
        self.setup_preview()
    
    def load_excel(self):
        """Load Excel file"""
        try:
            import pandas as pd
            df = pd.read_excel(self.file_path, nrows=10)
            self.headers = list(df.columns)
            self.data = df.to_dict('records')
            self.setup_preview()
        except ImportError:
            self.status_label.config(text="pandas required for Excel import", foreground='red')
    
    def setup_preview(self):
        """Setup preview table with loaded data"""
        # Update column mappings
        for combo in self.column_mappings.values():
            combo['values'] = self.headers
        
        # Auto-detect columns
        self.auto_detect_columns()
        
        # Setup preview tree
        self.preview_tree['columns'] = self.headers
        self.preview_tree['show'] = 'headings'
        
        for header in self.headers:
            self.preview_tree.heading(header, text=header)
            self.preview_tree.column(header, width=100)
        
        # Add preview data
        for row in self.data:
            values = [row.get(h, '') for h in self.headers]
            self.preview_tree.insert('', 'end', values=values)
        
        self.status_label.config(text=f"Loaded {len(self.data)} rows for preview", foreground='green')
    
    def auto_detect_columns(self):
        """Auto-detect column mappings"""
        for field, combo in self.column_mappings.items():
            detected = None
            
            # Try to match column names
            for header in self.headers:
                header_lower = header.lower()
                
                if field == 'date':
                    if any(word in header_lower for word in ['date', 'time', 'when']):
                        detected = header
                        break
                elif field == 'amount':
                    if any(word in header_lower for word in ['amount', 'value', 'sum', 'total']):
                        detected = header
                        break
                elif field == 'description':
                    if any(word in header_lower for word in ['description', 'desc', 'memo', 'details']):
                        detected = header
                        break
                elif field == 'category':
                    if any(word in header_lower for word in ['category', 'cat', 'type']):
                        detected = header
                        break
            
            if detected:
                combo.set(detected)
    
    def perform_import(self):
        """Perform the actual import"""
        try:
            # Get column mappings
            date_col = self.column_mappings['date'].get()
            amount_col = self.column_mappings['amount'].get()
            desc_col = self.column_mappings['description'].get()
            cat_col = self.column_mappings.get('category', {}).get()
            
            if not date_col or not amount_col:
                messagebox.showerror("Mapping Error", "Date and Amount columns are required")
                return
            
            # Load full file
            if self.file_path.endswith('.csv'):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)
            else:
                import pandas as pd
                df = pd.read_excel(self.file_path)
                data = df.to_dict('records')
            
            # Import transactions
            imported = 0
            errors = []
            
            for i, row in enumerate(data, 1):
                try:
                    date = row.get(date_col, '')
                    amount = float(str(row.get(amount_col, 0)).replace('₹', '').replace(',', ''))
                    description = row.get(desc_col, '') if desc_col else ''
                    category = row.get(cat_col, '') if cat_col else ''
                    
                    # Auto-categorize if needed
                    if not category and self.auto_categorize_var.get():
                        category = self.category_manager.auto_categorize_transaction(description) or 'Uncategorized'
                    
                    # Add transaction
                    success, msg = self.transaction_manager.add_transaction(
                        date, category or 'Uncategorized', amount, description, 'imported'
                    )
                    
                    if success:
                        imported += 1
                    else:
                        errors.append(f"Row {i}: {msg}")
                        
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
            
            # Show results
            if imported > 0:
                msg = f"Successfully imported {imported} transactions"
                if errors:
                    msg += f"\n\n{len(errors)} errors occurred"
                messagebox.showinfo("Import Complete", msg)
                
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Import Failed", f"No transactions imported\n\nErrors:\n" + "\n".join(errors[:10]))
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Import failed: {str(e)}")

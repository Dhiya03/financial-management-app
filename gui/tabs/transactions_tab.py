"""
Transactions tab for transaction management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

from managers.transaction_manager import TransactionManager

class TransactionsTab:
    """Transactions tab for transaction management"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.transaction_manager = TransactionManager()
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup transactions tab UI"""
        # Action buttons
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(action_frame, text="Add Transaction", 
                  command=self.add_transaction).pack(side='left', padx=(0, 10))
        ttk.Button(action_frame, text="Import CSV", 
                  command=self.import_csv).pack(side='left', padx=(0, 10))
        ttk.Button(action_frame, text="Export CSV", 
                  command=self.export_csv).pack(side='left', padx=(0, 10))
        ttk.Button(action_frame, text="Auto-Categorize", 
                  command=self.auto_categorize).pack(side='left')
        
        # Search and filters
        filter_frame = ttk.Frame(self.frame)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(filter_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=(5, 20))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Label(filter_frame, text="Category:").pack(side='left')
        self.category_var = tk.StringVar()
        categories = ["All"] + self.transaction_manager.category_manager.get_flat_category_list()
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, values=categories)
        category_combo.pack(side='left', padx=(5, 0))
        category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        category_combo.set("All")
        
        # Transactions table
        table_frame = ttk.LabelFrame(self.frame, text="Transactions", padding=15)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('Date', 'Category', 'Amount', 'Description', 'Source')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Context menu
        self.setup_context_menu()
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit Transaction", command=self.edit_transaction)
        self.context_menu.add_command(label="Delete Transaction", command=self.delete_transaction)
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def refresh(self):
        """Refresh transaction list"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get all transactions
            all_transactions = self.transaction_manager.get_all_transactions()
            
            # Apply filters
            search_term = self.search_var.get().lower()
            category_filter = self.category_var.get()
            
            filtered_transactions = []
            for transaction in all_transactions:
                # Search filter
                if search_term:
                    if (search_term not in transaction.get('description', '').lower() and
                        search_term not in transaction.get('category', '').lower()):
                        continue
                
                # Category filter
                if category_filter and category_filter != "All":
                    if transaction.get('category') != category_filter:
                        continue
                
                filtered_transactions.append(transaction)
            
            # Sort by date (newest first)
            filtered_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Add to table
            for transaction in filtered_transactions:
                self.tree.insert('', 'end', values=(
                    transaction.get('date', ''),
                    transaction.get('category', ''),
                    f"₹{transaction.get('amount', 0):,.2f}",
                    transaction.get('description', ''),
                    transaction.get('source', '')
                ), tags=(transaction.get('id'),))
        
        except Exception as e:
            logging.error(f"Error refreshing transactions: {e}")
    
    def on_search(self, event=None):
        """Handle search input change"""
        self.refresh()
    
    def on_filter_change(self, event=None):
        """Handle filter change"""
        self.refresh()
    
    def add_transaction(self):
        """Open add transaction dialog"""
        from gui.dialogs.transaction_dialog import TransactionDialog
        TransactionDialog(self.frame, callback=self.refresh)
    
    def edit_transaction(self):
        """Edit selected transaction"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            transaction_id = self.tree.item(item, 'tags')[0]
            # Placeholder for edit dialog
            messagebox.showinfo("Edit", f"Edit transaction: {transaction_id}")
    
    def delete_transaction(self):
        """Delete selected transaction"""
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Delete", "Are you sure you want to delete this transaction?"):
                item = selected[0]
                transaction_id = self.tree.item(item, 'tags')[0]
                success, message = self.transaction_manager.delete_transaction(transaction_id)
                if success:
                    messagebox.showinfo("Success", message)
                    self.refresh()
                else:
                    messagebox.showerror("Error", message)
    
    def import_csv(self):
        """Import transactions from CSV"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            success, message, count = self.transaction_manager.import_from_csv(file_path)
            
            if success:
                messagebox.showinfo("Import Successful", message)
                self.refresh()
            else:
                messagebox.showerror("Import Failed", message)
    
    def export_csv(self):
        """Export transactions to CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Save transactions as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import csv
                transactions = self.transaction_manager.get_all_transactions()
                
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Category', 'Amount', 'Description', 'Source'])
                    
                    for transaction in transactions:
                        writer.writerow([
                            transaction.get('date', ''),
                            transaction.get('category', ''),
                            transaction.get('amount', 0),
                            transaction.get('description', ''),
                            transaction.get('source', '')
                        ])
                
                messagebox.showinfo("Export Successful", f"Exported {len(transactions)} transactions")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export: {str(e)}")
    
    def auto_categorize(self):
        """Auto-categorize uncategorized transactions"""
        try:
            # Find uncategorized transactions
            uncategorized_count = 0
            categorized_count = 0
            
            from managers.data_manager import data_manager
            app_data = data_manager.get_data()
            
            for month, transactions in app_data.transactions.items():
                for transaction in transactions:
                    if not transaction.get('category') or transaction.get('category') == 'Uncategorized':
                        uncategorized_count += 1
                        
                        description = transaction.get('description', '')
                        suggested_category = self.transaction_manager.category_manager.auto_categorize_transaction(description)
                        
                        if suggested_category:
                            transaction['category'] = suggested_category
                            transaction['source'] = 'auto_categorized'
                            categorized_count += 1
            
            if categorized_count > 0:
                data_manager.save()
                messagebox.showinfo("Auto-Categorization", 
                                   f"Categorized {categorized_count} out of {uncategorized_count} transactions")
                self.refresh()
            else:
                messagebox.showinfo("Auto-Categorization", "No transactions to auto-categorize")
                
        except Exception as e:
            messagebox.showerror("Error", f"Auto-categorization failed: {str(e)}")

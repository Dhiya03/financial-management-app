"""
Dialog for adding and editing transactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from managers.transaction_manager import TransactionManager
from managers.category_manager import CategoryManager

class TransactionDialog:
    """Dialog for adding/editing transactions"""
    
    def __init__(self, parent, transaction_id=None, callback=None):
        self.parent = parent
        self.transaction_id = transaction_id
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Transaction" if not transaction_id else "Edit Transaction")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.transaction_manager = TransactionManager()
        self.category_manager = CategoryManager()
        
        self.setup_ui()
        self.center_dialog()
        
        if transaction_id:
            self.load_transaction(transaction_id)
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Date field
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=30)
        date_entry.grid(row=0, column=1, pady=5, sticky='ew')
        
        # Category field
        ttk.Label(main_frame, text="Category:").grid(row=1, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        categories = self.category_manager.get_flat_category_list()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                     values=categories, width=27)
        category_combo.grid(row=1, column=1, pady=5, sticky='ew')
        
        # Amount field
        ttk.Label(main_frame, text="Amount:").grid(row=2, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, width=30)
        amount_entry.grid(row=2, column=1, pady=5, sticky='ew')
        
        # Description field
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky='w', pady=5)
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(main_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=3, column=1, pady=5, sticky='ew')
        description_entry.bind('<KeyRelease>', self.on_description_change)
        
        # Auto-categorize suggestion
        self.suggestion_label = ttk.Label(main_frame, text="", foreground='blue')
        self.suggestion_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Quick amount buttons
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Amounts", padding=10)
        quick_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')
        
        quick_amounts = [500, 1000, 2000, 5000, 10000, 15000]
        for i, amount in enumerate(quick_amounts):
            ttk.Button(quick_frame, text=f"₹{amount}", width=8,
                      command=lambda a=amount: self.amount_var.set(str(a))).grid(
                      row=i//3, column=i%3, padx=2, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky='ew')
        
        ttk.Button(button_frame, text="Save", command=self.save_transaction).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='right')
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
    
    def on_description_change(self, event=None):
        """Auto-suggest category based on description"""
        description = self.description_var.get()
        if len(description) > 3:
            suggested = self.category_manager.auto_categorize_transaction(description)
            if suggested:
                self.suggestion_label.config(text=f"Suggested: {suggested}")
                if not self.category_var.get():
                    self.category_var.set(suggested)
            else:
                self.suggestion_label.config(text="")
    
    def save_transaction(self):
        """Save the transaction"""
        try:
            # Validate inputs
            date = self.date_var.get()
            category = self.category_var.get()
            amount_str = self.amount_var.get()
            description = self.description_var.get()
            
            if not date or not category or not amount_str:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a valid number")
                return
            
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than zero")
                return
            
            # Add or update transaction
            if self.transaction_id:
                # Update existing transaction
                updates = {
                    'date': date,
                    'category': category,
                    'amount': amount,
                    'description': description
                }
                success, message = self.transaction_manager.update_transaction(
                    self.transaction_id, updates
                )
            else:
                # Add new transaction
                success, message = self.transaction_manager.add_transaction(
                    date, category, amount, description, "manual"
                )
            
            if success:
                messagebox.showinfo("Success", message)
                self.dialog.destroy()
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Error", message)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transaction: {str(e)}")
    
    def load_transaction(self, transaction_id):
        """Load transaction data for editing"""
        # Placeholder for loading transaction data
        pass
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")

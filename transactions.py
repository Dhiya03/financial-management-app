import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime

class TransactionsTab(ttk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Transactions", font=("Arial", 16)).pack(pady=10)
        ttk.Button(self, text="Add Transaction", command=self.add_transaction_popup).pack()
        ttk.Button(self, text="Import CSV", command=self.import_csv).pack()

    def add_transaction_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add Transaction")
        tk.Label(popup, text="Date (YYYY-MM-DD)").grid(row=0,column=0)
        tk.Label(popup, text="Category").grid(row=1,column=0)
        tk.Label(popup, text="Amount").grid(row=2,column=0)
        date_var = tk.StringVar()
        category_var = tk.StringVar()
        amount_var = tk.StringVar()
        tk.Entry(popup, textvariable=date_var).grid(row=0,column=1)
        tk.Entry(popup, textvariable=category_var).grid(row=1,column=1)
        tk.Entry(popup, textvariable=amount_var).grid(row=2,column=1)
        def save_transaction():
            self.data["transactions"].append({
                "date": date_var.get(),
                "category": category_var.get(),
                "amount": float(amount_var.get())
            })
            messagebox.showinfo("Saved","Transaction Added")
            popup.destroy()
        tk.Button(popup, text="Save", command=save_transaction).grid(row=3,column=1)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if not file_path: return
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    self.data["transactions"].append({
                        "date": row["date"],
                        "category": row["category"],
                        "amount": float(row["amount"])
                    })
                except:
                    continue
        messagebox.showinfo("Imported", "CSV transactions imported successfully.")

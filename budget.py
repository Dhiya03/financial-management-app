import tkinter as tk
from tkinter import ttk, messagebox

class BudgetTab(ttk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Budget Planning", font=("Arial", 16)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("category", "budget"), show="headings")
        self.tree.heading("category", text="Category")
        self.tree.heading("budget", text="Planned Budget")
        self.tree.pack(pady=10)
        ttk.Button(self, text="Add/Update Budget", command=self.add_budget_popup).pack()
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for cat, amt in self.data.get("budgets", {}).items():
            self.tree.insert("", "end", values=(cat, amt))

    def add_budget_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add/Update Budget")
        tk.Label(popup, text="Category").grid(row=0,column=0)
        tk.Label(popup, text="Amount").grid(row=1,column=0)
        cat_var = tk.StringVar()
        amt_var = tk.StringVar()
        tk.Entry(popup, textvariable=cat_var).grid(row=0,column=1)
        tk.Entry(popup, textvariable=amt_var).grid(row=1,column=1)
        def save_budget():
            self.data["budgets"][cat_var.get()] = float(amt_var.get())
            self.refresh_tree()
            popup.destroy()
        tk.Button(popup, text="Save", command=save_budget).grid(row=2,column=1)

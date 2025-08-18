# main.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import pandas as pd

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from budget import BudgetManager
from transactions import TransactionManager
from categories import CategoryAnalysis
from scenarios import ScenarioManager
from gui_helpers import populate_tree, create_bar_chart, alert_if_low, prompt_top_level

DATA_FILE = "data.json"

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management App")
        self.root.geometry("1000x600")

        # Managers
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        self.category_analysis = CategoryAnalysis()
        self.scenario_manager = ScenarioManager()

        self.data = self.load_data()

        # Tabs
        self.tab_control = ttk.Notebook(root)
        self.create_dashboard_tab()
        self.create_transactions_tab()
        self.create_budget_tab()
        self.create_category_tab()
        self.create_scenario_tab()
        self.create_reports_tab()
        self.tab_control.pack(expand=1, fill="both")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {"budgets": {}, "transactions": {}, "scenarios": {}}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # ---------------- Dashboard ----------------
    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        ttk.Label(self.dashboard_tab, text="Dashboard - Overview").pack()

        if MATPLOTLIB_AVAILABLE:
            month_labels = list(self.data.get("transactions", {}).keys())
            spent = [sum(t['amount'] for t in self.data["transactions"][month]) for month in month_labels]
            budget = [self.data["budgets"].get(month, 0) for month in month_labels]
            create_bar_chart(self.dashboard_tab, "Monthly Spending vs Budget", month_labels,
                             {"Spent": spent, "Budget": budget})
        else:
            ttk.Label(self.dashboard_tab, text="Matplotlib not installed. Graphs disabled.").pack()

    # ---------------- Transactions ----------------
    def create_transactions_tab(self):
        self.transactions_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transactions_tab, text="Transactions")

        cols = ["Date", "Category", "Amount", "Description"]
        self.trans_tree = ttk.Treeview(self.transactions_tab, columns=cols, show="headings")
        for col in cols:
            self.trans_tree.heading(col, text=col)
        self.trans_tree.pack(expand=1, fill="both")

        ttk.Button(self.transactions_tab, text="Add Transaction", command=self.add_transaction).pack()

        self.refresh_transactions()

    def add_transaction(self):
        def callback(values):
            month = values["Date"][:7]
            self.data.setdefault("transactions", {}).setdefault(month, []).append({
                "date": values["Date"],
                "category": values["Category"],
                "amount": float(values["Amount"]),
                "description": values["Description"]
            })
            self.refresh_transactions()
        prompt_top_level(self.root, "Add Transaction", ["Date", "Category", "Amount", "Description"], callback)

    def refresh_transactions(self):
        all_trans = []
        for month, tlist in self.data.get("transactions", {}).items():
            all_trans.extend(tlist)
        populate_tree(self.trans_tree, all_trans, ["date", "category", "amount", "description"])

    # ---------------- Budget ----------------
    def create_budget_tab(self):
        self.budget_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.budget_tab, text="Budget Planning")

        cols = ["Month", "Budget", "Spent", "Remaining"]
        self.budget_tree = ttk.Treeview(self.budget_tab, columns=cols, show="headings")
        for col in cols:
            self.budget_tree.heading(col, text=col)
        self.budget_tree.pack(expand=1, fill="both")

        ttk.Button(self.budget_tab, text="Add/Update Budget", command=self.add_budget).pack()

        self.refresh_budget()

    def add_budget(self):
        def callback(values):
            month = values["Month"]
            self.data.setdefault("budgets", {})[month] = float(values["Budget"])
            self.refresh_budget()
        prompt_top_level(self.root, "Add Budget", ["Month", "Budget"], callback)

    def refresh_budget(self):
        all_months = set(list(self.data.get("budgets", {}).keys()) + list(self.data.get("transactions", {}).keys()))
        budget_list = []
        for month in all_months:
            budget = self.data.get("budgets", {}).get(month, 0)
            spent = sum(t['amount'] for t in self.data.get("transactions", {}).get(month, []))
            remaining = budget - spent
            budget_list.append({"Month": month, "Budget": budget, "Spent": spent, "Remaining": remaining})
        populate_tree(self.budget_tree, budget_list, ["Month", "Budget", "Spent", "Remaining"])
        alert_if_low(self.budget_tree, column=3, threshold=0.1)

    # ---------------- Category ----------------
    def create_category_tab(self):
        self.category_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.category_tab, text="Category Analysis")
        ttk.Label(self.category_tab, text="Category Analysis").pack()

        # Could integrate category_analysis module here for charts & analysis

    # ---------------- What-If Simulator ----------------
    def create_scenario_tab(self):
        self.scenario_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.scenario_tab, text="What-If Simulator")

        ttk.Label(self.scenario_tab, text="Adjust Budget / Expenses to see impact").pack()
        ttk.Button(self.scenario_tab, text="Run Scenario", command=self.run_scenario).pack()

    def run_scenario(self):
        def callback(values):
            # Example: temporarily adjust budgets and show new remaining
            month = values["Month"]
            delta = float(values["Delta"])
            self.data.setdefault("budgets", {}).setdefault(month, 0)
            self.data["budgets"][month] += delta
            messagebox.showinfo("Scenario Applied", f"Budget for {month} adjusted by {delta}")
            self.refresh_budget()
        prompt_top_level(self.root, "Run What-If Scenario", ["Month", "Delta"], callback)

    # ---------------- Reports ----------------
    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.reports_tab, text="Reports")
        ttk.Button(self.reports_tab, text="Export JSON", command=self.export_json).pack(pady=5)
        ttk.Button(self.reports_tab, text="Export Excel", command=self.export_excel).pack(pady=5)

    def export_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Export", "Exported JSON successfully!")

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if file_path:
            try:
                all_transactions = []
                for month, trans_list in self.data.get("transactions", {}).items():
                    for t in trans_list:
                        t_copy = t.copy()
                        t_copy["Month"] = month
                        all_transactions.append(t_copy)
                df = pd.DataFrame(all_transactions)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Export", "Exported Excel successfully!")
            except Exception as e:
                messagebox.showerror("Export", f"Failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.save_data)
    root.mainloop()

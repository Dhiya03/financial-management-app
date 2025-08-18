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

DATA_FILE = "data.json"

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management App")
        self.root.geometry("1000x600")

        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        self.category_analysis = CategoryAnalysis()
        self.scenario_manager = ScenarioManager()

        self.data = self.load_data()

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

    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        ttk.Label(self.dashboard_tab, text="Dashboard - Overview").pack()

        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(5,3))
            ax.set_title("Monthly Spending vs Budget")
            canvas = FigureCanvasTkAgg(fig, master=self.dashboard_tab)
            canvas.get_tk_widget().pack()
            canvas.draw()
        else:
            ttk.Label(self.dashboard_tab, text="Matplotlib not installed. Graphs disabled.").pack()

    def create_transactions_tab(self):
        self.transactions_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transactions_tab, text="Transactions")
        ttk.Label(self.transactions_tab, text="Transactions Tab").pack()

    def create_budget_tab(self):
        self.budget_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.budget_tab, text="Budget Planning")
        ttk.Label(self.budget_tab, text="Budget Planning Tab").pack()

    def create_category_tab(self):
        self.category_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.category_tab, text="Category Analysis")
        ttk.Label(self.category_tab, text="Category Analysis Tab").pack()

    def create_scenario_tab(self):
        self.scenario_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.scenario_tab, text="What-If Simulator")
        ttk.Label(self.scenario_tab, text="What-If Simulator Tab").pack()

    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.reports_tab, text="Reports")
        ttk.Button(self.reports_tab, text="Export JSON", command=self.export_json).pack()
        ttk.Button(self.reports_tab, text="Export Excel", command=self.export_excel).pack()

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

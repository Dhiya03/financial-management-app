import tkinter as tk
from gui.dashboard import DashboardTab
from gui.transactions import TransactionsTab
from gui.budget import BudgetTab
from gui.categories import CategoryAnalysisTab
from gui.scenarios import WhatIfTab
from persistence.storage import load_data, save_data

class FinancialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Management App")
        self.geometry("1000x700")
        self.data = load_data()
        self.create_tabs()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_tabs(self):
        from tkinter import ttk
        self.tab_control = ttk.Notebook(self)

        self.dashboard_tab = DashboardTab(self.tab_control, self.data)
        self.transactions_tab = TransactionsTab(self.tab_control, self.data)
        self.budget_tab = BudgetTab(self.tab_control, self.data)
        self.category_tab = CategoryAnalysisTab(self.tab_control, self.data)
        self.whatif_tab = WhatIfTab(self.tab_control, self.data)

        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.transactions_tab, text="Transactions")
        self.tab_control.add(self.budget_tab, text="Budget")
        self.tab_control.add(self.category_tab, text="Category Analysis")
        self.tab_control.add(self.whatif_tab, text="What-If Simulator")

        self.tab_control.pack(expand=1, fill="both")

    def on_exit(self):
        save_data(self.data)
        self.destroy()

if __name__ == "__main__":
    app = FinancialApp()
    app.mainloop()

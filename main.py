import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from budget import set_budget, get_monthly_budget
from transactions import add_transaction, import_transactions_from_csv, get_transactions
from category_analysis import plot_category_breakdown
from whatif_simulator import add_scenario, apply_scenario
from utils import format_currency, get_alert_color

class BudgetApp:
    def __init__(self, root):
        self.root = root
        root.title("Personal Budget Manager")
        self.current_year = 2025
        self.current_month = 8

        self.tab_control = ttk.Notebook(root)
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.transactions_tab = ttk.Frame(self.tab_control)
        self.budget_tab = ttk.Frame(self.tab_control)
        self.category_tab = ttk.Frame(self.tab_control)
        self.whatif_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.transactions_tab, text="Transactions")
        self.tab_control.add(self.budget_tab, text="Budget")
        self.tab_control.add(self.category_tab, text="Category Analysis")
        self.tab_control.add(self.whatif_tab, text="What-If Simulator")
        self.tab_control.pack(expand=1, fill="both")

        self.build_dashboard_tab()
        self.build_transactions_tab()
        self.build_budget_tab()
        self.build_category_tab()
        self.build_whatif_tab()
        self.refresh_dashboard()

    def build_dashboard_tab(self):
        frame = self.dashboard_tab
        # Month selector
        month_frame = tk.Frame(frame)
        month_frame.pack(pady=5)
        tk.Label(month_frame, text="Year:").pack(side="left")
        self.year_var = tk.IntVar(value=self.current_year)
        tk.Spinbox(month_frame, from_=2024, to=2025, textvariable=self.year_var, width=5, command=self.refresh_dashboard).pack(side="left")
        tk.Label(month_frame, text="Month:").pack(side="left")
        self.month_var = tk.IntVar(value=self.current_month)
        tk.Spinbox(month_frame, from_=1, to=12, textvariable=self.month_var, width=3, command=self.refresh_dashboard).pack(side="left")

        # Dashboard table
        self.tree = ttk.Treeview(frame, columns=("Budget", "Spent", "Remaining"), show="headings")
        for col in ("Budget", "Spent", "Remaining"):
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", pady=10)

    def refresh_dashboard(self):
        self.current_year = self.year_var.get()
        self.current_month = self.month_var.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        budgets = get_monthly_budget(self.current_year, self.current_month)
        transactions = get_transactions()
        month_key = f"{self.current_year}-{self.current_month:02d}"
        spent_per_category = {}
        for t in transactions.get(month_key, []):
            cat = t["category"]
            spent_per_category[cat] = spent_per_category.get(cat, 0) + t["amount"]

        categories = set(list(budgets.keys()) + list(spent_per_category.keys()))
        for cat in categories:
            budget = budgets.get(cat, 0)
            spent = spent_per_category.get(cat, 0)
            remaining = budget - spent
            color = get_alert_color(remaining, budget)
            self.tree.insert("", "end", values=(format_currency(budget), format_currency(spent), format_currency(remaining)), text=cat, tags=(color,))
        self.tree.tag_configure("red", background="#FFCCCC")
        self.tree.tag_configure("orange", background="#FFE0B2")
        self.tree.tag_configure("green", background="#CCFFCC")

    def build_transactions_tab(self):
        frame = self.transactions_tab
        tk.Label(frame, text="Add Transaction").pack()
        tk.Button(frame, text="Import CSV/Excel", command=self.import_csv).pack(pady=5)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if file_path:
            import_transactions_from_csv(file_path, self.current_year, self.current_month)
            messagebox.showinfo("Import", "Transactions imported!")
            self.refresh_dashboard()

    def build_budget_tab(self):
        tk.Label(self.budget_tab, text="Set monthly budgets").pack()

    def build_category_tab(self):
        tk.Button(self.category_tab, text="Plot Category Breakdown", command=lambda: plot_category_breakdown(self.current_year, self.current_month)).pack()

    def build_whatif_tab(self):
        tk.Label(self.whatif_tab, text="Add Scenario").pack()
        tk.Button(self.whatif_tab, text="Apply Example Scenario", command=self.apply_example_scenario).pack(pady=5)

    def apply_example_scenario(self):
        add_scenario("Extra Swiggy", [{"category": "Swiggy", "amount": 1000, "start": "2025-08", "end": "2025-08"}])
        apply_scenario(self.current_year, self.current_month, "Extra Swiggy")
        messagebox.showinfo("Scenario", "Scenario applied!")
        self.refresh_dashboard()

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

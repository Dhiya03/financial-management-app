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
ALERT_THRESHOLD = 0.1  # 10% remaining

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Management App")
        self.root.geometry("1100x650")

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

    # ------------------------- Data Persistence -------------------------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {"budgets": {}, "transactions": {}, "scenarios": {}}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # ------------------------- Dashboard Tab -------------------------
    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.dashboard_tab, text="Dashboard")

        ttk.Label(self.dashboard_tab, text="Dashboard - Overview", font=("Arial", 14, "bold")).pack(pady=5)

        self.dashboard_tree = ttk.Treeview(self.dashboard_tab, columns=("Spent","Budget","Remaining","Status"), show="headings")
        for col in ("Spent","Budget","Remaining","Status"):
            self.dashboard_tree.heading(col, text=col)
        self.dashboard_tree.pack(expand=True, fill="both", pady=10)

        self.update_dashboard_tree()

        if MATPLOTLIB_AVAILABLE:
            self.dashboard_fig, self.dashboard_ax = plt.subplots(figsize=(6,3))
            self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, master=self.dashboard_tab)
            self.dashboard_canvas.get_tk_widget().pack()
            self.update_dashboard_chart()
        else:
            ttk.Label(self.dashboard_tab, text="Matplotlib not installed. Graphs disabled.").pack()

    def update_dashboard_tree(self):
        for row in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(row)

        month_data = self.data.get("transactions", {})
        budgets = self.data.get("budgets", {})

        for category, budget_val in budgets.items():
            spent = sum(t["amount"] for month, trans in month_data.items() for t in trans if t.get("category")==category)
            remaining = budget_val - spent
            status = "On Track ✅" if remaining >= budget_val * -ALERT_THRESHOLD else "Overspent ⚠️"
            self.dashboard_tree.insert("", "end", values=(spent, budget_val, remaining, status))

    def update_dashboard_chart(self):
        self.dashboard_ax.clear()
        categories = list(self.data.get("budgets", {}).keys())
        spent = [sum(t["amount"] for month, trans in self.data.get("transactions", {}).items() for t in trans if t.get("category")==cat) for cat in categories]
        budgets = [self.data.get("budgets", {}).get(cat,0) for cat in categories]
        x = range(len(categories))
        self.dashboard_ax.bar(x, budgets, alpha=0.3, label="Budget")
        self.dashboard_ax.bar(x, spent, alpha=0.7, label="Spent")
        self.dashboard_ax.set_xticks(x)
        self.dashboard_ax.set_xticklabels(categories, rotation=45)
        self.dashboard_ax.legend()
        self.dashboard_ax.set_title("Category-wise Spending vs Budget")
        self.dashboard_canvas.draw()

    # ------------------------- Transactions Tab -------------------------
    def create_transactions_tab(self):
        self.transactions_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transactions_tab, text="Transactions")
        ttk.Label(self.transactions_tab, text="Transactions", font=("Arial",12,"bold")).pack(pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.transactions_tab)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Add Transaction", command=self.add_transaction).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Import CSV/Excel", command=self.import_transactions).pack(side="left", padx=5)

        # Treeview
        self.trans_tree = ttk.Treeview(self.transactions_tab, columns=("Date","Category","Amount","Notes"), show="headings")
        for col in ("Date","Category","Amount","Notes"):
            self.trans_tree.heading(col, text=col)
        self.trans_tree.pack(expand=True, fill="both", pady=10)
        self.update_transactions_tree()

    def add_transaction(self):
        def save_trans():
            t = {
                "date": date_var.get(),
                "category": cat_var.get(),
                "amount": float(amount_var.get()),
                "notes": notes_var.get()
            }
            month = t["date"][:7]  # YYYY-MM
            if month not in self.data["transactions"]:
                self.data["transactions"][month] = []
            self.data["transactions"][month].append(t)
            self.update_transactions_tree()
            self.update_dashboard_tree()
            self.update_dashboard_chart()
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add Transaction")
        tk.Label(top, text="Date (YYYY-MM-DD)").grid(row=0,column=0)
        tk.Label(top, text="Category").grid(row=1,column=0)
        tk.Label(top, text="Amount").grid(row=2,column=0)
        tk.Label(top, text="Notes").grid(row=3,column=0)

        date_var = tk.StringVar()
        cat_var = tk.StringVar()
        amount_var = tk.StringVar()
        notes_var = tk.StringVar()

        tk.Entry(top, textvariable=date_var).grid(row=0,column=1)
        tk.Entry(top, textvariable=cat_var).grid(row=1,column=1)
        tk.Entry(top, textvariable=amount_var).grid(row=2,column=1)
        tk.Entry(top, textvariable=notes_var).grid(row=3,column=1)

        ttk.Button(top, text="Save", command=save_trans).grid(row=4,column=0,columnspan=2,pady=5)

    def import_transactions(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV/Excel","*.csv *.xlsx")])
        if not file_path:
            return
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                month = str(row["date"])[:7]
                t = {"date": str(row["date"]), "category": row.get("category","Uncategorized"),
                     "amount": float(row.get("amount",0)), "notes": row.get("notes","")}
                if month not in self.data["transactions"]:
                    self.data["transactions"][month] = []
                self.data["transactions"][month].append(t)
            self.update_transactions_tree()
            self.update_dashboard_tree()
            self.update_dashboard_chart()
            messagebox.showinfo("Import","Transactions imported successfully!")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def update_transactions_tree(self):
        for row in self.trans_tree.get_children():
            self.trans_tree.delete(row)
        for month, trans_list in self.data.get("transactions", {}).items():
            for t in trans_list:
                self.trans_tree.insert("", "end", values=(t["date"], t["category"], t["amount"], t["notes"]))

    # ------------------------- Budget Tab -------------------------
    def create_budget_tab(self):
        self.budget_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.budget_tab, text="Budget Planning")
        ttk.Label(self.budget_tab, text="Budget Planning", font=("Arial",12,"bold")).pack(pady=5)

        # Treeview
        self.budget_tree = ttk.Treeview(self.budget_tab, columns=("Category","Planned"), show="headings")
        for col in ("Category","Planned"):
            self.budget_tree.heading(col, text=col)
        self.budget_tree.pack(expand=True, fill="both", pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.budget_tab)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Add/Edit Budget", command=self.add_budget).pack(side="left", padx=5)
        self.update_budget_tree()

    def add_budget(self):
        def save_budget():
            cat = cat_var.get()
            val = float(amount_var.get())
            self.data["budgets"][cat] = val
            self.update_budget_tree()
            self.update_dashboard_tree()
            self.update_dashboard_chart()
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add/Edit Budget")
        tk.Label(top, text="Category").grid(row=0,column=0)
        tk.Label(top, text="Amount").grid(row=1,column=0)

        cat_var = tk.StringVar()
        amount_var = tk.StringVar()

        tk.Entry(top, textvariable=cat_var).grid(row=0,column=1)
        tk.Entry(top, textvariable=amount_var).grid(row=1,column=1)

        ttk.Button(top, text="Save", command=save_budget).grid(row=2,column=0,columnspan=2,pady=5)

    def update_budget_tree(self):
        for row in self.budget_tree.get_children():
            self.budget_tree.delete(row)
        for cat, val in self.data.get("budgets", {}).items():
            self.budget_tree.insert("", "end", values=(cat, val))

    # ------------------------- Category Analysis Tab -------------------------
    def create_category_tab(self):
        self.category_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.category_tab, text="Category Analysis")
        ttk.Label(self.category_tab, text="Category Analysis", font=("Arial",12,"bold")).pack(pady=5)

        self.cat_tree = ttk.Treeview(self.category_tab, columns=("Category","Total Spent"), show="headings")
        for col in ("Category","Total Spent"):
            self.cat_tree.heading(col, text=col)
        self.cat_tree.pack(expand=True, fill="both", pady=10)
        self.update_category_tree()

        if MATPLOTLIB_AVAILABLE:
            self.cat_fig, self.cat_ax = plt.subplots(figsize=(6,3))
            self.cat_canvas = FigureCanvasTkAgg(self.cat_fig, master=self.category_tab)
            self.cat_canvas.get_tk_widget().pack()
            self.update_category_chart()

    def update_category_tree(self):
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)
        cat_totals = {}
        for month, trans_list in self.data.get("transactions", {}).items():
            for t in trans_list:
                cat = t.get("category","Uncategorized")
                cat_totals[cat] = cat_totals.get(cat,0) + t["amount"]
        for cat, val in cat_totals.items():
            self.cat_tree.insert("", "end", values=(cat,val))

    def update_category_chart(self):
        self.cat_ax.clear()
        cat_totals = {}
        for month, trans_list in self.data.get("transactions", {}).items():
            for t in trans_list:
                cat = t.get("category","Uncategorized")
                cat_totals[cat] = cat_totals.get(cat,0) + t["amount"]
        cats = list(cat_totals.keys())
        vals = list(cat_totals.values())
        self.cat_ax.bar(cats, vals)
        self.cat_ax.set_title("Spending by Category")
        self.cat_ax.set_xticklabels(cats, rotation=45)
        self.cat_canvas.draw()

    # ------------------------- Scenario Tab -------------------------
    def create_scenario_tab(self):
        self.scenario_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.scenario_tab, text="What-If Simulator")
        ttk.Label(self.scenario_tab, text="What-If Simulator", font=("Arial",12,"bold")).pack(pady=5)

        ttk.Button(self.scenario_tab, text="Add Scenario", command=self.add_scenario).pack(pady=5)

        self.scenario_tree = ttk.Treeview(self.scenario_tab, columns=("Name","Type","Impact"), show="headings")
        for col in ("Name","Type","Impact"):
            self.scenario_tree.heading(col, text=col)
        self.scenario_tree.pack(expand=True, fill="both", pady=10)
        self.update_scenario_tree()

    def add_scenario(self):
        def save_scenario():
            name = name_var.get()
            stype = type_var.get()
            impact = float(impact_var.get())
            self.data["scenarios"][name] = {"type":stype,"impact":impact}
            self.update_scenario_tree()
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add Scenario")
        tk.Label(top, text="Scenario Name").grid(row=0,column=0)
        tk.Label(top, text="Type").grid(row=1,column=0)
        tk.Label(top, text="Impact Amount").grid(row=2,column=0)

        name_var = tk.StringVar()
        type_var = tk.StringVar()
        impact_var = tk.StringVar()

        tk.Entry(top, textvariable=name_var).grid(row=0,column=1)
        tk.Entry(top, textvariable=type_var).grid(row=1,column=1)
        tk.Entry(top, textvariable=impact_var).grid(row=2,column=1)

        ttk.Button(top, text="Save", command=save_scenario).grid(row=3,column=0,columnspan=2,pady=5)

    def update_scenario_tree(self):
        for row in self.scenario_tree.get_children():
            self.scenario_tree.delete(row)
        for name, info in self.data.get("scenarios", {}).items():
            self.scenario_tree.insert("", "end", values=(name, info["type"], info["impact"]))

    # ------------------------- Reports Tab -------------------------
    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.reports_tab, text="Reports")
        ttk.Label(self.reports_tab, text="Export Reports", font=("Arial",12,"bold")).pack(pady=5)

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

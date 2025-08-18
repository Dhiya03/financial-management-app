import json
import os
from datetime import datetime
from tkinter import Tk, Frame, Label, Entry, Button, Listbox, Scrollbar, END, messagebox

SCENARIO_FILE = "scenarios.json"

class ScenarioManager:
    def __init__(self):
        self.scenarios = []
        self.load_scenarios()

    def load_scenarios(self):
        if os.path.exists(SCENARIO_FILE):
            with open(SCENARIO_FILE, "r") as f:
                self.scenarios = json.load(f)
        else:
            self.scenarios = []

    def save_scenarios(self):
        with open(SCENARIO_FILE, "w") as f:
            json.dump(self.scenarios, f, indent=4)

    def add_scenario(self, category, change, start_month, end_month):
        scenario = {
            "id": len(self.scenarios) + 1,
            "category": category,
            "change": change,
            "start_month": start_month,
            "end_month": end_month
        }
        self.scenarios.append(scenario)
        self.save_scenarios()

    def delete_scenario(self, scenario_id):
        self.scenarios = [s for s in self.scenarios if s["id"] != scenario_id]
        self.save_scenarios()

    def apply_scenarios(self, monthly_data):
        """
        Apply scenarios to monthly_data.
        monthly_data: dict {month_str: {category: spent_amount}}
        Returns projected monthly data with scenarios applied.
        """
        projected = {}
        for month, categories in monthly_data.items():
            projected[month] = categories.copy()
            for scenario in self.scenarios:
                start = datetime.strptime(scenario["start_month"], "%b-%y")
                end = datetime.strptime(scenario["end_month"], "%b-%y")
                current = datetime.strptime(month, "%b-%y")
                if start <= current <= end:
                    if scenario["category"] in projected[month]:
                        projected[month][scenario["category"]] += scenario["change"]
                    else:
                        projected[month][scenario["category"]] = scenario["change"]
        return projected

# --------- GUI for Scenarios ----------
class ScenarioGUI:
    def __init__(self, root, manager, apply_callback=None):
        self.root = root
        self.manager = manager
        self.apply_callback = apply_callback
        self.frame = Frame(root)
        self.frame.pack(fill="both", expand=True)
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        Label(self.frame, text="Category").grid(row=0, column=0)
        self.cat_entry = Entry(self.frame)
        self.cat_entry.grid(row=0, column=1)

        Label(self.frame, text="Change (+/-)").grid(row=1, column=0)
        self.change_entry = Entry(self.frame)
        self.change_entry.grid(row=1, column=1)

        Label(self.frame, text="Start Month (e.g., Aug-25)").grid(row=2, column=0)
        self.start_entry = Entry(self.frame)
        self.start_entry.grid(row=2, column=1)

        Label(self.frame, text="End Month (e.g., Dec-25)").grid(row=3, column=0)
        self.end_entry = Entry(self.frame)
        self.end_entry.grid(row=3, column=1)

        Button(self.frame, text="Add Scenario", command=self.add_scenario).grid(row=4, column=0, columnspan=2, pady=5)

        self.listbox = Listbox(self.frame, width=60)
        self.listbox.grid(row=5, column=0, columnspan=2, pady=5)
        scrollbar = Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=5, column=2, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        Button(self.frame, text="Delete Selected", command=self.delete_selected).grid(row=6, column=0, columnspan=2, pady=5)

        if self.apply_callback:
            Button(self.frame, text="Apply Scenarios", command=self.apply_callback).grid(row=7, column=0, columnspan=2, pady=5)

    def refresh_list(self):
        self.listbox.delete(0, END)
        for s in self.manager.scenarios:
            display = f'ID:{s["id"]} | {s["category"]} | Change: {s["change"]} | {s["start_month"]} → {s["end_month"]}'
            self.listbox.insert(END, display)

    def add_scenario(self):
        try:
            category = self.cat_entry.get()
            change = float(self.change_entry.get())
            start = self.start_entry.get()
            end = self.end_entry.get()
            if not category or not start or not end:
                messagebox.showwarning("Input Error", "All fields are required")
                return
            self.manager.add_scenario(category, change, start, end)
            self.refresh_list()
        except ValueError:
            messagebox.showwarning("Input Error", "Change must be a number")

    def delete_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        scenario = self.manager.scenarios[idx]
        self.manager.delete_scenario(scenario["id"])
        self.refresh_list()


# ---------- Example Integration ----------
if __name__ == "__main__":
    root = Tk()
    root.title("What-If Simulator")
    manager = ScenarioManager()

    # Example dummy monthly data
    monthly_data = {
        "Aug-25": {"Groceries": 5000, "Swiggy": 3000},
        "Sep-25": {"Groceries": 4500, "Swiggy": 3500},
    }

    def apply_scenarios():
        projected = manager.apply_scenarios(monthly_data)
        messagebox.showinfo("Projected Data", str(projected))

    gui = ScenarioGUI(root, manager, apply_callback=apply_scenarios)
    root.mainloop()

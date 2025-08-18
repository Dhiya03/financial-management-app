import tkinter as tk
from tkinter import ttk, messagebox

class WhatIfTab(ttk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="What-If Simulator", font=("Arial", 16)).pack(pady=10)
        ttk.Button(self, text="Add Scenario", command=self.add_scenario_popup).pack(pady=5)
        self.scenario_list = tk.Listbox(self)
        self.scenario_list.pack(fill="both", expand=True)
        self.refresh_list()

    def add_scenario_popup(self):
        popup = tk.Toplevel(self)
        tk.Label(popup

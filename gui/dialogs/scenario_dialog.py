"""
Create scenario dialog for what-if simulations
"""
import tkinter as tk
from tkinter import ttk, messagebox

class ScenarioDialog:
    """Dialog for creating what-if scenarios"""

    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Scenario")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Scenario name
        ttk.Label(main_frame, text="Scenario Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)

        # Scenario type
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var,
                                 values=["Budget Change", "One-time Event", "Investment Adjustment"],
                                 width=37)
        type_combo.grid(row=1, column=1, pady=5)
        type_combo.set("Budget Change")

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=5)
        self.desc_text = tk.Text(main_frame, width=40, height=4)
        self.desc_text.grid(row=2, column=1, pady=5)

        # Parameters frame
        param_frame = ttk.LabelFrame(main_frame, text="Scenario Parameters", padding=10)
        param_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

        ttk.Label(param_frame, text="Category:").grid(row=0, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        ttk.Combobox(param_frame, textvariable=self.category_var, width=25).grid(row=0, column=1, pady=5)

        ttk.Label(param_frame, text="Amount Change:").grid(row=1, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(param_frame, textvariable=self.amount_var, width=27).grid(row=1, column=1, pady=5)

        ttk.Label(param_frame, text="Start Month:").grid(row=2, column=0, sticky='w', pady=5)
        self.start_var = tk.StringVar()
        ttk.Combobox(param_frame, textvariable=self.start_var, width=25).grid(row=2, column=1, pady=5)

        ttk.Label(param_frame, text="End Month:").grid(row=3, column=0, sticky='w', pady=5)
        self.end_var = tk.StringVar()
        ttk.Combobox(param_frame, textvariable=self.end_var, width=25).grid(row=3, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Create", command=self.create_scenario).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)

    def create_scenario(self):
        """Create the scenario"""
        # TODO: Implement scenario creation logic
        messagebox.showinfo("Success", "Scenario created successfully")

        if self.callback:
            self.callback()

        self.dialog.destroy()

    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 250
        y = (self.dialog.winfo_screenheight() // 2) - 200
        self.dialog.geometry(f"500x400+{x}+{y}")

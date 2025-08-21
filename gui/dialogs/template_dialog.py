"""
Budget template dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox

class TemplateDialog:
    """Dialog for applying budget templates"""

    def __init__(self, parent, current_month, callback=None):
        self.parent = parent
        self.current_month = current_month
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Apply Budget Template")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Instructions
        ttk.Label(main_frame, text="Select a budget template to apply:",
                 font=('Arial', 12)).pack(pady=(0, 20))

        # Template selection
        self.template_var = tk.StringVar()
        templates = ["Conservative", "Moderate", "Aggressive"]

        for template in templates:
            ttk.Radiobutton(main_frame, text=template, variable=self.template_var,
                           value=template).pack(anchor='w', pady=5)

        self.template_var.set("Conservative")

        # Apply to multiple months option
        self.multi_month_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Apply to all 24 months",
                       variable=self.multi_month_var).pack(pady=20)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', pady=20)

        ttk.Button(button_frame, text="Apply", command=self.apply_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)

    def apply_template(self):
        """Apply selected template"""
        template = self.template_var.get()
        apply_all = self.multi_month_var.get()

        # TODO: Implement template application logic
        messagebox.showinfo("Success", f"Applied {template} template")

        if self.callback:
            self.callback()

        self.dialog.destroy()

    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 200
        y = (self.dialog.winfo_screenheight() // 2) - 150
        self.dialog.geometry(f"400x300+{x}+{y}")

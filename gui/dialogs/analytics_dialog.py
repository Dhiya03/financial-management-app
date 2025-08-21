"""
Analytics details dialog
"""
import tkinter as tk
from tkinter import ttk

class AnalyticsDialog:
    """Dialog for detailed analytics view"""

    def __init__(self, parent, category=None):
        self.parent = parent
        self.category = category
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Analytics: {category or 'All Categories'}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Title
        title = f"Detailed Analysis: {self.category or 'All Categories'}"
        ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Placeholder content
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Trends tab
        trends_frame = ttk.Frame(notebook)
        notebook.add(trends_frame, text="Trends")
        ttk.Label(trends_frame, text="[Trend analysis will appear here]",
                 font=('Arial', 12, 'italic')).pack(expand=True)

        # Statistics tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        ttk.Label(stats_frame, text="[Statistical analysis will appear here]",
                 font=('Arial', 12, 'italic')).pack(expand=True)

        # Insights tab
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="Insights")
        ttk.Label(insights_frame, text="[AI-generated insights will appear here]",
                 font=('Arial', 12, 'italic')).pack(expand=True)

        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=10)

    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 250
        self.dialog.geometry(f"600x500+{x}+{y}")

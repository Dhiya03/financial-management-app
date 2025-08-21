"""
Main application window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

from config import AppSettings
from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.transactions_tab import TransactionsTab
from gui.tabs.budget_tab import BudgetTab
from gui.tabs.analysis_tab import AnalysisTab
from gui.tabs.simulator_tab import SimulatorTab
from gui.tabs.reports_tab import ReportsTab

class FinancialManagementApp:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_tabs()
        self.setup_menu()
        self.setup_status_bar()
        
    def setup_window(self):
        """Configure main window"""
        self.root.title(f"{AppSettings.APP_NAME} v{AppSettings.APP_VERSION}")
        self.root.geometry(f"{AppSettings.WINDOW_WIDTH}x{AppSettings.WINDOW_HEIGHT}")
        self.root.minsize(AppSettings.MIN_WINDOW_WIDTH, AppSettings.MIN_WINDOW_HEIGHT)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (AppSettings.WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (AppSettings.WINDOW_HEIGHT // 2)
        self.root.geometry(f"{AppSettings.WINDOW_WIDTH}x{AppSettings.WINDOW_HEIGHT}+{x}+{y}")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.configure('Tab.TNotebook.Tab', padding=[20, 10])
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
    def setup_tabs(self):
        """Create and configure tabs"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tab instances
        self.dashboard_tab = DashboardTab(self.notebook)
        self.transactions_tab = TransactionsTab(self.notebook)
        self.budget_tab = BudgetTab(self.notebook)
        self.analysis_tab = AnalysisTab(self.notebook)
        self.simulator_tab = SimulatorTab(self.notebook)
        self.reports_tab = ReportsTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab.frame, text="📊 Dashboard", padding=10)
        self.notebook.add(self.transactions_tab.frame, text="💳 Transactions", padding=10)
        self.notebook.add(self.budget_tab.frame, text="💰 Budget Planning", padding=10)
        self.notebook.add(self.analysis_tab.frame, text="📈 Analytics", padding=10)
        self.notebook.add(self.simulator_tab.frame, text="🎯 Simulator", padding=10)
        self.notebook.add(self.reports_tab.frame, text="📄 Reports", padding=10)
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Transaction", command=self.new_transaction, accelerator="Ctrl+N")
        file_menu.add_command(label="Import CSV", command=self.import_csv, accelerator="Ctrl+I")
        file_menu.add_separator()
        file_menu.add_command(label="Backup Data", command=self.backup_data, accelerator="Ctrl+B")
        file_menu.add_command(label="Restore Data", command=self.restore_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Auto-Categorize", command=self.auto_categorize)
        edit_menu.add_command(label="Clean Data", command=self.clean_data)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_tabs, accelerator="F5")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_transaction())
        self.root.bind('<Control-i>', lambda e: self.import_csv())
        self.root.bind('<Control-b>', lambda e: self.backup_data())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F5>', lambda e: self.refresh_all_tabs())
    
    def setup_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side='left', padx=5)
        
        self.data_info_label = ttk.Label(self.status_bar, text="")
        self.data_info_label.pack(side='right', padx=5)
        
        self.update_status_bar()
    
    def update_status_bar(self):
        """Update status bar information"""
        # Placeholder for status updates
        pass
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        tab_name = tab_text.split()[-1].lower()
        logging.info(f"Switched to tab: {tab_name}")
        self.update_status_bar()
    
    def new_transaction(self):
        """Open new transaction dialog"""
        # Placeholder for new transaction dialog
        messagebox.showinfo("New Transaction", "Add transaction functionality coming soon")
    
    def import_csv(self):
        """Import CSV file"""
        # Placeholder for CSV import
        messagebox.showinfo("Import CSV", "CSV import functionality coming soon")
    
    def backup_data(self):
        """Create data backup"""
        # Placeholder for backup
        messagebox.showinfo("Backup", "Backup functionality coming soon")
    
    def restore_data(self):
        """Restore from backup"""
        # Placeholder for restore
        messagebox.showinfo("Restore", "Restore functionality coming soon")
    
    def auto_categorize(self):
        """Auto-categorize transactions"""
        # Placeholder for auto-categorization
        messagebox.showinfo("Auto-Categorize", "Auto-categorization coming soon")
    
    def clean_data(self):
        """Clean data"""
        # Placeholder for data cleaning
        messagebox.showinfo("Clean Data", "Data cleaning functionality coming soon")
    
    def refresh_all_tabs(self):
        """Refresh all tabs"""
        for tab_name in ['dashboard', 'transactions', 'budget', 'analysis', 'simulator', 'reports']:
            tab_obj = getattr(self, f"{tab_name}_tab", None)
            if tab_obj and hasattr(tab_obj, 'refresh'):
                tab_obj.refresh()
        self.update_status_bar()
        self.status_label.config(text="All tabs refreshed")
    
    def show_help(self):
        """Show help dialog"""
        messagebox.showinfo("Help", "User guide coming soon")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        Keyboard Shortcuts:
        
        Ctrl+N: New Transaction
        Ctrl+I: Import CSV
        Ctrl+B: Backup Data
        Ctrl+Q: Exit
        F5: Refresh All
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        {AppSettings.APP_NAME}
        Version: {AppSettings.APP_VERSION}
        Author: {AppSettings.APP_AUTHOR}
        
        Personal finance management tool
        """
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askyesno("Exit", "Do you want to save data before exiting?"):
            from managers.data_manager import data_manager
            data_manager.save()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        logging.info("Starting GUI application")
        self.status_label.config(text="Application started successfully")
        self.root.mainloop()

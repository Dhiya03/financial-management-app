"""
What-if simulator tab for scenario planning
"""
import tkinter as tk
from tkinter import ttk
import logging

class SimulatorTab:
    """What-if simulator tab"""

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup simulator tab UI"""
        # Title
        title_label = ttk.Label(self.frame, text="What-If Simulator", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Scenario list frame
        scenario_frame = ttk.LabelFrame(self.frame, text="Scenarios", padding=15)
        scenario_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Buttons
        button_frame = ttk.Frame(scenario_frame)
        button_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(button_frame, text="Create New Scenario").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Run Simulation").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Compare Scenarios").pack(side='left', padx=5)

        # Placeholder list
        list_frame = ttk.Frame(scenario_frame)
        list_frame.pack(fill='both', expand=True)

        ttk.Label(list_frame, text="Scenario Types:", font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(list_frame, text="• Budget Changes").pack(anchor='w', padx=20)
        ttk.Label(list_frame, text="• One-time Events").pack(anchor='w', padx=20)
        ttk.Label(list_frame, text="• Investment Adjustments").pack(anchor='w', padx=20)

        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Simulation Results", padding=15)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        ttk.Label(results_frame, text="[Simulation results will appear here]",
                 font=('Arial', 12, 'italic')).pack(expand=True)

    def refresh(self):
        """Refresh simulator data"""
        logging.info("Refreshing simulator tab")
        # TODO: Implement scenario refresh logic

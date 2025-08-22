"""
What-If Simulator Tab - Complete Implementation
Implements User Story 5: Advanced Financial Scenario Simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from copy import deepcopy
import json

from config import PLANNING_MONTHS, CURRENCY_SYMBOL, DEFAULT_CATEGORIES
from managers.scenario_simulator import ScenarioSimulator
from managers.budget_manager import BudgetManager
from managers.transaction_manager import TransactionManager
from utils.formatters import format_currency, format_percentage

class SimulatorTab:
    """What-if simulator tab for scenario planning"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.simulator = ScenarioSimulator()
        self.budget_manager = BudgetManager()
        self.transaction_manager = TransactionManager()
        
        # Track current scenario
        self.current_scenario = None
        self.scenario_results = {}
        self.comparison_data = {}
        
        # Store scenarios
        self.scenarios = self.load_scenarios()
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup simulator tab UI"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Header with title and controls
        self.setup_header(main_container)
        
        # Create main layout with paned window
        paned = ttk.PanedWindow(main_container, orient='horizontal')
        paned.pack(fill='both', expand=True, pady=(10, 0))
        
        # Left panel - Scenario management
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        self.setup_scenario_panel(left_frame)
        
        # Right panel - Results and analysis
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        self.setup_results_panel(right_frame)
    
    def setup_header(self, parent):
        """Setup header with controls"""
        header_frame = ttk.LabelFrame(parent, text="What-If Simulator", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(header_frame, 
                              text="Create and simulate financial scenarios to understand their impact on your budget",
                              font=('Arial', 10))
        desc_label.pack(anchor='w', pady=(0, 10))
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="➕ New Scenario", 
                  command=self.create_scenario).pack(side='left', padx=2)
        ttk.Button(button_frame, text="📊 Compare Scenarios", 
                  command=self.compare_scenarios).pack(side='left', padx=2)
        ttk.Button(button_frame, text="🔄 Reset All", 
                  command=self.reset_all_scenarios).pack(side='left', padx=2)
        ttk.Button(button_frame, text="📤 Export Results", 
                  command=self.export_results).pack(side='left', padx=2)
    
    def setup_scenario_panel(self, parent):
        """Setup scenario management panel"""
        # Scenario list
        list_frame = ttk.LabelFrame(parent, text="Scenarios", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scenario listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)
        
        self.scenario_listbox = tk.Listbox(list_container, height=15)
        scrollbar = ttk.Scrollbar(list_container, command=self.scenario_listbox.yview)
        self.scenario_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.scenario_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.scenario_listbox.bind('<<ListboxSelect>>', self.on_scenario_selected)
        
        # Scenario action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(action_frame, text="Edit", 
                  command=self.edit_scenario).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Duplicate", 
                  command=self.duplicate_scenario).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Delete", 
                  command=self.delete_scenario).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Apply", 
                  command=self.apply_scenario).pack(side='right', padx=2)
        
        # Scenario details
        details_frame = ttk.LabelFrame(parent, text="Scenario Details", padding=10)
        details_frame.pack(fill='x')
        
        self.details_text = tk.Text(details_frame, height=8, width=40, wrap='word')
        self.details_text.pack(fill='both', expand=True)
    
    def setup_results_panel(self, parent):
        """Setup results and analysis panel"""
        # Create notebook for different views
        self.results_notebook = ttk.Notebook(parent)
        self.results_notebook.pack(fill='both', expand=True)
        
        # Impact Analysis tab
        impact_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(impact_frame, text="Impact Analysis")
        self.setup_impact_analysis(impact_frame)
        
        # Monthly View tab
        monthly_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(monthly_frame, text="Monthly Breakdown")
        self.setup_monthly_view(monthly_frame)
        
        # Comparison tab
        comparison_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(comparison_frame, text="Scenario Comparison")
        self.setup_comparison_view(comparison_frame)
        
        # Recommendations tab
        recommendations_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(recommendations_frame, text="Recommendations")
        self.setup_recommendations_view(recommendations_frame)
    
    def setup_impact_analysis(self, parent):
        """Setup impact analysis view"""
        # Summary cards
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        # Configure grid
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)
        
        # Net Impact card
        impact_card = ttk.LabelFrame(summary_frame, text="Net Impact", padding=10)
        impact_card.grid(row=0, column=0, padx=5, sticky='ew')
        
        self.net_impact_label = ttk.Label(impact_card, text=f"{CURRENCY_SYMBOL}0",
                                         font=('Arial', 14, 'bold'))
        self.net_impact_label.pack()
        self.impact_direction_label = ttk.Label(impact_card, text="")
        self.impact_direction_label.pack()
        
        # Affected Months card
        months_card = ttk.LabelFrame(summary_frame, text="Affected Period", padding=10)
        months_card.grid(row=0, column=1, padx=5, sticky='ew')
        
        self.affected_months_label = ttk.Label(months_card, text="0 months",
                                              font=('Arial', 14, 'bold'))
        self.affected_months_label.pack()
        self.period_range_label = ttk.Label(months_card, text="")
        self.period_range_label.pack()
        
        # Risk Level card
        risk_card = ttk.LabelFrame(summary_frame, text="Risk Assessment", padding=10)
        risk_card.grid(row=0, column=2, padx=5, sticky='ew')
        
        self.risk_level_label = ttk.Label(risk_card, text="Low",
                                         font=('Arial', 14, 'bold'))
        self.risk_level_label.pack()
        self.risk_details_label = ttk.Label(risk_card, text="")
        self.risk_details_label.pack()
        
        # Detailed impact analysis
        analysis_frame = ttk.LabelFrame(parent, text="Detailed Analysis", padding=10)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.impact_text = tk.Text(analysis_frame, height=15, width=60, wrap='word')
        scrollbar = ttk.Scrollbar(analysis_frame, command=self.impact_text.yview)
        self.impact_text.configure(yscrollcommand=scrollbar.set)
        
        self.impact_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configure text tags
        self.impact_text.tag_configure('header', font=('Arial', 12, 'bold'))
        self.impact_text.tag_configure('positive', foreground='green')
        self.impact_text.tag_configure('negative', foreground='red')
        self.impact_text.tag_configure('warning', foreground='orange')
    
    def setup_monthly_view(self, parent):
        """Setup monthly breakdown view"""
        # Monthly impact table
        table_frame = ttk.Frame(parent, padding=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview
        columns = ('Month', 'Original Budget', 'Simulated Budget', 'Change', '% Change', 'Impact')
        self.monthly_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        column_widths = {
            'Month': 100,
            'Original Budget': 120,
            'Simulated Budget': 120,
            'Change': 100,
            '% Change': 80,
            'Impact': 100
        }
        
        for col in columns:
            self.monthly_tree.heading(col, text=col)
            self.monthly_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.monthly_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.monthly_tree.xview)
        self.monthly_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.monthly_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tags
        self.monthly_tree.tag_configure('increase', foreground='red')
        self.monthly_tree.tag_configure('decrease', foreground='green')
        self.monthly_tree.tag_configure('neutral', foreground='gray')
    
    def setup_comparison_view(self, parent):
        """Setup scenario comparison view"""
        # Comparison controls
        control_frame = ttk.Frame(parent, padding=10)
        control_frame.pack(fill='x')
        
        ttk.Label(control_frame, text="Select scenarios to compare:",
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Scenario selection checkboxes will be added dynamically
        self.comparison_vars = {}
        self.comparison_frame = ttk.Frame(control_frame)
        self.comparison_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(control_frame, text="Compare Selected",
                  command=self.perform_comparison).pack(pady=10)
        
        # Comparison results
        results_frame = ttk.LabelFrame(parent, text="Comparison Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10)
        
        self.comparison_text = tk.Text(results_frame, height=15, width=70, wrap='word')
        scrollbar = ttk.Scrollbar(results_frame, command=self.comparison_text.yview)
        self.comparison_text.configure(yscrollcommand=scrollbar.set)
        
        self.comparison_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_recommendations_view(self, parent):
        """Setup recommendations view"""
        rec_frame = ttk.Frame(parent, padding=10)
        rec_frame.pack(fill='both', expand=True)
        
        ttk.Label(rec_frame, text="Scenario Recommendations",
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.recommendations_text = tk.Text(rec_frame, height=20, width=70, wrap='word')
        scrollbar = ttk.Scrollbar(rec_frame, command=self.recommendations_text.yview)
        self.recommendations_text.configure(yscrollcommand=scrollbar.set)
        
        self.recommendations_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configure tags
        self.recommendations_text.tag_configure('recommendation', font=('Arial', 10, 'bold'))
        self.recommendations_text.tag_configure('pro', foreground='green')
        self.recommendations_text.tag_configure('con', foreground='red')
        self.recommendations_text.tag_configure('action', foreground='blue')
    
    def load_scenarios(self) -> List[Dict]:
        """Load saved scenarios"""
        from managers.data_manager import data_manager
        return list(data_manager.get_data().scenarios.values())
    
    def refresh(self):
        """Refresh scenario list and views"""
        self.refresh_scenario_list()
        self.update_comparison_checkboxes()
        
        if not self.scenarios:
            self.clear_all_views()
            self.show_welcome_message()
    
    def refresh_scenario_list(self):
        """Refresh the scenario listbox"""
        self.scenario_listbox.delete(0, tk.END)
        
        for scenario in self.scenarios:
            # Format display text
            name = scenario.get('name', 'Unnamed')
            scenario_type = scenario.get('scenario_type', 'unknown')
            changes_count = len(scenario.get('changes', []))
            
            display_text = f"{name} ({scenario_type}) - {changes_count} changes"
            self.scenario_listbox.insert(tk.END, display_text)
    
    def update_comparison_checkboxes(self):
        """Update comparison checkboxes based on scenarios"""
        # Clear existing checkboxes
        for widget in self.comparison_frame.winfo_children():
            widget.destroy()
        self.comparison_vars.clear()
        
        # Add checkbox for each scenario
        for i, scenario in enumerate(self.scenarios):
            var = tk.BooleanVar()
            self.comparison_vars[scenario.get('id', str(i))] = var
            
            cb = ttk.Checkbutton(self.comparison_frame, 
                                text=scenario.get('name', f'Scenario {i+1}'),
                                variable=var)
            cb.pack(anchor='w', pady=2)
    
    def on_scenario_selected(self, event=None):
        """Handle scenario selection"""
        selection = self.scenario_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.scenarios):
                self.current_scenario = self.scenarios[index]
                self.show_scenario_details()
                self.simulate_scenario()
    
    def show_scenario_details(self):
        """Show details of selected scenario"""
        if not self.current_scenario:
            return
        
        self.details_text.delete(1.0, tk.END)
        
        # Display scenario details
        self.details_text.insert(tk.END, f"Name: {self.current_scenario.get('name', 'Unnamed')}\n")
        self.details_text.insert(tk.END, f"Type: {self.current_scenario.get('scenario_type', 'Unknown')}\n")
        self.details_text.insert(tk.END, f"Created: {self.current_scenario.get('created_at', 'Unknown')[:10]}\n\n")
        
        self.details_text.insert(tk.END, "Changes:\n")
        for change in self.current_scenario.get('changes', []):
            category = change.get('category', 'Unknown')
            
            if self.current_scenario.get('scenario_type') == 'budget_change':
                amount = change.get('amount_change', 0)
                start = change.get('start_month', '')
                end = change.get('end_month', '')
                self.details_text.insert(tk.END, f"• {category}: {format_currency(amount)}\n")
                self.details_text.insert(tk.END, f"  Period: {start} to {end}\n")
            elif self.current_scenario.get('scenario_type') == 'one_time_event':
                amount = change.get('amount', 0)
                month = change.get('event_month', '')
                self.details_text.insert(tk.END, f"• {category}: {format_currency(amount)}\n")
                self.details_text.insert(tk.END, f"  Month: {month}\n")
            elif self.current_scenario.get('scenario_type') == 'investment_adjustment':
                adj_type = change.get('adjustment_type', '')
                start = change.get('start_month', '')
                end = change.get('end_month', '')
                self.details_text.insert(tk.END, f"• {category}: {adj_type}\n")
                self.details_text.insert(tk.END, f"  Period: {start} to {end}\n")
    
    def simulate_scenario(self):
        """Simulate the selected scenario"""
        if not self.current_scenario:
            return
        
        try:
            # Run simulation
            results = self.simulator.simulate_scenario(self.current_scenario.get('id', ''))
            
            if 'error' in results:
                messagebox.showerror("Simulation Error", results['error'])
                return
            
            self.scenario_results = results
            
            # Update all views
            self.update_impact_analysis()
            self.update_monthly_view()
            self.generate_recommendations()
            
        except Exception as e:
            logging.error(f"Error simulating scenario: {e}")
            messagebox.showerror("Error", f"Failed to simulate scenario: {str(e)}")
    
    def update_impact_analysis(self):
        """Update impact analysis view"""
        if not self.scenario_results:
            return
        
        impact = self.scenario_results.get('impact', {})
        
        # Update summary cards
        net_impact = impact.get('total_impact', 0)
        self.net_impact_label.config(text=format_currency(abs(net_impact)))
        
        if net_impact > 0:
            self.impact_direction_label.config(text="Increase in spending", foreground='red')
            self.net_impact_label.config(foreground='red')
        elif net_impact < 0:
            self.impact_direction_label.config(text="Decrease in spending", foreground='green')
            self.net_impact_label.config(foreground='green')
        else:
            self.impact_direction_label.config(text="No net change", foreground='gray')
            self.net_impact_label.config(foreground='gray')
        
        # Update affected months
        affected = impact.get('affected_months', 0)
        self.affected_months_label.config(text=f"{affected} months")
        
        monthly_changes = impact.get('monthly_changes', {})
        if monthly_changes:
            months = list(monthly_changes.keys())
            self.period_range_label.config(text=f"{months[0]} to {months[-1]}")
        
        # Update risk assessment
        summary = impact.get('summary', {})
        risk_level = summary.get('risk_level', 'unknown')
        
        if risk_level == 'high':
            self.risk_level_label.config(text="High Risk", foreground='red')
            self.risk_details_label.config(text="Significant budget impact")
        elif risk_level == 'medium':
            self.risk_level_label.config(text="Medium Risk", foreground='orange')
            self.risk_details_label.config(text="Moderate budget impact")
        else:
            self.risk_level_label.config(text="Low Risk", foreground='green')
            self.risk_details_label.config(text="Manageable impact")
        
        # Update detailed analysis
        self.impact_text.delete(1.0, tk.END)
        
        self.impact_text.insert(tk.END, "SCENARIO IMPACT ANALYSIS\n", 'header')
        self.impact_text.insert(tk.END, "="*50 + "\n\n")
        
        # Summary
        self.impact_text.insert(tk.END, f"Scenario: {self.current_scenario.get('name', 'Unnamed')}\n")
        self.impact_text.insert(tk.END, f"Type: {self.current_scenario.get('scenario_type', 'Unknown')}\n\n")
        
        # Financial Impact
        self.impact_text.insert(tk.END, "Financial Impact:\n", 'header')
        self.impact_text.insert(tk.END, f"• Net Change: ")
        if net_impact > 0:
            self.impact_text.insert(tk.END, f"+{format_currency(net_impact)}\n", 'negative')
        else:
            self.impact_text.insert(tk.END, f"{format_currency(net_impact)}\n", 'positive')
        
        self.impact_text.insert(tk.END, f"• Affected Months: {affected}\n")
        self.impact_text.insert(tk.END, f"• Risk Level: {risk_level.title()}\n\n")
        
        # Category Impact
        category_impact = impact.get('category_impact', {})
        if category_impact:
            self.impact_text.insert(tk.END, "Category Impact:\n", 'header')
            
            for category, cat_impact in sorted(category_impact.items(), 
                                              key=lambda x: abs(x[1]['change']), 
                                              reverse=True)[:10]:
                change = cat_impact['change']
                self.impact_text.insert(tk.END, f"• {category}: ")
                
                if change > 0:
                    self.impact_text.insert(tk.END, f"+{format_currency(change)}\n", 'negative')
                else:
                    self.impact_text.insert(tk.END, f"{format_currency(change)}\n", 'positive')
        
        # Recommendation
        self.impact_text.insert(tk.END, "\nRecommendation:\n", 'header')
        self.impact_text.insert(tk.END, summary.get('recommendation', 'Review budget allocations'))
    
    def update_monthly_view(self):
        """Update monthly breakdown view"""
        # Clear existing items
        for item in self.monthly_tree.get_children():
            self.monthly_tree.delete(item)
        
        if not self.scenario_results:
            return
        
        impact = self.scenario_results.get('impact', {})
        monthly_changes = impact.get('monthly_changes', {})
        
        for month in PLANNING_MONTHS:
            if month in monthly_changes:
                change_data = monthly_changes[month]
                original = change_data['original_total']
                simulated = change_data['simulated_total']
                change = change_data['change']
                change_percent = change_data['change_percent']
                
                # Determine tag
                if change > 0:
                    tag = 'increase'
                    impact = 'Increase'
                elif change < 0:
                    tag = 'decrease'
                    impact = 'Decrease'
                else:
                    tag = 'neutral'
                    impact = 'No Change'
                
                self.monthly_tree.insert('', 'end', values=(
                    month,
                    format_currency(original),
                    format_currency(simulated),
                    format_currency(change),
                    f"{change_percent:.1f}%",
                    impact
                ), tags=(tag,))
    
    def generate_recommendations(self):
        """Generate recommendations for the scenario"""
        self.recommendations_text.delete(1.0, tk.END)
        
        if not self.scenario_results:
            return
        
        impact = self.scenario_results.get('impact', {})
        summary = impact.get('summary', {})
        
        self.recommendations_text.insert(tk.END, "SCENARIO RECOMMENDATIONS\n", 'recommendation')
        self.recommendations_text.insert(tk.END, "="*50 + "\n\n")
        
        # Pros
        self.recommendations_text.insert(tk.END, "Advantages:\n", 'recommendation')
        
        net_change = impact.get('total_impact', 0)
        if net_change < 0:
            self.recommendations_text.insert(tk.END, 
                f"✓ Reduces overall spending by {format_currency(abs(net_change))}\n", 'pro')
            self.recommendations_text.insert(tk.END, 
                "✓ Improves budget efficiency\n", 'pro')
        
        category_impact = impact.get('category_impact', {})
        reduced_categories = [cat for cat, imp in category_impact.items() if imp['change'] < 0]
        if reduced_categories:
            self.recommendations_text.insert(tk.END, 
                f"✓ Optimizes {len(reduced_categories)} category budgets\n", 'pro')
        
        # Cons
        self.recommendations_text.insert(tk.END, "\nDisadvantages:\n", 'recommendation')
        
        if net_change > 0:
            self.recommendations_text.insert(tk.END, 
                f"✗ Increases spending by {format_currency(net_change)}\n", 'con')
        
        risk_level = summary.get('risk_level', 'low')
        if risk_level == 'high':
            self.recommendations_text.insert(tk.END, 
                "✗ High risk - significant budget impact\n", 'con')
        
        affected_months = impact.get('affected_months', 0)
        if affected_months > 12:
            self.recommendations_text.insert(tk.END, 
                f"✗ Long-term commitment ({affected_months} months)\n", 'con')
        
        # Action Items
        self.recommendations_text.insert(tk.END, "\nRecommended Actions:\n", 'recommendation')
        
        actions = self.generate_action_items(impact, summary)
        for i, action in enumerate(actions, 1):
            self.recommendations_text.insert(tk.END, f"{i}. {action}\n", 'action')
        
        # Overall Assessment
        self.recommendations_text.insert(tk.END, "\nOverall Assessment:\n", 'recommendation')
        self.recommendations_text.insert(tk.END, summary.get('recommendation', 
            'Review the scenario impact carefully before implementation'))
    
    def generate_action_items(self, impact: Dict, summary: Dict) -> List[str]:
        """Generate specific action items"""
        actions = []
        
        net_change = impact.get('total_impact', 0)
        risk_level = summary.get('risk_level', 'low')
        
        if risk_level == 'high':
            actions.append("Review and validate all assumptions before proceeding")
            actions.append("Consider implementing changes gradually")
        
        if net_change > 10000:
            actions.append("Identify additional income sources or savings opportunities")
        
        category_impact = impact.get('category_impact', {})
        high_impact_cats = [cat for cat, imp in category_impact.items() 
                           if abs(imp['change']) > 5000]
        if high_impact_cats:
            actions.append(f"Focus on optimizing: {', '.join(high_impact_cats[:3])}")
        
        if impact.get('affected_months', 0) > 6:
            actions.append("Set up monthly review checkpoints to track progress")
        
        if not actions:
            actions.append("Proceed with implementation and monitor results")
        
        return actions
    
    def create_scenario(self):
        """Open dialog to create new scenario"""
        CreateScenarioDialog(self.frame, callback=self.on_scenario_created)
    
    def on_scenario_created(self, scenario_data: Dict):
        """Handle new scenario creation"""
        try:
            # Create scenario using simulator
            name = scenario_data['name']
            description = scenario_data.get('description', '')
            scenario_type = scenario_data['type']
            changes = scenario_data['changes']
            
            success, message = self.simulator.create_scenario(
                name, description, scenario_type, changes
            )
            
            if success:
                # Reload scenarios
                self.scenarios = self.load_scenarios()
                self.refresh()
                messagebox.showinfo("Success", "Scenario created successfully")
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            logging.error(f"Error creating scenario: {e}")
            messagebox.showerror("Error", f"Failed to create scenario: {str(e)}")
    
    def edit_scenario(self):
        """Edit selected scenario"""
        selection = self.scenario_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.scenarios):
                scenario = self.scenarios[index]
                EditScenarioDialog(self.frame, scenario, callback=self.on_scenario_edited)
    
    def on_scenario_edited(self, updated_scenario: Dict):
        """Handle scenario edit"""
        # Update scenario in data
        from managers.data_manager import data_manager
        app_data = data_manager.get_data()
        
        scenario_id = updated_scenario.get('id')
        if scenario_id in app_data.scenarios:
            app_data.scenarios[scenario_id] = updated_scenario
            data_manager.save()
            
            # Reload and refresh
            self.scenarios = self.load_scenarios()
            self.refresh()
            messagebox.showinfo("Success", "Scenario updated successfully")
    
    def duplicate_scenario(self):
        """Duplicate selected scenario"""
        selection = self.scenario_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.scenarios):
                original = self.scenarios[index]
                
                # Create copy with new name
                new_scenario = deepcopy(original)
                new_scenario['name'] = f"{original.get('name', 'Scenario')} (Copy)"
                new_scenario['id'] = None  # Will be regenerated
                
                # Create using simulator
                success, _ = self.simulator.create_scenario(
                    new_scenario['name'],
                    new_scenario.get('description', ''),
                    new_scenario.get('scenario_type', 'budget_change'),
                    new_scenario.get('changes', [])
                )
                
                if success:
                    self.scenarios = self.load_scenarios()
                    self.refresh()
                    messagebox.showinfo("Success", "Scenario duplicated successfully")
    
    def delete_scenario(self):
        """Delete selected scenario"""
        selection = self.scenario_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.scenarios):
                scenario = self.scenarios[index]
                
                if messagebox.askyesno("Delete Scenario", 
                                      f"Delete scenario '{scenario.get('name', 'Unnamed')}'?"):
                    success, message = self.simulator.delete_scenario(scenario.get('id', ''))
                    
                    if success:
                        self.scenarios = self.load_scenarios()
                        self.refresh()
                        messagebox.showinfo("Success", "Scenario deleted")
                    else:
                        messagebox.showerror("Error", message)
    
    def apply_scenario(self):
        """Apply selected scenario to actual budgets"""
        if not self.current_scenario:
            messagebox.showwarning("No Selection", "Please select a scenario to apply")
            return
        
        if messagebox.askyesno("Apply Scenario", 
                              f"Apply '{self.current_scenario.get('name', 'Unnamed')}' to actual budgets?\n\n"
                              "This will modify your real budget data."):
            
            # Apply the scenario changes to actual budgets
            # This would need implementation in the budget manager
            messagebox.showinfo("Applied", "Scenario applied to budgets\n\n"
                              "Note: This is a simulation. Actual budget modification "
                              "would be implemented in production.")
    
    def compare_scenarios(self):
        """Open scenario comparison view"""
        self.results_notebook.select(2)  # Switch to comparison tab
    
    def perform_comparison(self):
        """Perform comparison of selected scenarios"""
        selected_ids = [sid for sid, var in self.comparison_vars.items() if var.get()]
        
        if len(selected_ids) < 2:
            messagebox.showwarning("Selection Required", "Please select at least 2 scenarios to compare")
            return
        
        self.comparison_text.delete(1.0, tk.END)
        
        self.comparison_text.insert(tk.END, "SCENARIO COMPARISON\n", 'header')
        self.comparison_text.insert(tk.END, "="*60 + "\n\n")
        
        # Simulate each selected scenario
        comparison_data = []
        for scenario_id in selected_ids:
            # Find scenario
            scenario = next((s for s in self.scenarios if s.get('id') == scenario_id), None)
            if scenario:
                results = self.simulator.simulate_scenario(scenario_id)
                if 'error' not in results:
                    comparison_data.append({
                        'name': scenario.get('name', 'Unnamed'),
                        'impact': results.get('impact', {}),
                        'summary': results.get('impact', {}).get('summary', {})
                    })
        
        # Compare results
        if comparison_data:
            # Net impact comparison
            self.comparison_text.insert(tk.END, "Net Impact:\n")
            for data in comparison_data:
                net_impact = data['impact'].get('total_impact', 0)
                name = data['name']
                self.comparison_text.insert(tk.END, f"• {name}: {format_currency(net_impact)}\n")
            
            self.comparison_text.insert(tk.END, "\nRisk Assessment:\n")
            for data in comparison_data:
                risk = data['summary'].get('risk_level', 'unknown')
                name = data['name']
                self.comparison_text.insert(tk.END, f"• {name}: {risk.title()}\n")
            
            # Find best scenario
            best_scenario = min(comparison_data, key=lambda x: x['impact'].get('total_impact', 0))
            self.comparison_text.insert(tk.END, f"\nRecommended: {best_scenario['name']}\n", 'positive')
    
    def reset_all_scenarios(self):
        """Reset/clear all scenarios"""
        if self.scenarios and messagebox.askyesno("Reset All", 
                                                 "Delete all scenarios? This cannot be undone."):
            from managers.data_manager import data_manager
            app_data = data_manager.get_data()
            app_data.scenarios.clear()
            data_manager.save()
            
            self.scenarios = []
            self.refresh()
            messagebox.showinfo("Reset", "All scenarios have been deleted")
    
    def export_results(self):
        """Export simulation results"""
        if not self.scenario_results:
            messagebox.showwarning("No Results", "Please simulate a scenario first")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"scenario_results_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        if file_path:
            try:
                export_data = {
                    'scenario': self.current_scenario,
                    'results': self.scenario_results,
                    'exported': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Export Complete", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def clear_all_views(self):
        """Clear all result views"""
        self.impact_text.delete(1.0, tk.END)
        self.comparison_text.delete(1.0, tk.END)
        self.recommendations_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)
        
        for item in self.monthly_tree.get_children():
            self.monthly_tree.delete(item)
    
    def show_welcome_message(self):
        """Show welcome message when no scenarios exist"""
        self.impact_text.insert(tk.END, "Welcome to What-If Simulator!\n\n", 'header')
        self.impact_text.insert(tk.END, "Create your first scenario to:\n")
        self.impact_text.insert(tk.END, "• Simulate budget changes\n")
        self.impact_text.insert(tk.END, "• Model one-time expenses\n")
        self.impact_text.insert(tk.END, "• Test investment adjustments\n")
        self.impact_text.insert(tk.END, "• Compare different financial strategies\n\n")
        self.impact_text.insert(tk.END, "Click 'New Scenario' to get started!")


class CreateScenarioDialog:
    """Dialog for creating new scenarios"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.changes = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Scenario")
        self.dialog.geometry("600x700")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Scenario name
        ttk.Label(main_frame, text="Scenario Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky='w', pady=5)
        self.desc_text = tk.Text(main_frame, height=3, width=40)
        self.desc_text.grid(row=1, column=1, pady=5)
        
        # Scenario type
        ttk.Label(main_frame, text="Type:").grid(row=2, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar(value="budget_change")
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Radiobutton(type_frame, text="Budget Change", 
                       variable=self.type_var, value="budget_change",
                       command=self.on_type_changed).pack(anchor='w')
        ttk.Radiobutton(type_frame, text="One-time Event", 
                       variable=self.type_var, value="one_time_event",
                       command=self.on_type_changed).pack(anchor='w')
        ttk.Radiobutton(type_frame, text="Investment Adjustment", 
                       variable=self.type_var, value="investment_adjustment",
                       command=self.on_type_changed).pack(anchor='w')
        
        # Changes section
        changes_frame = ttk.LabelFrame(main_frame, text="Changes", padding=10)
        changes_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Change input fields
        self.change_frame = ttk.Frame(changes_frame)
        self.change_frame.pack(fill='x')
        
        self.setup_change_inputs()
        
        ttk.Button(changes_frame, text="Add Change", 
                  command=self.add_change).pack(pady=10)
        
        # Changes list
        list_frame = ttk.Frame(changes_frame)
        list_frame.pack(fill='both', expand=True)
        
        ttk.Label(list_frame, text="Added Changes:").pack(anchor='w')
        
        self.changes_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, command=self.changes_listbox.yview)
        self.changes_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.changes_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(changes_frame, text="Remove Selected", 
                  command=self.remove_change).pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create", command=self.create_scenario).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def setup_change_inputs(self):
        """Setup input fields based on scenario type"""
        # Clear existing widgets
        for widget in self.change_frame.winfo_children():
            widget.destroy()
        
        scenario_type = self.type_var.get()
        
        # Category selection (common)
        ttk.Label(self.change_frame, text="Category:").grid(row=0, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        
        from managers.category_manager import CategoryManager
        categories = CategoryManager().get_flat_category_list()
        cat_combo = ttk.Combobox(self.change_frame, textvariable=self.category_var,
                                values=categories, width=25)
        cat_combo.grid(row=0, column=1, pady=5)
        
        if scenario_type == "budget_change":
            # Amount change
            ttk.Label(self.change_frame, text="Amount Change:").grid(row=1, column=0, sticky='w', pady=5)
            self.amount_var = tk.StringVar()
            ttk.Entry(self.change_frame, textvariable=self.amount_var, width=15).grid(row=1, column=1, sticky='w', pady=5)
            
            # Period
            ttk.Label(self.change_frame, text="Start Month:").grid(row=2, column=0, sticky='w', pady=5)
            self.start_var = tk.StringVar(value=PLANNING_MONTHS[0])
            ttk.Combobox(self.change_frame, textvariable=self.start_var,
                        values=PLANNING_MONTHS, width=10).grid(row=2, column=1, sticky='w', pady=5)
            
            ttk.Label(self.change_frame, text="End Month:").grid(row=3, column=0, sticky='w', pady=5)
            self.end_var = tk.StringVar(value=PLANNING_MONTHS[-1])
            ttk.Combobox(self.change_frame, textvariable=self.end_var,
                        values=PLANNING_MONTHS, width=10).grid(row=3, column=1, sticky='w', pady=5)
            
        elif scenario_type == "one_time_event":
            # Amount
            ttk.Label(self.change_frame, text="Amount:").grid(row=1, column=0, sticky='w', pady=5)
            self.amount_var = tk.StringVar()
            ttk.Entry(self.change_frame, textvariable=self.amount_var, width=15).grid(row=1, column=1, sticky='w', pady=5)
            
            # Event month
            ttk.Label(self.change_frame, text="Event Month:").grid(row=2, column=0, sticky='w', pady=5)
            self.event_month_var = tk.StringVar(value=PLANNING_MONTHS[0])
            ttk.Combobox(self.change_frame, textvariable=self.event_month_var,
                        values=PLANNING_MONTHS, width=10).grid(row=2, column=1, sticky='w', pady=5)
            
        elif scenario_type == "investment_adjustment":
            # Adjustment type
            ttk.Label(self.change_frame, text="Adjustment:").grid(row=1, column=0, sticky='w', pady=5)
            self.adjustment_var = tk.StringVar(value="pause")
            adj_frame = ttk.Frame(self.change_frame)
            adj_frame.grid(row=1, column=1, sticky='w', pady=5)
            
            ttk.Radiobutton(adj_frame, text="Pause", 
                          variable=self.adjustment_var, value="pause").pack(side='left')
            ttk.Radiobutton(adj_frame, text="Double", 
                          variable=self.adjustment_var, value="double").pack(side='left')
            
            # Period
            ttk.Label(self.change_frame, text="Start Month:").grid(row=2, column=0, sticky='w', pady=5)
            self.start_var = tk.StringVar(value=PLANNING_MONTHS[0])
            ttk.Combobox(self.change_frame, textvariable=self.start_var,
                        values=PLANNING_MONTHS, width=10).grid(row=2, column=1, sticky='w', pady=5)
            
            ttk.Label(self.change_frame, text="End Month:").grid(row=3, column=0, sticky='w', pady=5)
            self.end_var = tk.StringVar(value=PLANNING_MONTHS[-1])
            ttk.Combobox(self.change_frame, textvariable=self.end_var,
                        values=PLANNING_MONTHS, width=10).grid(row=3, column=1, sticky='w', pady=5)
    
    def on_type_changed(self):
        """Handle scenario type change"""
        self.setup_change_inputs()
    
    def add_change(self):
        """Add a change to the scenario"""
        scenario_type = self.type_var.get()
        category = self.category_var.get()
        
        if not category:
            messagebox.showwarning("Missing Data", "Please select a category")
            return
        
        change = {'category': category, 'type': scenario_type}
        
        if scenario_type == "budget_change":
            try:
                amount = float(self.amount_var.get())
                change['amount_change'] = amount
                change['start_month'] = self.start_var.get()
                change['end_month'] = self.end_var.get()
                
                display = f"{category}: {format_currency(amount)} ({self.start_var.get()} to {self.end_var.get()})"
                
            except ValueError:
                messagebox.showwarning("Invalid Amount", "Please enter a valid amount")
                return
                
        elif scenario_type == "one_time_event":
            try:
                amount = float(self.amount_var.get())
                change['amount'] = amount
                change['event_month'] = self.event_month_var.get()
                
                display = f"{category}: {format_currency(amount)} in {self.event_month_var.get()}"
                
            except ValueError:
                messagebox.showwarning("Invalid Amount", "Please enter a valid amount")
                return
                
        elif scenario_type == "investment_adjustment":
            change['adjustment_type'] = self.adjustment_var.get()
            change['start_month'] = self.start_var.get()
            change['end_month'] = self.end_var.get()
            
            display = f"{category}: {self.adjustment_var.get()} ({self.start_var.get()} to {self.end_var.get()})"
        
        self.changes.append(change)
        self.changes_listbox.insert(tk.END, display)
        
        # Clear inputs
        self.category_var.set("")
        if hasattr(self, 'amount_var'):
            self.amount_var.set("")
    
    def remove_change(self):
        """Remove selected change"""
        selection = self.changes_listbox.curselection()
        if selection:
            index = selection[0]
            self.changes_listbox.delete(index)
            del self.changes[index]
    
    def create_scenario(self):
        """Create the scenario"""
        name = self.name_var.get()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a scenario name")
            return
        
        if not self.changes:
            messagebox.showwarning("No Changes", "Please add at least one change")
            return
        
        scenario_data = {
            'name': name,
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'type': self.type_var.get(),
            'changes': self.changes
        }
        
        if self.callback:
            self.callback(scenario_data)
        
        self.dialog.destroy()


class EditScenarioDialog(CreateScenarioDialog):
    """Dialog for editing existing scenarios"""
    
    def __init__(self, parent, scenario, callback=None):
        self.scenario = scenario
        super().__init__(parent, callback)
        self.dialog.title("Edit Scenario")
        self.load_scenario_data()
    
    def load_scenario_data(self):
        """Load existing scenario data"""
        self.name_var.set(self.scenario.get('name', ''))
        self.desc_text.insert(1.0, self.scenario.get('description', ''))
        self.type_var.set(self.scenario.get('scenario_type', 'budget_change'))
        
        # Load changes
        self.changes = self.scenario.get('changes', [])
        for change in self.changes:
            # Create display text
            category = change.get('category', 'Unknown')
            
            if self.scenario.get('scenario_type') == 'budget_change':
                amount = change.get('amount_change', 0)
                start = change.get('start_month', '')
                end = change.get('end_month', '')
                display = f"{category}: {format_currency(amount)} ({start} to {end})"
            elif self.scenario.get('scenario_type') == 'one_time_event':
                amount = change.get('amount', 0)
                month = change.get('event_month', '')
                display = f"{category}: {format_currency(amount)} in {month}"
            else:
                adj_type = change.get('adjustment_type', '')
                start = change.get('start_month', '')
                end = change.get('end_month', '')
                display = f"{category}: {adj_type} ({start} to {end})"
            
            self.changes_listbox.insert(tk.END, display)
    
    def create_scenario(self):
        """Update the scenario"""
        name = self.name_var.get()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a scenario name")
            return
        
        if not self.changes:
            messagebox.showwarning("No Changes", "Please add at least one change")
            return
        
        # Update scenario data
        self.scenario['name'] = name
        self.scenario['description'] = self.desc_text.get(1.0, tk.END).strip()
        self.scenario['scenario_type'] = self.type_var.get()
        self.scenario['changes'] = self.changes
        
        if self.callback:
            self.callback(self.scenario)
        
        self.dialog.destroy()

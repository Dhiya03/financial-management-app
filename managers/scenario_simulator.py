"""
What-if scenario simulation manager
"""

import logging
from typing import Dict, List, Any, Tuple
from copy import deepcopy
from datetime import datetime

from models.scenario import Scenario
from config import PLANNING_MONTHS

class ScenarioSimulator:
    """Simulates what-if scenarios"""
    
    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
        from managers.budget_manager import BudgetManager
        self.budget_manager = BudgetManager()
    
    def create_scenario(self, name: str, description: str, scenario_type: str, 
                       changes: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Create a new scenario"""
        try:
            scenario = Scenario(
                name=name,
                description=description,
                scenario_type=scenario_type,
                changes=changes
            )
            
            # Add to data
            self.app_data.scenarios[scenario.id] = scenario.to_dict()
            
            # Save changes
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Created scenario: {name}")
                return True, "Scenario created successfully"
            else:
                return False, "Failed to save scenario"
                
        except Exception as e:
            logging.error(f"Error creating scenario: {e}")
            return False, f"Error creating scenario: {str(e)}"
    
    def simulate_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Simulate a scenario and return impact analysis"""
        try:
            scenario = self.app_data.scenarios.get(scenario_id)
            if not scenario:
                return {'error': 'Scenario not found'}
            
            # Create copies of current budgets
            original_budgets = deepcopy(self.app_data.budgets)
            simulated_budgets = deepcopy(self.app_data.budgets)
            
            # Apply scenario changes
            for change in scenario['changes']:
                self.apply_change(simulated_budgets, change)
            
            # Calculate impact
            impact = self.calculate_impact(original_budgets, simulated_budgets, scenario)
            
            return {
                'scenario': scenario,
                'impact': impact,
                'original_budgets': original_budgets,
                'simulated_budgets': simulated_budgets
            }
            
        except Exception as e:
            logging.error(f"Error simulating scenario: {e}")
            return {'error': f'Simulation failed: {str(e)}'}
    
    def apply_change(self, budgets: Dict[str, Dict[str, float]], change: Dict[str, Any]):
        """Apply a single change to budget data"""
        change_type = change.get('type', 'budget_change')
        category = change.get('category')
        start_month = change.get('start_month')
        end_month = change.get('end_month')
        
        if change_type == 'budget_change':
            # Apply budget changes across months
            amount_change = change.get('amount_change', 0)
            
            start_idx = PLANNING_MONTHS.index(start_month) if start_month in PLANNING_MONTHS else 0
            end_idx = PLANNING_MONTHS.index(end_month) if end_month in PLANNING_MONTHS else len(PLANNING_MONTHS) - 1
            
            for i in range(start_idx, end_idx + 1):
                month = PLANNING_MONTHS[i]
                if month not in budgets:
                    budgets[month] = {}
                if category not in budgets[month]:
                    budgets[month][category] = 0
                
                budgets[month][category] += amount_change
                
        elif change_type == 'one_time_event':
            # Apply one-time event
            event_month = change.get('event_month', start_month)
            amount = change.get('amount', 0)
            
            if event_month in budgets:
                if category not in budgets[event_month]:
                    budgets[event_month][category] = 0
                budgets[event_month][category] += amount
                
        elif change_type == 'investment_adjustment':
            # Handle investment adjustments
            adjustment_type = change.get('adjustment_type', 'pause')
            
            if adjustment_type == 'pause':
                # Set category to 0 for specified months
                start_idx = PLANNING_MONTHS.index(start_month) if start_month in PLANNING_MONTHS else 0
                end_idx = PLANNING_MONTHS.index(end_month) if end_month in PLANNING_MONTHS else len(PLANNING_MONTHS) - 1
                
                for i in range(start_idx, end_idx + 1):
                    month = PLANNING_MONTHS[i]
                    if month in budgets and category in budgets[month]:
                        budgets[month][category] = 0
            
            elif adjustment_type == 'double':
                # Double the investment amount
                start_idx = PLANNING_MONTHS.index(start_month) if start_month in PLANNING_MONTHS else 0
                end_idx = PLANNING_MONTHS.index(end_month) if end_month in PLANNING_MONTHS else len(PLANNING_MONTHS) - 1
                
                for i in range(start_idx, end_idx + 1):
                    month = PLANNING_MONTHS[i]
                    if month in budgets and category in budgets[month]:
                        budgets[month][category] *= 2
    
    def calculate_impact(self, original: Dict[str, Dict[str, float]], 
                        simulated: Dict[str, Dict[str, float]], 
                        scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of scenario on budgets"""
        try:
            impact = {
                'monthly_changes': {},
                'total_impact': 0,
                'affected_months': 0,
                'category_impact': {},
                'summary': {}
            }
            
            # Calculate monthly changes
            for month in PLANNING_MONTHS:
                original_month = original.get(month, {})
                simulated_month = simulated.get(month, {})
                
                original_total = sum(original_month.values())
                simulated_total = sum(simulated_month.values())
                month_change = simulated_total - original_total
                
                if month_change != 0:
                    impact['monthly_changes'][month] = {
                        'original_total': original_total,
                        'simulated_total': simulated_total,
                        'change': month_change,
                        'change_percent': (month_change / original_total * 100) if original_total > 0 else 0
                    }
                    impact['affected_months'] += 1
                    impact['total_impact'] += month_change
            
            # Calculate category impact
            all_categories = set()
            for month_budgets in list(original.values()) + list(simulated.values()):
                all_categories.update(month_budgets.keys())
            
            for category in all_categories:
                original_cat_total = sum(month_budgets.get(category, 0) for month_budgets in original.values())
                simulated_cat_total = sum(month_budgets.get(category, 0) for month_budgets in simulated.values())
                cat_change = simulated_cat_total - original_cat_total
                
                if cat_change != 0:
                    impact['category_impact'][category] = {
                        'original_total': original_cat_total,
                        'simulated_total': simulated_cat_total,
                        'change': cat_change
                    }
            
            # Generate summary
            impact['summary'] = self.generate_impact_summary(impact, scenario)
            
            return impact
            
        except Exception as e:
            logging.error(f"Error calculating impact: {e}")
            return {'error': f'Impact calculation failed: {str(e)}'}
    
    def generate_impact_summary(self, impact: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable impact summary"""
        total_impact = impact['total_impact']
        affected_months = impact['affected_months']
        
        summary = {
            'net_change': total_impact,
            'affected_periods': affected_months,
            'impact_type': 'increase' if total_impact > 0 else 'decrease' if total_impact < 0 else 'neutral',
            'recommendation': '',
            'risk_level': 'low'
        }
        
        # Determine risk level and recommendation
        if abs(total_impact) < 10000:
            summary['recommendation'] = 'Low impact scenario - manageable changes'
            summary['risk_level'] = 'low'
        elif abs(total_impact) < 50000:
            summary['recommendation'] = 'Moderate impact - review budget allocations'
            summary['risk_level'] = 'medium'
        else:
            summary['recommendation'] = 'High impact scenario - significant budget review required'
            summary['risk_level'] = 'high'
        
        return summary
    
    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """Get all saved scenarios"""
        return list(self.app_data.scenarios.values())
    
    def delete_scenario(self, scenario_id: str) -> Tuple[bool, str]:
        """Delete a scenario"""
        try:
            if scenario_id not in self.app_data.scenarios:
                return False, "Scenario not found"
            
            scenario_name = self.app_data.scenarios[scenario_id]['name']
            del self.app_data.scenarios[scenario_id]
            
            from managers.data_manager import data_manager
            if data_manager.save():
                logging.info(f"Deleted scenario: {scenario_name}")
                return True, "Scenario deleted successfully"
            else:
                return False, "Failed to save changes"
                
        except Exception as e:
            logging.error(f"Error deleting scenario: {e}")
            return False, f"Error deleting scenario: {str(e)}"

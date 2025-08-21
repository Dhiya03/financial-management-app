"""
Scenario data model for what-if simulations
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any
from uuid import uuid4

def generate_unique_id() -> str:
    """Generate unique ID for scenarios"""
    return str(uuid4())

@dataclass
class Scenario:
    """What-if scenario data model"""
    id: str = field(default_factory=generate_unique_id)
    name: str = ""
    description: str = ""
    scenario_type: str = ""  # budget_change, one_time_event, investment_adjustment
    changes: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scenario_type": self.scenario_type,
            "changes": self.changes,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """Create instance from dictionary"""
        return cls(**data)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate scenario data"""
        errors = []
        
        if not self.name:
            errors.append("Scenario name is required")
        
        valid_types = ["budget_change", "one_time_event", "investment_adjustment"]
        if self.scenario_type not in valid_types:
            errors.append(f"Invalid scenario type. Must be one of: {', '.join(valid_types)}")
        
        if not self.changes:
            errors.append("At least one change is required")
        
        return len(errors) == 0, errors
    
    def add_change(self, change: Dict[str, Any]):
        """Add a change to the scenario"""
        self.changes.append(change)
    
    def remove_change(self, index: int):
        """Remove a change by index"""
        if 0 <= index < len(self.changes):
            del self.changes[index]
    
    def get_summary(self) -> str:
        """Get a summary of the scenario"""
        change_count = len(self.changes)
        if self.scenario_type == "budget_change":
            return f"Budget changes: {change_count} modifications"
        elif self.scenario_type == "one_time_event":
            return f"One-time events: {change_count} events"
        elif self.scenario_type == "investment_adjustment":
            return f"Investment adjustments: {change_count} changes"
        else:
            return f"{change_count} changes"

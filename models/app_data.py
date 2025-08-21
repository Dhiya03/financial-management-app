"""
Main application data model
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class AppData:
    """Main application data model"""
    categories: Dict[str, List[str]] = field(default_factory=dict)
    budgets: Dict[str, Dict[str, float]] = field(default_factory=dict)
    transactions: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    scenarios: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "categories": self.categories,
            "budgets": self.budgets,
            "transactions": self.transactions,
            "scenarios": self.scenarios,
            "settings": self.settings,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppData':
        """Create instance from dictionary"""
        return cls(
            categories=data.get("categories", {}),
            budgets=data.get("budgets", {}),
            transactions=data.get("transactions", {}),
            scenarios=data.get("scenarios", {}),
            settings=data.get("settings", {}),
            metadata=data.get("metadata", {})
        )

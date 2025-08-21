"""
Budget data model
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Budget:
    """Budget data model"""
    month: str
    category: str
    amount: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "month": self.month,
            "category": self.category,
            "amount": self.amount
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """Create instance from dictionary"""
        return cls(**data)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate budget data"""
        errors = []

        if not self.month:
            errors.append("Month is required")

        if not self.category:
            errors.append("Category is required")

        if self.amount < 0:
            errors.append("Amount cannot be negative")

        return len(errors) == 0, errors

"""
Transaction data model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

def generate_unique_id() -> str:
    """Generate unique ID for transactions"""
    return str(uuid4())

@dataclass
class Transaction:
    """Transaction data model"""
    id: str = field(default_factory=generate_unique_id)
    date: str = ""
    category: str = ""
    amount: float = 0.0
    description: str = ""
    source: str = "manual"  # manual, imported, auto_categorized
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "source": self.source,
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create instance from dictionary"""
        return cls(**data)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate transaction data"""
        errors = []
        
        if not self.date:
            errors.append("Date is required")
        
        if not self.category:
            errors.append("Category is required")
        
        if self.amount <= 0:
            errors.append("Amount must be positive")
        
        return len(errors) == 0, errors

#!/bin/bash

# Financial Management Tool - Project Setup Script
# This script creates the complete project structure

echo "Creating Financial Management Tool project structure..."

# Create main project directory
PROJECT_DIR="financial_management_tool"
mkdir -p $PROJECT_DIR

# Create subdirectories
echo "Creating directories..."
mkdir -p $PROJECT_DIR/models
mkdir -p $PROJECT_DIR/managers
mkdir -p $PROJECT_DIR/gui/tabs
mkdir -p $PROJECT_DIR/gui/dialogs
mkdir -p $PROJECT_DIR/utils
mkdir -p $PROJECT_DIR/resources/templates
mkdir -p $PROJECT_DIR/resources/sample_data

# Create __init__.py files for Python packages
echo "Creating __init__.py files..."
touch $PROJECT_DIR/__init__.py
touch $PROJECT_DIR/models/__init__.py
touch $PROJECT_DIR/managers/__init__.py
touch $PROJECT_DIR/gui/__init__.py
touch $PROJECT_DIR/gui/tabs/__init__.py
touch $PROJECT_DIR/gui/dialogs/__init__.py
touch $PROJECT_DIR/utils/__init__.py

# Create placeholder files for remaining modules
echo "Creating placeholder files..."

# Create remaining model files
cat > $PROJECT_DIR/models/budget.py << 'EOF'
"""Budget data model"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class Budget:
    """Budget data model"""
    month: str
    category: str
    amount: float
    
    def to_dict(self) -> Dict:
        return {
            "month": self.month,
            "category": self.category,
            "amount": self.amount
        }
EOF

# Create remaining tab files
cat > $PROJECT_DIR/gui/tabs/analysis_tab.py << 'EOF'
"""Category analysis tab"""
import tkinter as tk
from tkinter import ttk

class AnalysisTab:
    """Category analysis tab with analytics"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup analysis tab UI"""
        label = ttk.Label(self.frame, text="Category Analysis - Coming Soon")
        label.pack(pady=20)
    
    def refresh(self):
        """Refresh analysis data"""
        pass
EOF

cat > $PROJECT_DIR/gui/tabs/simulator_tab.py << 'EOF'
"""What-if simulator tab"""
import tkinter as tk
from tkinter import ttk

class SimulatorTab:
    """What-if simulator tab"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup simulator tab UI"""
        label = ttk.Label(self.frame, text="What-If Simulator - Coming Soon")
        label.pack(pady=20)
    
    def refresh(self):
        """Refresh simulator data"""
        pass
EOF

cat > $PROJECT_DIR/gui/tabs/reports_tab.py << 'EOF'
"""Reports and export tab"""
import tkinter as tk
from tkinter import ttk

class ReportsTab:
    """Reports and export tab"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup reports tab UI"""
        label = ttk.Label(self.frame, text="Reports & Export - Coming Soon")
        label.pack(pady=20)
    
    def refresh(self):
        """Refresh reports data"""
        pass
EOF

# Create dialog files
cat > $PROJECT_DIR/gui/dialogs/template_dialog.py << 'EOF'
"""Budget template dialog"""
import tkinter as tk
from tkinter import ttk

class TemplateDialog:
    """Dialog for applying budget templates"""
    
    def __init__(self, parent, current_month, callback=None):
        self.parent = parent
        self.current_month = current_month
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Apply Budget Template")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        label = ttk.Label(self.dialog, text="Template Dialog - Coming Soon")
        label.pack(pady=20)
EOF

# Create analytics engine
cat > $PROJECT_DIR/managers/analytics_engine.py << 'EOF'
"""Analytics and insights engine"""
import logging
from typing import Dict, List, Any

class AnalyticsEngine:
    """Provides advanced analytics and insights"""
    
    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()
    
    def get_spending_trends(self, months: List[str], category: str = None) -> Dict[str, Any]:
        """Get spending trends over time"""
        # Placeholder implementation
        return {'data': {}, 'trend_direction': 'stable', 'average': 0}
    
    def get_category_performance(self) -> List[Dict[str, Any]]:
        """Get performance analysis for all categories"""
        # Placeholder implementation
        return []
EOF

# Create utilities
cat > $PROJECT_DIR/utils/file_handlers.py << 'EOF'
"""File import/export utilities"""
import csv
import json
from typing import List, Dict, Any

def export_to_csv(data: List[Dict[str, Any]], file_path: str):
    """Export data to CSV file"""
    if not data:
        return
    
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def export_to_json(data: Dict[str, Any], file_path: str):
    """Export data to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
EOF

# Create sample data
cat > $PROJECT_DIR/resources/sample_data/sample_transactions.csv << 'EOF'
Date,Category,Amount,Description,Source
2025-08-01,Credit Card EMI 1,15000,Monthly EMI Payment,manual
2025-08-05,Mutual Fund SIP,5000,SIP Investment,manual
2025-08-10,Hospital,8500,Medical Consultation,imported
2025-08-15,Swiggy/Food,1250,Food Delivery,imported
2025-08-20,Petrol,3000,Fuel,manual
2025-08-25,Shopping,5500,Amazon Purchase,imported
EOF

# Create budget templates
cat > $PROJECT_DIR/resources/templates/budget_templates.json << 'EOF'
{
  "Conservative": {
    "Credit Card EMI 1": 15000,
    "Mutual Fund SIP": 5000,
    "Hospital": 8000,
    "Swiggy/Food": 3000,
    "Petrol": 3000,
    "Shopping": 5000
  },
  "Moderate": {
    "Credit Card EMI 1": 15000,
    "Mutual Fund SIP": 7000,
    "Hospital": 10000,
    "Swiggy/Food": 5000,
    "Petrol": 4000,
    "Shopping": 8000
  },
  "Aggressive": {
    "Credit Card EMI 1": 15000,
    "Mutual Fund SIP": 10000,
    "Hospital": 12000,
    "Swiggy/Food": 8000,
    "Petrol": 5000,
    "Shopping": 12000
  }
}
EOF

echo "Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. pip install -r requirements.txt"
echo "3. python main.py"
echo ""
echo "Files created:"
find $PROJECT_DIR -type f -name "*.py" | wc -l
echo "Python files created"

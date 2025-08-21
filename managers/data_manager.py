"""
Data persistence and loading manager
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import shutil

from config import AppSettings
from models.app_data import AppData

class DataManager:
    """Manages data persistence and loading"""
    
    def __init__(self):
        self.data_file = AppSettings.APP_DATA_FILE
        self.backup_dir = AppSettings.BACKUP_DIR
        self.app_data: AppData = AppData()
        self._ensure_directories()
        self._load_data()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        AppSettings.ensure_directories()
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Get default data structure for new installations"""
        from config import DEFAULT_CATEGORIES, CATEGORY_KEYWORDS
        
        return {
            "categories": DEFAULT_CATEGORIES.copy(),
            "budgets": {},
            "transactions": {},
            "scenarios": {},
            "settings": {
                "alert_threshold": AppSettings.DEFAULT_ALERT_THRESHOLD,
                "currency": AppSettings.DEFAULT_CURRENCY,
                "last_selected_month": "Aug-25",
                "category_keywords": CATEGORY_KEYWORDS.copy()
            },
            "metadata": {
                "version": AppSettings.APP_VERSION,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat()
            }
        }
    
    def _load_data(self):
        """Load data from JSON file or create default"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.app_data = AppData.from_dict(data)
                logging.info("Data loaded successfully")
            else:
                default_data = self._get_default_data()
                self.app_data = AppData.from_dict(default_data)
                self._save_data()
                logging.info("Created new data file with defaults")
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            self.app_data = AppData.from_dict(self._get_default_data())
    
    def _save_data(self) -> bool:
        """Save data to JSON file"""
        try:
            self.app_data.metadata["last_modified"] = datetime.now().isoformat()
            
            # Create backup if file exists
            if self.data_file.exists():
                self._create_backup()
            
            # Save data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_data.to_dict(), f, indent=2, ensure_ascii=False)
            
            logging.info("Data saved successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to save data: {e}")
            return False
    
    def _create_backup(self):
        """Create backup of current data file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(self.data_file, backup_path)
            logging.info(f"Backup created: {backup_path}")
            self._cleanup_old_backups()
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.now().timestamp() - (AppSettings.BACKUP_RETENTION_DAYS * 24 * 3600)
            for backup_file in self.backup_dir.glob("auto_backup_*.json"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    logging.info(f"Deleted old backup: {backup_file}")
        except Exception as e:
            logging.error(f"Failed to cleanup old backups: {e}")
    
    def get_data(self) -> AppData:
        """Get current application data"""
        return self.app_data
    
    def save(self) -> bool:
        """Save current data"""
        return self._save_data()
    
    def backup(self, backup_name: Optional[str] = None) -> Optional[Path]:
        """Create manual backup"""
        try:
            if backup_name:
                backup_path = self.backup_dir / f"{backup_name}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"manual_backup_{timestamp}.json"
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.app_data.to_dict(), f, indent=2, ensure_ascii=False)
            
            logging.info(f"Manual backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
            return None
    
    def restore(self, backup_path: Path) -> bool:
        """Restore data from backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create backup of current data before restore
            self.backup("pre_restore")
            
            # Restore data
            self.app_data = AppData.from_dict(data)
            self._save_data()
            
            logging.info(f"Data restored from: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to restore from backup: {e}")
            return False

# Global data manager instance
data_manager = DataManager()

#!/usr/bin/env python3
"""
Financial Management & Simulation Tool - Main Entry Point
Version: 2.0.0
Description: Personal finance tracking and planning tool with 2-year projection capabilities
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from config import AppSettings
from gui.main_window import FinancialManagementApp

def main():
    """Main application entry point"""
    try:
        # Setup logging
        logger = setup_logging()
        logger.info(f"Starting {AppSettings.APP_NAME} v{AppSettings.APP_VERSION}")
        
        # Ensure directories exist
        AppSettings.ensure_directories()
        
        # Create and run the application
        app = FinancialManagementApp()
        app.run()
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

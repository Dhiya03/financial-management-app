"""
Logging configuration for the application
"""

import logging
import logging.handlers
from pathlib import Path
from config import AppSettings

def setup_logging():
    """Setup application logging with file and console handlers"""
    AppSettings.ensure_directories()
    log_dir = AppSettings.LOG_DIR
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    root_logger.info("="*50)
    root_logger.info(f"Starting {AppSettings.APP_NAME} v{AppSettings.APP_VERSION}")
    root_logger.info("="*50)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)

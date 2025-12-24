# validation/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logger():
    """Setup lightweight logging for validation system"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger('validation')
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # File handler only - rotating file (5MB max per file, keep 3 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/validation.log',
        maxBytes=5242880,  # 5MB
        backupCount=2  # Only keep 2 old logs
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Simple format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

validation_logger = setup_logger()
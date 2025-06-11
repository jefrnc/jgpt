import logging
import os
from datetime import datetime
from colorlog import ColoredFormatter


def setup_logger(name: str = 'trading_bot', log_level: str = 'INFO') -> logging.Logger:
    """Setup a colored logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    console_format = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    
    # File handler
    log_filename = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
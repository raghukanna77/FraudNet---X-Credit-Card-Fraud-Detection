"""
Logging utilities for FraudNet-X
"""

import sys
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logger(log_dir: Path = None, log_level: str = "INFO"):
    """
    Configure logger with file and console output
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # File handler if log_dir provided
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"fraudnet_x_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            log_file,
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level
        )
    
    return logger


# Initialize default logger
from ..utils.config import Config
logger = setup_logger(Config.LOGS_DIR)

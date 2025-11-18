"""Application logger setup."""

import logging
import sys
from typing import Optional

from ...shared.constants import LOG_FORMAT, LOG_DATE_FORMAT


_loggers = {}


def setup_logger(
    name: str = 'sagittarius_entj',
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup and configure a logger.
    
    Args:
        name: Logger name.
        level: Logging level (e.g., logging.INFO, logging.DEBUG).
        log_file: Optional file path to write logs to.
        
    Returns:
        Configured logger instance.
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.warning(f"Failed to create log file '{log_file}': {e}")
    
    _loggers[name] = logger
    return logger


def get_logger(name: str = 'sagittarius_entj') -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name.
        
    Returns:
        Logger instance.
    """
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)

"""
Logger - Logging configuration for Bgpt.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Global logger instance
_logger: Optional[logging.Logger] = None

def setup_logger(name: str = "bgpt", level: str = "INFO") -> logging.Logger:
    """Setup main logger."""
    global _logger
    
    if _logger is not None:
        return _logger
        
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)  # Only show warnings and errors on console
        console_formatter = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            log_dir = Path.home() / ".bgpt" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "bgpt.log")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue without it
            pass
    
    _logger = logger
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger for module."""
    # Ensure main logger is initialized
    if _logger is None:
        setup_logger()
    return logging.getLogger(f"bgpt.{name}")

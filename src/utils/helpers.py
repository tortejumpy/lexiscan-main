"""
Utility functions for LexiScan Auto
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def setup_logging(log_file: str = None, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_file: Path to log file (optional)
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def ensure_dir(directory: str) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """
    Get project root directory
    
    Returns:
        Project root path
    """
    return Path(__file__).parent.parent.parent


class EntityLabels:
    """Entity label constants"""
    PARTY = "PARTY"
    DATE = "DATE"
    AMOUNT = "AMOUNT"
    JURISDICTION = "JURISDICTION"
    TERM = "TERM"
    
    @classmethod
    def all_labels(cls):
        """Get all entity labels"""
        return [cls.PARTY, cls.DATE, cls.AMOUNT, cls.JURISDICTION, cls.TERM]
    
    @classmethod
    def to_iob2(cls, label: str, position: str = "B") -> str:
        """
        Convert label to IOB2 format
        
        Args:
            label: Entity label
            position: B (Beginning) or I (Inside)
            
        Returns:
            IOB2 formatted label
        """
        if position not in ["B", "I", "O"]:
            raise ValueError("Position must be B, I, or O")
        
        if position == "O":
            return "O"
        
        return f"{position}-{label}"

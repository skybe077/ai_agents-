# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 09:43:21 2025

Logging Configuration Script
Provides a reusable logger setup for AI agents and database utilities.

Usage:
    from logging_config import get_logger
    logger = get_logger("my_logger_name")

@author: ET
"""
import logging

def get_logger(name, log_file="app.log", level=logging.DEBUG):
    """Creates and returns a logger with the specified name and log file."""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if the logger already has handlers to prevent duplicates
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def close_log_handlers(logger):
    """Close all handlers of a given logger to allow log file deletion."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

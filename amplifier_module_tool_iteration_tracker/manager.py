"""
Iteration Tracker Manager

Manages the lifecycle of iteration boards and storage.
"""

import logging
from pathlib import Path
from typing import Any

from .board import IterationBoard
from .storage import IterationStorage

logger = logging.getLogger(__name__)


def get_iterations_data_directory() -> Path:
    """
    Get the data directory for iteration tracker storage.
    
    Returns:
        Path to ~/.amplifier/iterations/ directory
    """
    data_dir = Path.home() / ".amplifier" / "iterations"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class IterationTrackerManager:
    """Manages iteration board and storage instances."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the iteration tracker manager.

        Args:
            config: Configuration dictionary with optional settings
        """
        self.config = config
        self.board = IterationBoard()
        self.storage = IterationStorage(get_iterations_data_directory())

    async def start(self):
        """Start the manager and initialize resources."""
        logger.info("Starting Iteration Tracker manager")
        # Add any initialization logic here if needed

    async def stop(self):
        """Stop the manager and clean up resources."""
        logger.info("Stopping Iteration Tracker manager")
        # Add any cleanup logic here if needed

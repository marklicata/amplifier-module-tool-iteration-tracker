"""
Iteration Tracker Manager

Manages the lifecycle of iteration boards and storage.
"""

import logging
from typing import Any

from .board import IterationBoard
from .storage import IterationStorage

logger = logging.getLogger(__name__)


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
        self.storage = IterationStorage()

    async def start(self):
        """Start the manager and initialize resources."""
        logger.info("Starting Iteration Tracker manager")
        # Add any initialization logic here if needed

    async def stop(self):
        """Stop the manager and clean up resources."""
        logger.info("Stopping Iteration Tracker manager")
        # Add any cleanup logic here if needed

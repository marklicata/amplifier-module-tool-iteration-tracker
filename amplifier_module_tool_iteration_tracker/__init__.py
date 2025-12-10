"""
Amplifier Iteration Tracker - Iteration-centric planning and tracking.

This module provides iteration/sprint planning tools where the Iteration
is the central entity that all queries flow through.
"""

import logging
from typing import Any

try:
    from amplifier_core import ModuleCoordinator
except ImportError:
    ModuleCoordinator = None

from .models import (
    Issue,
    IssueStatus,
    IssueType,
    Priority,
    Iteration,
    IterationStatus,
)
from .board import IterationBoard
from .query import IssueQuery
from .natural_language import parse_query, ask
from .storage import IterationStorage
from .config import (
    GitHubRepoConfig,
    TrackerConfig,
    ConfigManager,
)
from .manager import IterationTrackerManager
from .tools import (
    CreateIterationTool,
    ListIterationsTool,
    QueryIssuesTool,
    AskNaturalLanguageTool,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


async def mount(coordinator: "ModuleCoordinator", config: dict[str, Any] | None = None):
    """
    Mount the Iteration Tracker module with Amplifier.

    This function is the entry point called by Amplifier to initialize and
    register the iteration tracking tools.

    Args:
        coordinator: The ModuleCoordinator instance for registering capabilities
        config: Optional configuration dictionary with settings

    Returns:
        Async cleanup function to be called when the module is unmounted
    """
    config = config or {}

    logger.info("Mounting Iteration Tracker module...")

    try:
        # Initialize the manager
        manager = IterationTrackerManager(config)
        await manager.start()

        # Create tool instances
        tools = [
            CreateIterationTool(manager),
            ListIterationsTool(manager),
            QueryIssuesTool(manager),
            AskNaturalLanguageTool(manager),
        ]

        # Register each tool with the coordinator
        for tool in tools:
            await coordinator.mount("tools", tool, name=tool.name)
            logger.debug(f"Mounted Iteration Tracker tool: {tool.name}")

        logger.info(f"Iteration Tracker module mounted successfully with {len(tools)} tools")

        # Return cleanup function
        async def cleanup():
            logger.info("Cleaning up Iteration Tracker module...")
            await manager.stop()

        return cleanup

    except Exception as e:
        logger.error(f"Failed to mount Iteration Tracker module: {e}")
        return None


__all__ = [
    "mount",
    # Core models
    "Issue",
    "IssueStatus",
    "IssueType",
    "Priority",
    "Iteration",
    "IterationStatus",
    # Board
    "IterationBoard",
    # Query
    "IssueQuery",
    # Natural language
    "parse_query",
    "ask",
    # Storage
    "IterationStorage",
    # Configuration
    "GitHubRepoConfig",
    "TrackerConfig",
    "ConfigManager",
    # Manager
    "IterationTrackerManager",
    # Tools
    "CreateIterationTool",
    "ListIterationsTool",
    "QueryIssuesTool",
    "AskNaturalLanguageTool",
]

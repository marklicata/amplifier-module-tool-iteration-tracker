"""
Amplifier Iteration Tracker - Iteration-centric planning and tracking.

This module provides iteration/sprint planning tools where the Iteration
is the central entity that all queries flow through.
"""

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

__version__ = "1.0.0"

__all__ = [
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
]

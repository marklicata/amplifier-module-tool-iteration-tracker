"""Base class for Iteration Tracker tools."""

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import IterationTrackerManager

try:
    from amplifier_core import ToolResult
except ImportError:
    # Fallback for testing without amplifier-core
    class ToolResult:
        def __init__(self, success: bool, output: dict | None = None, error: dict | None = None):
            self.success = success
            self.output = output or {}
            self.error = error or {}

logger = logging.getLogger(__name__)


class IterationTrackerBaseTool:
    """Base class for all Iteration Tracker tools."""

    def __init__(self, manager: "IterationTrackerManager"):
        """
        Initialize the tool.

        Args:
            manager: The IterationTrackerManager instance
        """
        self.manager = manager

    @property
    def name(self) -> str:
        """Tool name - must be implemented by subclasses."""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """Tool description - must be implemented by subclasses."""
        raise NotImplementedError

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON schema for tool input - must be implemented by subclasses."""
        raise NotImplementedError

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """
        Execute the tool.

        Args:
            input_data: Input parameters matching the input_schema

        Returns:
            ToolResult with success status and output/error data
        """
        raise NotImplementedError

    async def __call__(self, input_data: dict[str, Any]) -> ToolResult:
        """Callable interface for the tool."""
        return await self.execute(input_data)

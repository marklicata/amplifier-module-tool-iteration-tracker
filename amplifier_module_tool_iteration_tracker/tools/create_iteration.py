"""Create Iteration Tool."""

from typing import Any
from datetime import date

from .base import IterationTrackerBaseTool, ToolResult
from ..models import IterationStatus


class CreateIterationTool(IterationTrackerBaseTool):
    """Tool for creating a new iteration/sprint."""

    @property
    def name(self) -> str:
        return "iteration_create"

    @property
    def description(self) -> str:
        return "Create a new iteration/sprint with a name, optional dates, goal, and status."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the iteration (e.g., 'Sprint 1', 'Q1 2025')"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in ISO format (YYYY-MM-DD), optional",
                    "format": "date"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in ISO format (YYYY-MM-DD), optional",
                    "format": "date"
                },
                "goal": {
                    "type": "string",
                    "description": "Goal or objective for this iteration",
                    "default": ""
                },
                "status": {
                    "type": "string",
                    "enum": ["planning", "active", "completed"],
                    "description": "Status of the iteration",
                    "default": "planning"
                }
            },
            "required": ["name"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute the create iteration tool."""
        try:
            name = input_data["name"]
            start_date_str = input_data.get("start_date")
            end_date_str = input_data.get("end_date")
            goal = input_data.get("goal", "")
            status_str = input_data.get("status", "planning")

            # Parse dates if provided
            start_date = date.fromisoformat(start_date_str) if start_date_str else None
            end_date = date.fromisoformat(end_date_str) if end_date_str else None

            # Parse status
            status = IterationStatus[status_str.upper()]

            # Create the iteration
            iteration = self.manager.board.create_iteration(
                name=name,
                start_date=start_date,
                end_date=end_date,
                goal=goal,
                status=status,
            )

            return ToolResult(
                success=True,
                output={
                    "iteration": {
                        "name": iteration.name,
                        "start_date": iteration.start_date.isoformat() if iteration.start_date else None,
                        "end_date": iteration.end_date.isoformat() if iteration.end_date else None,
                        "goal": iteration.goal,
                        "status": iteration.status.value,
                    },
                    "message": f"Created iteration '{name}'"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Failed to create iteration: {str(e)}"
                }
            )

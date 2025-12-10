"""List Iterations Tool."""

from typing import Any

from .base import IterationTrackerBaseTool, ToolResult


class ListIterationsTool(IterationTrackerBaseTool):
    """Tool for listing all iterations."""

    @property
    def name(self) -> str:
        return "iteration_list"

    @property
    def description(self) -> str:
        return "List all iterations/sprints with their details."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute the list iterations tool."""
        try:
            iterations = self.manager.board.list_iterations()

            result = {
                "iterations": [
                    {
                        "name": iteration.name,
                        "start_date": iteration.start_date.isoformat() if iteration.start_date else None,
                        "end_date": iteration.end_date.isoformat() if iteration.end_date else None,
                        "goal": iteration.goal,
                        "status": iteration.status.value,
                        "issue_count": len(iteration.issues),
                    }
                    for iteration in iterations
                ],
                "count": len(iterations)
            }

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Failed to list iterations: {str(e)}"
                }
            )

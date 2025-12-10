"""Ask Natural Language Tool."""

from typing import Any

from .base import IterationTrackerBaseTool, ToolResult
from ..natural_language import ask


class AskNaturalLanguageTool(IterationTrackerBaseTool):
    """Tool for asking natural language questions about iterations and issues."""

    @property
    def name(self) -> str:
        return "iteration_ask"

    @property
    def description(self) -> str:
        return (
            "Ask natural language questions about iterations and issues. "
            "Examples: 'What is Emily working on?', 'How many bugs are left?', "
            "'Show blocked issues'"
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language question about iterations or issues"
                }
            },
            "required": ["question"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute the natural language query tool."""
        try:
            question = input_data["question"]

            # Use the ask function from natural_language module
            answer = ask(
                question=question,
                board=self.manager.board
            )

            return ToolResult(
                success=True,
                output={
                    "question": question,
                    "answer": answer
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Failed to process question: {str(e)}"
                }
            )

"""Query Issues Tool."""

from typing import Any

from .base import IterationTrackerBaseTool, ToolResult


class QueryIssuesTool(IterationTrackerBaseTool):
    """Tool for querying issues with filters."""

    @property
    def name(self) -> str:
        return "iteration_query_issues"

    @property
    def description(self) -> str:
        return "Query and filter issues across iterations by assignee, status, type, priority, etc."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "iteration": {
                    "type": "string",
                    "description": "Name or partial name of the iteration to query (optional)"
                },
                "assignee": {
                    "type": "string",
                    "description": "Filter by assignee name (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "in_progress", "blocked", "closed"],
                    "description": "Filter by issue status (optional)"
                },
                "issue_type": {
                    "type": "string",
                    "enum": ["bug", "feature", "story", "task"],
                    "description": "Filter by issue type (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Filter by priority (optional)"
                },
                "label": {
                    "type": "string",
                    "description": "Filter by label (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 100
                }
            },
            "required": []
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute the query issues tool."""
        try:
            iteration_name = input_data.get("iteration")
            assignee = input_data.get("assignee")
            status = input_data.get("status")
            issue_type = input_data.get("issue_type")
            priority = input_data.get("priority")
            label = input_data.get("label")
            limit = input_data.get("limit", 100)

            # Get issues from board
            if iteration_name:
                iteration = self.manager.board.get_iteration(iteration_name)
                if not iteration:
                    return ToolResult(
                        success=False,
                        error={"message": f"Iteration '{iteration_name}' not found"}
                    )
                issues = list(iteration.issues.values())
            else:
                issues = list(self.manager.board._issues.values())

            # Apply filters
            filtered_issues = issues

            if assignee:
                assignee_lower = assignee.lower()
                filtered_issues = [
                    i for i in filtered_issues
                    if i.assignee and assignee_lower in i.assignee.lower()
                ]

            if status:
                filtered_issues = [
                    i for i in filtered_issues
                    if i.status.value == status
                ]

            if issue_type:
                filtered_issues = [
                    i for i in filtered_issues
                    if i.issue_type.value == issue_type
                ]

            if priority:
                filtered_issues = [
                    i for i in filtered_issues
                    if i.priority.value == priority
                ]

            if label:
                filtered_issues = [
                    i for i in filtered_issues
                    if label in i.labels
                ]

            # Apply limit
            filtered_issues = filtered_issues[:limit]

            # Format results
            result = {
                "issues": [
                    {
                        "id": issue.id,
                        "title": issue.title,
                        "status": issue.status.value,
                        "type": issue.issue_type.value,
                        "priority": issue.priority.value,
                        "assignee": issue.assignee,
                        "labels": issue.labels,
                        "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    }
                    for issue in filtered_issues
                ],
                "count": len(filtered_issues),
                "total_matches": len([i for i in issues if i in filtered_issues])
            }

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Failed to query issues: {str(e)}"
                }
            )

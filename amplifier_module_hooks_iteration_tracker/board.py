"""
IterationBoard - manages multiple iterations and provides cross-iteration queries.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .models import Iteration, IterationStatus, Issue, IssueStatus, IssueType, Priority


@dataclass
class IterationBoard:
    """
    Manages multiple iterations and provides cross-iteration operations.
    
    The board is the top-level container:
        board.create_iteration("Sprint 3", ...)
        board.current()  # Get active iteration
        board.by_assignee("emily")  # Query across all iterations
    """
    _iterations: dict[str, Iteration] = field(default_factory=dict)
    _issues: dict[str, Issue] = field(default_factory=dict)

    # -------------------------------------------------------------------------
    # Iteration management
    # -------------------------------------------------------------------------

    def create_iteration(
        self,
        name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        goal: str = "",
        status: IterationStatus = IterationStatus.PLANNING,
    ) -> Iteration:
        """Create a new iteration."""
        iteration = Iteration(
            name=name,
            start_date=start_date,
            end_date=end_date,
            goal=goal,
            status=status,
        )
        self._iterations[name] = iteration
        return iteration

    def get_iteration(self, name: str) -> Optional[Iteration]:
        """Get an iteration by name (case-insensitive partial match)."""
        name_lower = name.lower()
        # Exact match first
        if name in self._iterations:
            return self._iterations[name]
        # Partial match
        for iter_name, iteration in self._iterations.items():
            if name_lower in iter_name.lower():
                return iteration
        return None

    def delete_iteration(self, name: str) -> bool:
        """Delete an iteration."""
        if name in self._iterations:
            del self._iterations[name]
            return True
        return False

    def list_iterations(self) -> list[Iteration]:
        """List all iterations ordered by start date."""
        return sorted(
            self._iterations.values(),
            key=lambda i: i.start_date or date.min
        )

    # -------------------------------------------------------------------------
    # Iteration navigation
    # -------------------------------------------------------------------------

    def current(self) -> Optional[Iteration]:
        """Get the currently active iteration."""
        for iteration in self._iterations.values():
            if iteration.status == IterationStatus.ACTIVE:
                return iteration
        return None

    def next(self) -> Optional[Iteration]:
        """Get the next planned iteration."""
        planning = [
            i for i in self._iterations.values()
            if i.status == IterationStatus.PLANNING
        ]
        if not planning:
            return None
        return min(planning, key=lambda i: i.start_date or date.max)

    def previous(self) -> Optional[Iteration]:
        """Get the most recently completed iteration."""
        completed = [
            i for i in self._iterations.values()
            if i.status == IterationStatus.COMPLETED
        ]
        if not completed:
            return None
        return max(completed, key=lambda i: i.end_date or date.min)

    def active_iterations(self) -> list[Iteration]:
        """Get all active iterations."""
        return [
            i for i in self._iterations.values()
            if i.status == IterationStatus.ACTIVE
        ]

    def completed_iterations(self) -> list[Iteration]:
        """Get all completed iterations, ordered by end date."""
        completed = [
            i for i in self._iterations.values()
            if i.status == IterationStatus.COMPLETED
        ]
        return sorted(completed, key=lambda i: i.end_date or date.min)

    # -------------------------------------------------------------------------
    # Issue management
    # -------------------------------------------------------------------------

    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the board and its iteration."""
        self._issues[issue.id] = issue
        if issue.iteration and issue.iteration in self._iterations:
            self._iterations[issue.iteration].add_issue(issue)

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get an issue by ID."""
        return self._issues.get(issue_id)

    def move_issue(self, issue_id: str, to_iteration: str) -> bool:
        """Move an issue to a different iteration."""
        issue = self._issues.get(issue_id)
        if not issue:
            return False
        
        # Remove from current iteration
        if issue.iteration and issue.iteration in self._iterations:
            self._iterations[issue.iteration].remove_issue(issue_id)
        
        # Add to new iteration
        if to_iteration in self._iterations:
            self._iterations[to_iteration].add_issue(issue)
            return True
        return False

    def all_issues(self) -> list[Issue]:
        """Get all issues across all iterations."""
        return list(self._issues.values())

    # -------------------------------------------------------------------------
    # Cross-iteration queries
    # -------------------------------------------------------------------------

    def by_assignee(self, name: str) -> list[Issue]:
        """Get all issues assigned to a person across all iterations."""
        name_lower = name.lower()
        return [
            i for i in self._issues.values()
            if i.assignee and name_lower in i.assignee.lower()
        ]

    def by_author(self, name: str) -> list[Issue]:
        """Get all issues created by a person across all iterations."""
        name_lower = name.lower()
        return [
            i for i in self._issues.values()
            if i.author and name_lower in i.author.lower()
        ]

    def by_label(self, label: str) -> list[Issue]:
        """Get all issues with a label across all iterations."""
        label_lower = label.lower()
        return [
            i for i in self._issues.values()
            if any(label_lower in l.lower() for l in i.labels)
        ]

    def blocked_issues(self) -> list[Issue]:
        """Get all blocked issues across all iterations."""
        return [i for i in self._issues.values() if i.is_blocked]

    def open_issues(self) -> list[Issue]:
        """Get all open issues across all iterations."""
        return [i for i in self._issues.values() if i.is_open]

    def unassigned_issues(self) -> list[Issue]:
        """Get all unassigned issues across all iterations."""
        return [i for i in self._issues.values() if not i.assignee]

    # -------------------------------------------------------------------------
    # Velocity tracking
    # -------------------------------------------------------------------------

    def velocity_history(self, count: int = 5) -> list[dict]:
        """
        Get velocity for the last N completed iterations.
        
        Returns list of {"iteration": name, "velocity": points}
        """
        completed = self.completed_iterations()[-count:]
        return [
            {"iteration": i.name, "velocity": i.velocity}
            for i in completed
        ]

    def average_velocity(self, count: int = 3) -> float:
        """Calculate average velocity over last N completed iterations."""
        history = self.velocity_history(count)
        if not history:
            return 0.0
        return sum(h["velocity"] for h in history) / len(history)

    def velocity_trend(self, count: int = 5) -> str:
        """Determine if velocity is trending up, down, or stable."""
        history = self.velocity_history(count)
        if len(history) < 2:
            return "insufficient_data"
        
        velocities = [h["velocity"] for h in history]
        first_half = sum(velocities[:len(velocities)//2]) / (len(velocities)//2)
        second_half = sum(velocities[len(velocities)//2:]) / (len(velocities) - len(velocities)//2)
        
        diff_percent = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
        
        if diff_percent > 10:
            return "increasing"
        elif diff_percent < -10:
            return "decreasing"
        return "stable"

    # -------------------------------------------------------------------------
    # Team workload
    # -------------------------------------------------------------------------

    def team_workload(self, iteration_name: Optional[str] = None) -> dict[str, dict]:
        """
        Get workload breakdown by team member.
        
        Returns: {
            "Emily": {"total": 5, "in_progress": 2, "blocked": 1, "points": 13},
            ...
        }
        """
        if iteration_name:
            iteration = self.get_iteration(iteration_name)
            issues = iteration.issues() if iteration else []
        else:
            issues = list(self._issues.values())
        
        workload: dict[str, dict] = {}
        for issue in issues:
            name = issue.assignee or "Unassigned"
            if name not in workload:
                workload[name] = {
                    "total": 0,
                    "open": 0,
                    "in_progress": 0,
                    "blocked": 0,
                    "done": 0,
                    "points": 0,
                }
            workload[name]["total"] += 1
            workload[name]["points"] += issue.story_points
            
            if issue.is_open:
                workload[name]["open"] += 1
            if issue.status == IssueStatus.IN_PROGRESS:
                workload[name]["in_progress"] += 1
            if issue.is_blocked:
                workload[name]["blocked"] += 1
            if issue.status == IssueStatus.DONE:
                workload[name]["done"] += 1
        
        return workload

    # -------------------------------------------------------------------------
    # Natural language
    # -------------------------------------------------------------------------

    def ask(self, question: str) -> list[Issue] | dict | int | str:
        """
        Ask a question in natural language across all iterations.
        
        Examples:
            board.ask("What is Emily working on?")
            board.ask("Show all blocked issues")
        """
        from .natural_language import ask as nl_ask
        return nl_ask(question, list(self._issues.values()))

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize board to dictionary."""
        return {
            "iterations": [
                {
                    "name": i.name,
                    "start_date": i.start_date.isoformat() if i.start_date else None,
                    "end_date": i.end_date.isoformat() if i.end_date else None,
                    "status": i.status.value,
                    "goal": i.goal,
                }
                for i in self._iterations.values()
            ],
            "issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "status": i.status.value,
                    "issue_type": i.issue_type.value,
                    "priority": i.priority.value,
                    "assignee": i.assignee,
                    "author": i.author,
                    "iteration": i.iteration,
                    "labels": i.labels,
                    "story_points": i.story_points,
                    "created_at": i.created_at.isoformat(),
                    "updated_at": i.updated_at.isoformat(),
                    "closed_at": i.closed_at.isoformat() if i.closed_at else None,
                    "blocked_by": i.blocked_by,
                    "blocks": i.blocks,
                    "parent_id": i.parent_id,
                    "metadata": i.metadata,
                }
                for i in self._issues.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IterationBoard":
        """Deserialize board from dictionary."""
        from datetime import datetime
        
        board = cls()
        
        # Load iterations
        for iter_data in data.get("iterations", []):
            board.create_iteration(
                name=iter_data["name"],
                start_date=date.fromisoformat(iter_data["start_date"]) if iter_data.get("start_date") else None,
                end_date=date.fromisoformat(iter_data["end_date"]) if iter_data.get("end_date") else None,
                goal=iter_data.get("goal", ""),
                status=IterationStatus(iter_data.get("status", "planning")),
            )
        
        # Load issues
        for issue_data in data.get("issues", []):
            issue = Issue(
                id=issue_data["id"],
                title=issue_data["title"],
                description=issue_data.get("description", ""),
                status=IssueStatus(issue_data.get("status", "todo")),
                issue_type=IssueType(issue_data.get("issue_type", "task")),
                priority=Priority(issue_data.get("priority", "medium")),
                assignee=issue_data.get("assignee"),
                author=issue_data.get("author"),
                iteration=issue_data.get("iteration"),
                labels=issue_data.get("labels", []),
                story_points=issue_data.get("story_points", 0),
                created_at=datetime.fromisoformat(issue_data["created_at"]) if issue_data.get("created_at") else datetime.now(),
                updated_at=datetime.fromisoformat(issue_data["updated_at"]) if issue_data.get("updated_at") else datetime.now(),
                closed_at=datetime.fromisoformat(issue_data["closed_at"]) if issue_data.get("closed_at") else None,
                blocked_by=issue_data.get("blocked_by"),
                blocks=issue_data.get("blocks", []),
                parent_id=issue_data.get("parent_id"),
                metadata=issue_data.get("metadata", {}),
            )
            board.add_issue(issue)
        
        return board

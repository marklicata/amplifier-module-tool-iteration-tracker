"""
Core models for iteration tracking.

The Iteration is the central entity - all queries flow through it.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class IssueStatus(Enum):
    """Status of an issue."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class IssueType(Enum):
    """Type of issue."""
    STORY = "story"
    BUG = "bug"
    TASK = "task"
    SPIKE = "spike"
    EPIC = "epic"


class Priority(Enum):
    """Priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IterationStatus(Enum):
    """Status of an iteration."""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Issue:
    """
    An issue/ticket in the system.
    
    Attributes:
        id: Unique identifier (e.g., "PROJ-123")
        title: Short description
        description: Full description
        status: Current status
        issue_type: Type of issue (story, bug, task, etc.)
        priority: Priority level
        assignee: Person assigned to work on it
        author: Person who created it
        iteration: Which iteration this belongs to
        labels: Tags/labels for categorization
        story_points: Estimated effort
        created_at: When created
        updated_at: Last update time
        closed_at: When closed (if closed)
        blocked_by: Issue ID that blocks this
        blocks: List of issue IDs this blocks
        parent_id: Parent issue (for subtasks)
        metadata: Additional custom fields
    """
    id: str
    title: str
    description: str = ""
    status: IssueStatus = IssueStatus.TODO
    issue_type: IssueType = IssueType.TASK
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    author: Optional[str] = None
    iteration: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    story_points: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    blocked_by: Optional[str] = None
    blocks: list[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def is_open(self) -> bool:
        """Check if issue is open (not done or cancelled)."""
        return self.status not in (IssueStatus.DONE, IssueStatus.CANCELLED)
    
    @property
    def is_closed(self) -> bool:
        """Check if issue is closed."""
        return not self.is_open
    
    @property
    def is_blocked(self) -> bool:
        """Check if issue is blocked."""
        return self.status == IssueStatus.BLOCKED or self.blocked_by is not None


@dataclass
class Iteration:
    """
    An iteration/sprint - the central entity for planning.
    
    All queries flow through the Iteration object:
        iteration.open()
        iteration.by_assignee("emily")
        iteration.ask("How many bugs left?")
    """
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: IterationStatus = IterationStatus.PLANNING
    goal: str = ""
    _issues: list[Issue] = field(default_factory=list, repr=False)

    def issues(self) -> list[Issue]:
        """Get all issues in this iteration."""
        return self._issues.copy()
    
    def add_issue(self, issue: Issue) -> None:
        """Add an issue to this iteration."""
        issue.iteration = self.name
        self._issues.append(issue)
    
    def remove_issue(self, issue_id: str) -> bool:
        """Remove an issue from this iteration."""
        for i, issue in enumerate(self._issues):
            if issue.id == issue_id:
                self._issues.pop(i)
                return True
        return False

    # -------------------------------------------------------------------------
    # Status-based queries
    # -------------------------------------------------------------------------

    def open(self) -> list[Issue]:
        """Get all open issues (not done/cancelled)."""
        return [i for i in self._issues if i.is_open]
    
    def closed(self) -> list[Issue]:
        """Get all closed issues."""
        return [i for i in self._issues if i.is_closed]
    
    def done(self) -> list[Issue]:
        """Get successfully completed issues."""
        return [i for i in self._issues if i.status == IssueStatus.DONE]
    
    def cancelled(self) -> list[Issue]:
        """Get cancelled issues."""
        return [i for i in self._issues if i.status == IssueStatus.CANCELLED]
    
    def blocked(self) -> list[Issue]:
        """Get blocked issues."""
        return [i for i in self._issues if i.is_blocked]
    
    def in_progress(self) -> list[Issue]:
        """Get issues currently being worked on."""
        return [i for i in self._issues if i.status == IssueStatus.IN_PROGRESS]
    
    def in_review(self) -> list[Issue]:
        """Get issues in review."""
        return [i for i in self._issues if i.status == IssueStatus.IN_REVIEW]
    
    def todo(self) -> list[Issue]:
        """Get issues not yet started."""
        return [i for i in self._issues if i.status == IssueStatus.TODO]

    # -------------------------------------------------------------------------
    # People-based queries
    # -------------------------------------------------------------------------

    def by_assignee(self, name: str) -> list[Issue]:
        """Get issues assigned to a person (case-insensitive partial match)."""
        name_lower = name.lower()
        return [i for i in self._issues 
                if i.assignee and name_lower in i.assignee.lower()]
    
    def by_author(self, name: str) -> list[Issue]:
        """Get issues created by a person (case-insensitive partial match)."""
        name_lower = name.lower()
        return [i for i in self._issues 
                if i.author and name_lower in i.author.lower()]
    
    def unassigned(self) -> list[Issue]:
        """Get issues with no assignee."""
        return [i for i in self._issues if not i.assignee]

    # -------------------------------------------------------------------------
    # Type-based queries
    # -------------------------------------------------------------------------

    def bugs(self) -> list[Issue]:
        """Get all bugs."""
        return [i for i in self._issues if i.issue_type == IssueType.BUG]
    
    def stories(self) -> list[Issue]:
        """Get all user stories."""
        return [i for i in self._issues if i.issue_type == IssueType.STORY]
    
    def tasks(self) -> list[Issue]:
        """Get all tasks."""
        return [i for i in self._issues if i.issue_type == IssueType.TASK]
    
    def spikes(self) -> list[Issue]:
        """Get all spikes (research/investigation)."""
        return [i for i in self._issues if i.issue_type == IssueType.SPIKE]
    
    def by_type(self, issue_type: IssueType) -> list[Issue]:
        """Get issues of a specific type."""
        return [i for i in self._issues if i.issue_type == issue_type]

    # -------------------------------------------------------------------------
    # Label/priority queries
    # -------------------------------------------------------------------------

    def by_label(self, label: str) -> list[Issue]:
        """Get issues with a specific label (case-insensitive)."""
        label_lower = label.lower()
        return [i for i in self._issues 
                if any(label_lower in l.lower() for l in i.labels)]
    
    def by_labels(self, labels: list[str], match_all: bool = False) -> list[Issue]:
        """Get issues matching labels (any or all)."""
        labels_lower = [l.lower() for l in labels]
        if match_all:
            return [i for i in self._issues 
                    if all(any(l in il.lower() for il in i.labels) for l in labels_lower)]
        return [i for i in self._issues 
                if any(any(l in il.lower() for il in i.labels) for l in labels_lower)]
    
    def critical(self) -> list[Issue]:
        """Get critical priority issues."""
        return [i for i in self._issues if i.priority == Priority.CRITICAL]
    
    def high_priority(self) -> list[Issue]:
        """Get high and critical priority issues."""
        return [i for i in self._issues 
                if i.priority in (Priority.CRITICAL, Priority.HIGH)]
    
    def by_priority(self, priority: Priority) -> list[Issue]:
        """Get issues of a specific priority."""
        return [i for i in self._issues if i.priority == priority]

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def total_points(self) -> int:
        """Total story points in this iteration."""
        return sum(i.story_points for i in self._issues)
    
    @property
    def completed_points(self) -> int:
        """Story points completed."""
        return sum(i.story_points for i in self.done())
    
    @property
    def remaining_points(self) -> int:
        """Story points remaining."""
        return sum(i.story_points for i in self.open())
    
    @property
    def completion_percent(self) -> float:
        """Percentage of points completed."""
        if self.total_points == 0:
            return 0.0
        return (self.completed_points / self.total_points) * 100
    
    @property
    def velocity(self) -> int:
        """Velocity = completed story points."""
        return self.completed_points
    
    @property
    def days_remaining(self) -> int:
        """Days until iteration end."""
        if not self.end_date:
            return 0
        delta = self.end_date - date.today()
        return max(0, delta.days)
    
    @property
    def days_elapsed(self) -> int:
        """Days since iteration start."""
        if not self.start_date:
            return 0
        delta = date.today() - self.start_date
        return max(0, delta.days)
    
    @property
    def total_days(self) -> int:
        """Total duration in days."""
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days

    # -------------------------------------------------------------------------
    # Groupings
    # -------------------------------------------------------------------------

    def group_by_assignee(self) -> dict[str, list[Issue]]:
        """Group issues by assignee."""
        groups: dict[str, list[Issue]] = {}
        for issue in self._issues:
            key = issue.assignee or "Unassigned"
            groups.setdefault(key, []).append(issue)
        return groups
    
    def group_by_status(self) -> dict[str, list[Issue]]:
        """Group issues by status."""
        groups: dict[str, list[Issue]] = {}
        for issue in self._issues:
            key = issue.status.value
            groups.setdefault(key, []).append(issue)
        return groups
    
    def group_by_type(self) -> dict[str, list[Issue]]:
        """Group issues by type."""
        groups: dict[str, list[Issue]] = {}
        for issue in self._issues:
            key = issue.issue_type.value
            groups.setdefault(key, []).append(issue)
        return groups
    
    def group_by_priority(self) -> dict[str, list[Issue]]:
        """Group issues by priority."""
        groups: dict[str, list[Issue]] = {}
        for issue in self._issues:
            key = issue.priority.value
            groups.setdefault(key, []).append(issue)
        return groups
    
    def group_by_label(self) -> dict[str, list[Issue]]:
        """Group issues by label (issue appears in multiple groups if multi-labeled)."""
        groups: dict[str, list[Issue]] = {}
        for issue in self._issues:
            if not issue.labels:
                groups.setdefault("Unlabeled", []).append(issue)
            else:
                for label in issue.labels:
                    groups.setdefault(label, []).append(issue)
        return groups

    # -------------------------------------------------------------------------
    # Natural language interface
    # -------------------------------------------------------------------------

    def ask(self, question: str) -> list[Issue] | dict | int | str:
        """
        Ask a question in natural language.
        
        Examples:
            iteration.ask("What is Emily working on?")
            iteration.ask("How many bugs are left?")
            iteration.ask("Show blocked issues")
        """
        from .natural_language import ask as nl_ask
        return nl_ask(question, self._issues, self)

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(self) -> dict:
        """Get iteration summary statistics."""
        return {
            "name": self.name,
            "status": self.status.value,
            "goal": self.goal,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "days_remaining": self.days_remaining,
            "total_issues": len(self._issues),
            "open_issues": len(self.open()),
            "closed_issues": len(self.closed()),
            "blocked_issues": len(self.blocked()),
            "total_points": self.total_points,
            "completed_points": self.completed_points,
            "remaining_points": self.remaining_points,
            "completion_percent": round(self.completion_percent, 1),
            "velocity": self.velocity,
        }

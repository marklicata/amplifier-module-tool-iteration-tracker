"""
Fluent query builder for complex issue queries.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable

from .models import Issue, IssueStatus, IssueType, Priority


@dataclass
class IssueQuery:
    """
    Fluent query builder for filtering and sorting issues.
    
    Example:
        results = (
            IssueQuery(issues)
            .assignee("emily")
            .is_open()
            .by_priority()
            .limit(10)
            .execute()
        )
    """
    _issues: list[Issue]
    _filters: list[Callable[[Issue], bool]] = field(default_factory=list)
    _sort_key: Optional[Callable[[Issue], any]] = None
    _sort_reverse: bool = False
    _limit_count: Optional[int] = None
    _offset_count: int = 0

    def __post_init__(self):
        # Make a copy to avoid mutating original
        self._issues = list(self._issues)
        self._filters = list(self._filters)

    def _clone(self) -> "IssueQuery":
        """Create a clone of this query."""
        q = IssueQuery(self._issues)
        q._filters = list(self._filters)
        q._sort_key = self._sort_key
        q._sort_reverse = self._sort_reverse
        q._limit_count = self._limit_count
        q._offset_count = self._offset_count
        return q

    # -------------------------------------------------------------------------
    # Status filters
    # -------------------------------------------------------------------------

    def is_open(self) -> "IssueQuery":
        """Filter to open issues only."""
        q = self._clone()
        q._filters.append(lambda i: i.is_open)
        return q

    def is_closed(self) -> "IssueQuery":
        """Filter to closed issues only."""
        q = self._clone()
        q._filters.append(lambda i: i.is_closed)
        return q

    def is_blocked(self) -> "IssueQuery":
        """Filter to blocked issues only."""
        q = self._clone()
        q._filters.append(lambda i: i.is_blocked)
        return q

    def status(self, *statuses: IssueStatus) -> "IssueQuery":
        """Filter by one or more statuses."""
        q = self._clone()
        q._filters.append(lambda i: i.status in statuses)
        return q

    # -------------------------------------------------------------------------
    # People filters
    # -------------------------------------------------------------------------

    def assignee(self, name: str) -> "IssueQuery":
        """Filter by assignee (case-insensitive partial match)."""
        q = self._clone()
        name_lower = name.lower()
        q._filters.append(lambda i: i.assignee and name_lower in i.assignee.lower())
        return q

    def author(self, name: str) -> "IssueQuery":
        """Filter by author (case-insensitive partial match)."""
        q = self._clone()
        name_lower = name.lower()
        q._filters.append(lambda i: i.author and name_lower in i.author.lower())
        return q

    def unassigned(self) -> "IssueQuery":
        """Filter to unassigned issues."""
        q = self._clone()
        q._filters.append(lambda i: not i.assignee)
        return q

    # -------------------------------------------------------------------------
    # Type filters
    # -------------------------------------------------------------------------

    def issue_type(self, *types: IssueType) -> "IssueQuery":
        """Filter by one or more issue types."""
        q = self._clone()
        q._filters.append(lambda i: i.issue_type in types)
        return q

    def bugs(self) -> "IssueQuery":
        """Filter to bugs only."""
        return self.issue_type(IssueType.BUG)

    def stories(self) -> "IssueQuery":
        """Filter to stories only."""
        return self.issue_type(IssueType.STORY)

    def tasks(self) -> "IssueQuery":
        """Filter to tasks only."""
        return self.issue_type(IssueType.TASK)

    # -------------------------------------------------------------------------
    # Priority filters
    # -------------------------------------------------------------------------

    def priority(self, *priorities: Priority) -> "IssueQuery":
        """Filter by one or more priorities."""
        q = self._clone()
        q._filters.append(lambda i: i.priority in priorities)
        return q

    def critical(self) -> "IssueQuery":
        """Filter to critical priority."""
        return self.priority(Priority.CRITICAL)

    def high_priority(self) -> "IssueQuery":
        """Filter to high and critical priority."""
        return self.priority(Priority.CRITICAL, Priority.HIGH)

    # -------------------------------------------------------------------------
    # Label/iteration filters
    # -------------------------------------------------------------------------

    def label(self, label: str) -> "IssueQuery":
        """Filter by label (case-insensitive partial match)."""
        q = self._clone()
        label_lower = label.lower()
        q._filters.append(lambda i: any(label_lower in l.lower() for l in i.labels))
        return q

    def labels(self, labels: list[str], match_all: bool = False) -> "IssueQuery":
        """Filter by multiple labels (any or all)."""
        q = self._clone()
        labels_lower = [l.lower() for l in labels]
        if match_all:
            q._filters.append(
                lambda i: all(any(l in il.lower() for il in i.labels) for l in labels_lower)
            )
        else:
            q._filters.append(
                lambda i: any(any(l in il.lower() for il in i.labels) for l in labels_lower)
            )
        return q

    def iteration(self, name: str) -> "IssueQuery":
        """Filter by iteration (case-insensitive partial match)."""
        q = self._clone()
        name_lower = name.lower()
        q._filters.append(lambda i: i.iteration and name_lower in i.iteration.lower())
        return q

    # -------------------------------------------------------------------------
    # Custom filter
    # -------------------------------------------------------------------------

    def where(self, predicate: Callable[[Issue], bool]) -> "IssueQuery":
        """Add a custom filter predicate."""
        q = self._clone()
        q._filters.append(predicate)
        return q

    # -------------------------------------------------------------------------
    # Sorting
    # -------------------------------------------------------------------------

    def by_priority(self, descending: bool = True) -> "IssueQuery":
        """Sort by priority (critical first by default)."""
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }
        q = self._clone()
        q._sort_key = lambda i: priority_order.get(i.priority, 99)
        q._sort_reverse = not descending  # Lower number = higher priority
        return q

    def by_created(self, descending: bool = True) -> "IssueQuery":
        """Sort by creation date."""
        q = self._clone()
        q._sort_key = lambda i: i.created_at
        q._sort_reverse = descending
        return q

    def by_updated(self, descending: bool = True) -> "IssueQuery":
        """Sort by update date."""
        q = self._clone()
        q._sort_key = lambda i: i.updated_at
        q._sort_reverse = descending
        return q

    def by_points(self, descending: bool = True) -> "IssueQuery":
        """Sort by story points."""
        q = self._clone()
        q._sort_key = lambda i: i.story_points
        q._sort_reverse = descending
        return q

    def by_assignee(self) -> "IssueQuery":
        """Sort by assignee name."""
        q = self._clone()
        q._sort_key = lambda i: i.assignee or "zzz"  # Unassigned at end
        q._sort_reverse = False
        return q

    def order_by(self, key: Callable[[Issue], any], descending: bool = False) -> "IssueQuery":
        """Sort by custom key."""
        q = self._clone()
        q._sort_key = key
        q._sort_reverse = descending
        return q

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------

    def limit(self, count: int) -> "IssueQuery":
        """Limit number of results."""
        q = self._clone()
        q._limit_count = count
        return q

    def offset(self, count: int) -> "IssueQuery":
        """Skip first N results."""
        q = self._clone()
        q._offset_count = count
        return q

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------

    def execute(self) -> list[Issue]:
        """Execute query and return results."""
        results = self._issues
        
        # Apply filters
        for f in self._filters:
            results = [i for i in results if f(i)]
        
        # Apply sorting
        if self._sort_key:
            results = sorted(results, key=self._sort_key, reverse=self._sort_reverse)
        
        # Apply pagination
        if self._offset_count:
            results = results[self._offset_count:]
        if self._limit_count is not None:
            results = results[:self._limit_count]
        
        return results

    def count(self) -> int:
        """Count matching issues (ignores limit/offset)."""
        results = self._issues
        for f in self._filters:
            results = [i for i in results if f(i)]
        return len(results)

    def exists(self) -> bool:
        """Check if any issues match."""
        return self.count() > 0

    def first(self) -> Optional[Issue]:
        """Get first matching issue."""
        results = self.limit(1).execute()
        return results[0] if results else None

    def stats(self) -> dict:
        """Get aggregate statistics for matching issues."""
        results = self.execute()
        open_issues = [i for i in results if i.is_open]
        closed_issues = [i for i in results if i.is_closed]
        
        return {
            "total": len(results),
            "open": len(open_issues),
            "closed": len(closed_issues),
            "blocked": len([i for i in results if i.is_blocked]),
            "points": sum(i.story_points for i in results),
            "open_points": sum(i.story_points for i in open_issues),
            "closed_points": sum(i.story_points for i in closed_issues),
        }

    # -------------------------------------------------------------------------
    # Grouping
    # -------------------------------------------------------------------------

    def group_by_assignee(self) -> dict[str, list[Issue]]:
        """Group results by assignee."""
        results = self.execute()
        groups: dict[str, list[Issue]] = {}
        for issue in results:
            key = issue.assignee or "Unassigned"
            groups.setdefault(key, []).append(issue)
        return groups

    def group_by_status(self) -> dict[str, list[Issue]]:
        """Group results by status."""
        results = self.execute()
        groups: dict[str, list[Issue]] = {}
        for issue in results:
            key = issue.status.value
            groups.setdefault(key, []).append(issue)
        return groups

    def group_by_type(self) -> dict[str, list[Issue]]:
        """Group results by issue type."""
        results = self.execute()
        groups: dict[str, list[Issue]] = {}
        for issue in results:
            key = issue.issue_type.value
            groups.setdefault(key, []).append(issue)
        return groups

    def group_by(self, key_fn: Callable[[Issue], str]) -> dict[str, list[Issue]]:
        """Group results by custom key function."""
        results = self.execute()
        groups: dict[str, list[Issue]] = {}
        for issue in results:
            key = key_fn(issue)
            groups.setdefault(key, []).append(issue)
        return groups

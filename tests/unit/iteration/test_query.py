"""Tests for IssueQuery fluent builder."""

import pytest
from datetime import datetime

from amplifier_module_hooks_iteration_tracker import (
    IssueQuery, Issue, IssueStatus, IssueType, Priority,
)


class TestIssueQuery:
    """Tests for IssueQuery fluent builder."""
    
    @pytest.fixture
    def issues(self):
        """Create test issues."""
        return [
            Issue(id="BUG-1", title="Critical bug", status=IssueStatus.IN_PROGRESS,
                  issue_type=IssueType.BUG, priority=Priority.CRITICAL,
                  assignee="Emily", labels=["backend"], story_points=5),
            Issue(id="BUG-2", title="Minor bug", status=IssueStatus.TODO,
                  issue_type=IssueType.BUG, priority=Priority.LOW,
                  assignee="John", labels=["frontend"], story_points=2),
            Issue(id="STORY-1", title="New feature", status=IssueStatus.DONE,
                  issue_type=IssueType.STORY, priority=Priority.HIGH,
                  assignee="Emily", labels=["backend", "api"], story_points=8),
            Issue(id="TASK-1", title="Refactor", status=IssueStatus.BLOCKED,
                  issue_type=IssueType.TASK, priority=Priority.MEDIUM,
                  assignee="John", labels=["tech-debt"], story_points=3),
            Issue(id="TASK-2", title="Docs", status=IssueStatus.TODO,
                  issue_type=IssueType.TASK, priority=Priority.LOW,
                  assignee=None, labels=[], story_points=1),
        ]
    
    def test_basic_query(self, issues):
        """Test basic query execution."""
        results = IssueQuery(issues).execute()
        assert len(results) == 5
    
    def test_status_filters(self, issues):
        """Test status filtering."""
        open_issues = IssueQuery(issues).is_open().execute()
        assert len(open_issues) == 4
        
        closed_issues = IssueQuery(issues).is_closed().execute()
        assert len(closed_issues) == 1
        
        blocked = IssueQuery(issues).is_blocked().execute()
        assert len(blocked) == 1
    
    def test_assignee_filter(self, issues):
        """Test assignee filtering."""
        emily_issues = IssueQuery(issues).assignee("emily").execute()
        assert len(emily_issues) == 2
        
        unassigned = IssueQuery(issues).unassigned().execute()
        assert len(unassigned) == 1
    
    def test_type_filter(self, issues):
        """Test type filtering."""
        bugs = IssueQuery(issues).bugs().execute()
        assert len(bugs) == 2
        
        tasks = IssueQuery(issues).tasks().execute()
        assert len(tasks) == 2
    
    def test_priority_filter(self, issues):
        """Test priority filtering."""
        critical = IssueQuery(issues).critical().execute()
        assert len(critical) == 1
        
        high_priority = IssueQuery(issues).high_priority().execute()
        assert len(high_priority) == 2
    
    def test_label_filter(self, issues):
        """Test label filtering."""
        backend = IssueQuery(issues).label("backend").execute()
        assert len(backend) == 2
        
        multi_label = IssueQuery(issues).labels(["backend", "frontend"]).execute()
        assert len(multi_label) == 3  # Any match
        
        all_labels = IssueQuery(issues).labels(["backend", "api"], match_all=True).execute()
        assert len(all_labels) == 1
    
    def test_chained_filters(self, issues):
        """Test chaining multiple filters."""
        results = (
            IssueQuery(issues)
            .assignee("emily")
            .is_open()
            .execute()
        )
        assert len(results) == 1
        assert results[0].id == "BUG-1"
    
    def test_sorting(self, issues):
        """Test sorting."""
        by_priority = IssueQuery(issues).by_priority().execute()
        assert by_priority[0].priority == Priority.CRITICAL
        
        by_points = IssueQuery(issues).by_points().execute()
        assert by_points[0].story_points == 8
    
    def test_pagination(self, issues):
        """Test limit and offset."""
        limited = IssueQuery(issues).limit(2).execute()
        assert len(limited) == 2
        
        offset = IssueQuery(issues).offset(2).limit(2).execute()
        assert len(offset) == 2
    
    def test_count(self, issues):
        """Test count without executing."""
        count = IssueQuery(issues).bugs().count()
        assert count == 2
    
    def test_exists(self, issues):
        """Test exists check."""
        assert IssueQuery(issues).critical().exists() is True
        assert IssueQuery(issues).assignee("nobody").exists() is False
    
    def test_first(self, issues):
        """Test getting first result."""
        first = IssueQuery(issues).by_priority().first()
        assert first is not None
        assert first.priority == Priority.CRITICAL
        
        none = IssueQuery(issues).assignee("nobody").first()
        assert none is None
    
    def test_stats(self, issues):
        """Test aggregate statistics."""
        stats = IssueQuery(issues).stats()
        assert stats["total"] == 5
        assert stats["open"] == 4
        assert stats["closed"] == 1
        assert stats["points"] == 19
    
    def test_group_by(self, issues):
        """Test grouping."""
        by_assignee = IssueQuery(issues).group_by_assignee()
        assert "Emily" in by_assignee
        assert len(by_assignee["Emily"]) == 2
        
        by_status = IssueQuery(issues).group_by_status()
        assert "todo" in by_status
    
    def test_custom_filter(self, issues):
        """Test custom filter predicate."""
        high_points = IssueQuery(issues).where(lambda i: i.story_points > 3).execute()
        assert len(high_points) == 2
    
    def test_custom_sort(self, issues):
        """Test custom sort key."""
        by_title = IssueQuery(issues).order_by(lambda i: i.title).execute()
        assert by_title[0].title == "Critical bug"
    
    def test_immutability(self, issues):
        """Test that queries are immutable."""
        q1 = IssueQuery(issues)
        q2 = q1.bugs()
        q3 = q1.stories()
        
        assert len(q1.execute()) == 5
        assert len(q2.execute()) == 2
        assert len(q3.execute()) == 1

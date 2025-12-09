"""Tests for iteration models."""

import pytest
from datetime import date, datetime

from amplifier_module_hooks_iteration_tracker import (
    Issue, IssueStatus, IssueType, Priority,
    Iteration, IterationStatus,
)


class TestIssue:
    """Tests for Issue model."""
    
    def test_create_issue(self):
        """Test basic issue creation."""
        issue = Issue(id="TEST-1", title="Test issue")
        assert issue.id == "TEST-1"
        assert issue.title == "Test issue"
        assert issue.status == IssueStatus.TODO
        assert issue.is_open is True
        assert issue.is_closed is False
    
    def test_issue_is_open(self):
        """Test is_open property."""
        issue = Issue(id="TEST-1", title="Test", status=IssueStatus.IN_PROGRESS)
        assert issue.is_open is True
        
        issue.status = IssueStatus.DONE
        assert issue.is_open is False
        
        issue.status = IssueStatus.CANCELLED
        assert issue.is_open is False
    
    def test_issue_is_blocked(self):
        """Test is_blocked property."""
        issue = Issue(id="TEST-1", title="Test")
        assert issue.is_blocked is False
        
        issue.status = IssueStatus.BLOCKED
        assert issue.is_blocked is True
        
        issue.status = IssueStatus.TODO
        issue.blocked_by = "TEST-2"
        assert issue.is_blocked is True


class TestIteration:
    """Tests for Iteration model."""
    
    @pytest.fixture
    def iteration(self):
        """Create a test iteration with issues."""
        iteration = Iteration(
            name="Sprint 1",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 14),
            status=IterationStatus.ACTIVE,
        )
        
        # Add test issues
        issues = [
            Issue(id="TEST-1", title="Bug fix", status=IssueStatus.DONE, 
                  issue_type=IssueType.BUG, assignee="Emily", story_points=3),
            Issue(id="TEST-2", title="New feature", status=IssueStatus.IN_PROGRESS,
                  issue_type=IssueType.STORY, assignee="Emily", story_points=5),
            Issue(id="TEST-3", title="Tech debt", status=IssueStatus.TODO,
                  issue_type=IssueType.TASK, assignee="John", story_points=2),
            Issue(id="TEST-4", title="Blocked task", status=IssueStatus.BLOCKED,
                  issue_type=IssueType.TASK, assignee="John", story_points=3),
            Issue(id="TEST-5", title="Unassigned bug", status=IssueStatus.TODO,
                  issue_type=IssueType.BUG, labels=["backend"], story_points=2),
        ]
        for issue in issues:
            iteration.add_issue(issue)
        
        return iteration
    
    def test_create_iteration(self):
        """Test basic iteration creation."""
        iteration = Iteration(name="Sprint 1")
        assert iteration.name == "Sprint 1"
        assert iteration.status == IterationStatus.PLANNING
        assert len(iteration.issues()) == 0
    
    def test_add_issue(self, iteration):
        """Test adding issues."""
        assert len(iteration.issues()) == 5
        
        new_issue = Issue(id="TEST-6", title="New")
        iteration.add_issue(new_issue)
        assert len(iteration.issues()) == 6
        assert new_issue.iteration == "Sprint 1"
    
    def test_remove_issue(self, iteration):
        """Test removing issues."""
        assert iteration.remove_issue("TEST-1") is True
        assert len(iteration.issues()) == 4
        assert iteration.remove_issue("NONEXISTENT") is False
    
    def test_open_closed(self, iteration):
        """Test open/closed filtering."""
        assert len(iteration.open()) == 4
        assert len(iteration.closed()) == 1
    
    def test_status_filters(self, iteration):
        """Test status-based filters."""
        assert len(iteration.done()) == 1
        assert len(iteration.blocked()) == 1
        assert len(iteration.in_progress()) == 1
        assert len(iteration.todo()) == 2
    
    def test_by_assignee(self, iteration):
        """Test assignee filter."""
        emily_issues = iteration.by_assignee("emily")
        assert len(emily_issues) == 2
        
        john_issues = iteration.by_assignee("John")
        assert len(john_issues) == 2
    
    def test_unassigned(self, iteration):
        """Test unassigned filter."""
        unassigned = iteration.unassigned()
        assert len(unassigned) == 1
        assert unassigned[0].id == "TEST-5"
    
    def test_type_filters(self, iteration):
        """Test type-based filters."""
        assert len(iteration.bugs()) == 2
        assert len(iteration.stories()) == 1
        assert len(iteration.tasks()) == 2
    
    def test_by_label(self, iteration):
        """Test label filter."""
        backend_issues = iteration.by_label("backend")
        assert len(backend_issues) == 1
        assert backend_issues[0].id == "TEST-5"
    
    def test_statistics(self, iteration):
        """Test iteration statistics."""
        assert iteration.total_points == 15
        assert iteration.completed_points == 3
        assert iteration.remaining_points == 12
        assert iteration.completion_percent == 20.0
        assert iteration.velocity == 3
    
    def test_group_by_assignee(self, iteration):
        """Test grouping by assignee."""
        groups = iteration.group_by_assignee()
        assert len(groups) == 3  # Emily, John, Unassigned
        assert len(groups["Emily"]) == 2
        assert len(groups["John"]) == 2
        assert len(groups["Unassigned"]) == 1
    
    def test_group_by_status(self, iteration):
        """Test grouping by status."""
        groups = iteration.group_by_status()
        assert "done" in groups
        assert "todo" in groups
        assert len(groups["done"]) == 1
    
    def test_summary(self, iteration):
        """Test iteration summary."""
        summary = iteration.summary()
        assert summary["name"] == "Sprint 1"
        assert summary["total_issues"] == 5
        assert summary["open_issues"] == 4
        assert summary["closed_issues"] == 1
        assert summary["total_points"] == 15

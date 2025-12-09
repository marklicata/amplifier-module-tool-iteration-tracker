"""Tests for IterationBoard."""

import pytest
from datetime import date

from amplifier_module_hooks_iteration_tracker import (
    IterationBoard, Iteration, IterationStatus,
    Issue, IssueStatus, IssueType,
)


class TestIterationBoard:
    """Tests for IterationBoard."""
    
    @pytest.fixture
    def board(self):
        """Create a test board with iterations and issues."""
        board = IterationBoard()
        
        # Create iterations
        board.create_iteration(
            "Sprint 1",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 14),
            status=IterationStatus.COMPLETED,
        )
        board.create_iteration(
            "Sprint 2",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 28),
            status=IterationStatus.ACTIVE,
        )
        board.create_iteration(
            "Sprint 3",
            start_date=date(2024, 1, 29),
            end_date=date(2024, 2, 11),
            status=IterationStatus.PLANNING,
        )
        
        # Add issues
        issues = [
            Issue(id="TEST-1", title="Done in S1", status=IssueStatus.DONE,
                  iteration="Sprint 1", assignee="Emily", story_points=5),
            Issue(id="TEST-2", title="Done in S1", status=IssueStatus.DONE,
                  iteration="Sprint 1", assignee="John", story_points=3),
            Issue(id="TEST-3", title="Active in S2", status=IssueStatus.IN_PROGRESS,
                  iteration="Sprint 2", assignee="Emily", story_points=5),
            Issue(id="TEST-4", title="Blocked in S2", status=IssueStatus.BLOCKED,
                  iteration="Sprint 2", assignee="John", story_points=3),
            Issue(id="TEST-5", title="Todo in S2", status=IssueStatus.TODO,
                  iteration="Sprint 2", labels=["backend"], story_points=2),
        ]
        for issue in issues:
            board.add_issue(issue)
        
        return board
    
    def test_create_iteration(self, board):
        """Test creating iterations."""
        assert len(board.list_iterations()) == 3
        
        board.create_iteration("Sprint 4")
        assert len(board.list_iterations()) == 4
    
    def test_get_iteration(self, board):
        """Test getting iteration by name."""
        iteration = board.get_iteration("Sprint 2")
        assert iteration is not None
        assert iteration.name == "Sprint 2"
        
        # Partial match
        iteration = board.get_iteration("sprint 2")
        assert iteration is not None
        
        # Not found
        assert board.get_iteration("Sprint 99") is None
    
    def test_delete_iteration(self, board):
        """Test deleting iteration."""
        assert board.delete_iteration("Sprint 3") is True
        assert len(board.list_iterations()) == 2
        assert board.delete_iteration("Sprint 3") is False
    
    def test_current_iteration(self, board):
        """Test getting current active iteration."""
        current = board.current()
        assert current is not None
        assert current.name == "Sprint 2"
    
    def test_next_iteration(self, board):
        """Test getting next planned iteration."""
        next_iter = board.next()
        assert next_iter is not None
        assert next_iter.name == "Sprint 3"
    
    def test_previous_iteration(self, board):
        """Test getting previous completed iteration."""
        prev = board.previous()
        assert prev is not None
        assert prev.name == "Sprint 1"
    
    def test_add_issue(self, board):
        """Test adding issues."""
        issue = Issue(id="TEST-6", title="New", iteration="Sprint 2")
        board.add_issue(issue)
        
        assert board.get_issue("TEST-6") is not None
        assert len(board.get_iteration("Sprint 2").issues()) == 4
    
    def test_move_issue(self, board):
        """Test moving issue between iterations."""
        assert board.move_issue("TEST-3", "Sprint 3") is True
        
        sprint2 = board.get_iteration("Sprint 2")
        sprint3 = board.get_iteration("Sprint 3")
        
        assert len(sprint2.issues()) == 2
        assert len(sprint3.issues()) == 1
    
    def test_cross_iteration_queries(self, board):
        """Test queries across all iterations."""
        emily_issues = board.by_assignee("emily")
        assert len(emily_issues) == 2
        
        blocked = board.blocked_issues()
        assert len(blocked) == 1
        
        open_issues = board.open_issues()
        assert len(open_issues) == 3
    
    def test_velocity_history(self, board):
        """Test velocity tracking."""
        history = board.velocity_history(5)
        assert len(history) == 1  # Only Sprint 1 is completed
        assert history[0]["iteration"] == "Sprint 1"
        assert history[0]["velocity"] == 8  # 5 + 3 points
    
    def test_team_workload(self, board):
        """Test team workload breakdown."""
        workload = board.team_workload("Sprint 2")
        
        assert "Emily" in workload
        assert workload["Emily"]["total"] == 1
        assert workload["Emily"]["in_progress"] == 1
        
        assert "John" in workload
        assert workload["John"]["blocked"] == 1
    
    def test_serialization(self, board):
        """Test board serialization/deserialization."""
        data = board.to_dict()
        
        assert "iterations" in data
        assert "issues" in data
        assert len(data["iterations"]) == 3
        assert len(data["issues"]) == 5
        
        # Restore
        restored = IterationBoard.from_dict(data)
        assert len(restored.list_iterations()) == 3
        assert len(restored.all_issues()) == 5
        assert restored.get_iteration("Sprint 2").name == "Sprint 2"

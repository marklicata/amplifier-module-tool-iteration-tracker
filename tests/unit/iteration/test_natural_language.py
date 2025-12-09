"""Tests for natural language query parsing."""

import pytest

from amplifier_module_hooks_iteration_tracker import (
    parse_query, ask,
    Issue, IssueStatus, IssueType, Priority,
)


class TestParseQuery:
    """Tests for parse_query function."""
    
    def test_parse_assignee(self):
        """Test parsing assignee queries."""
        query = parse_query("What is Emily working on?")
        assert query.assignee == "emily"
        
        query = parse_query("Show John's tasks")
        assert query.assignee == "john"
        
        query = parse_query("assigned to Sarah")
        assert query.assignee == "sarah"
    
    def test_parse_author(self):
        """Test parsing author queries."""
        query = parse_query("created by John")
        assert query.author == "john"
        
        query = parse_query("filed by Emily")
        assert query.author == "emily"
    
    def test_parse_iteration(self):
        """Test parsing iteration queries."""
        query = parse_query("What's in Sprint 3?")
        assert "sprint" in query.iteration.lower()
        
        query = parse_query("Issues in Iteration 2")
        assert "iteration" in query.iteration.lower()
    
    def test_parse_status(self):
        """Test parsing status queries."""
        query = parse_query("Show blocked issues")
        assert query.status == "blocked"
        
        query = parse_query("What's open?")
        assert query.status == "open"
        
        query = parse_query("What did we close?")
        assert query.status == "closed"
        
        query = parse_query("What's in progress?")
        assert query.status == "in_progress"
    
    def test_parse_type(self):
        """Test parsing issue type queries."""
        query = parse_query("Show all bugs")
        assert query.issue_type == "bug"
        
        query = parse_query("List user stories")
        assert query.issue_type == "story"
        
        query = parse_query("Show tasks")
        assert query.issue_type == "task"
    
    def test_parse_count(self):
        """Test parsing count queries."""
        query = parse_query("How many bugs are left?")
        assert query.query_type == "count"
        assert query.issue_type == "bug"
        assert query.status == "open"
    
    def test_parse_label(self):
        """Test parsing label queries."""
        query = parse_query("Show issues labeled backend")
        assert query.label == "backend"
        
        query = parse_query("Issues tagged urgent")
        assert query.label == "urgent"
    
    def test_parse_priority(self):
        """Test parsing priority queries."""
        query = parse_query("Show critical issues")
        assert query.priority == "critical"
        
        query = parse_query("High priority bugs")
        assert query.priority == "high"


class TestAsk:
    """Tests for ask function."""
    
    @pytest.fixture
    def issues(self):
        """Create test issues."""
        return [
            Issue(id="BUG-1", title="Critical bug", status=IssueStatus.IN_PROGRESS,
                  issue_type=IssueType.BUG, assignee="Emily", story_points=5),
            Issue(id="BUG-2", title="Minor bug", status=IssueStatus.TODO,
                  issue_type=IssueType.BUG, assignee="John", story_points=2),
            Issue(id="STORY-1", title="New feature", status=IssueStatus.DONE,
                  issue_type=IssueType.STORY, assignee="Emily", story_points=8),
            Issue(id="TASK-1", title="Refactor", status=IssueStatus.BLOCKED,
                  issue_type=IssueType.TASK, assignee="John", story_points=3),
        ]
    
    def test_ask_assignee(self, issues):
        """Test asking about assignee."""
        result = ask("What is Emily working on?", issues)
        assert isinstance(result, list)
        # "working on" implies in_progress, so only the in-progress issue
        assert len(result) == 1
        assert result[0].assignee == "Emily"
        assert result[0].status == IssueStatus.IN_PROGRESS
    
    def test_ask_assignee_all(self, issues):
        """Test asking about all assignee's issues."""
        result = ask("Show Emily's issues", issues)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(i.assignee == "Emily" for i in result)
    
    def test_ask_count(self, issues):
        """Test count queries."""
        result = ask("How many bugs are there?", issues)
        assert result == 2
    
    def test_ask_status(self, issues):
        """Test status queries."""
        result = ask("Show blocked issues", issues)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == "TASK-1"
    
    def test_ask_closed(self, issues):
        """Test closed issues query."""
        result = ask("What did we close?", issues)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == "STORY-1"
    
    def test_ask_combined(self, issues):
        """Test combined queries."""
        result = ask("What bugs are open?", issues)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(i.issue_type == IssueType.BUG for i in result)
    
    def test_ask_default_open(self, issues):
        """Test default returns open issues."""
        result = ask("Show issues", issues)
        assert isinstance(result, list)
        # Should return open issues by default
        assert all(i.is_open for i in result)

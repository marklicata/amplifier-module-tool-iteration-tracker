"""
Natural language query parser for iteration tracking.

Parses questions like:
    "What is Emily working on?"
    "How many bugs are left?"
    "Show blocked issues"
"""

import re
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from .models import Issue, IssueStatus, IssueType, Priority

if TYPE_CHECKING:
    from .models import Iteration


@dataclass
class ParsedQuery:
    """Represents a parsed natural language query."""
    query_type: str  # "list", "count", "summary"
    assignee: Optional[str] = None
    author: Optional[str] = None
    iteration: Optional[str] = None
    status: Optional[str] = None  # "open", "closed", "blocked", "in_progress"
    issue_type: Optional[str] = None  # "bug", "story", "task"
    label: Optional[str] = None
    priority: Optional[str] = None  # "critical", "high"
    time_filter: Optional[str] = None  # "today", "this_week"


def parse_query(question: str) -> ParsedQuery:
    """
    Parse a natural language question into a structured query.
    
    Examples:
        "What is Emily working on?" -> assignee=emily, status=open
        "How many bugs are left?" -> type=count, issue_type=bug, status=open
        "Show blocked issues" -> status=blocked
    """
    q = question.lower().strip()
    query = ParsedQuery(query_type="list")
    
    # Detect query type
    if any(word in q for word in ["how many", "count", "number of"]):
        query.query_type = "count"
    elif any(word in q for word in ["summary", "summarize", "overview", "stats"]):
        query.query_type = "summary"
    
    # Detect assignee - "What is Emily working on?", "assigned to Emily"
    assignee_patterns = [
        r"(?:assigned to|assignee[:\s]+)\s+(\w+)",
        r"what (?:is|are) (\w+) working",
        r"what's (\w+) working",
        r"(\w+)'s (?:tasks|issues|work|items)",
    ]
    for pattern in assignee_patterns:
        match = re.search(pattern, q)
        if match:
            name = match.group(1)
            # Exclude common words
            if name not in ["the", "a", "an", "to", "in", "on", "what", "show", "all", "is", "are"]:
                query.assignee = name
                break
    
    # Detect author
    author_patterns = [
        r"(?:created by|filed by|authored by|author[:\s]+)\s+(\w+)",
        r"(\w+)(?:'s filed|'s created|'s reported)",
    ]
    for pattern in author_patterns:
        match = re.search(pattern, q)
        if match:
            query.author = match.group(1)
            break
    
    # Detect iteration
    iteration_patterns = [
        r"(?:in|for|during)\s+(sprint\s*\d+|iteration\s*\d+|milestone\s*\d+)",
        r"(sprint\s*\d+|iteration\s*\d+|milestone\s*\d+)",
    ]
    for pattern in iteration_patterns:
        match = re.search(pattern, q)
        if match:
            query.iteration = match.group(1)
            break
    
    # Detect status - order matters, check more specific patterns first
    if any(word in q for word in ["blocked", "stuck"]):
        query.status = "blocked"
    elif any(word in q for word in ["in progress", "working on", "active"]):
        query.status = "in_progress"
    elif any(phrase in q for phrase in ["did we close", "we closed", "closed", "completed", "done", "finished", "resolved"]):
        query.status = "closed"
    elif any(word in q for word in ["open", "remaining", "left", "todo", "pending"]):
        query.status = "open"
    
    # Detect issue type
    if "bug" in q:
        query.issue_type = "bug"
    elif "stor" in q:  # story, stories
        query.issue_type = "story"
    elif "task" in q:
        query.issue_type = "task"
    elif "spike" in q:
        query.issue_type = "spike"
    
    # Detect label
    label_patterns = [
        r"(?:labeled?|tagged?|with label|with tag)\s+['\"]?(\w+)['\"]?",
    ]
    for pattern in label_patterns:
        match = re.search(pattern, q)
        if match:
            query.label = match.group(1)
            break
    
    # Detect priority
    if "critical" in q:
        query.priority = "critical"
    elif "high priority" in q or "high-priority" in q:
        query.priority = "high"
    elif "low priority" in q or "low-priority" in q:
        query.priority = "low"
    
    # Detect time filter
    if "today" in q:
        query.time_filter = "today"
    elif "this week" in q:
        query.time_filter = "this_week"
    elif "yesterday" in q:
        query.time_filter = "yesterday"
    
    return query


def execute_query(
    parsed: ParsedQuery,
    issues: list[Issue],
    iteration: Optional["Iteration"] = None
) -> list[Issue] | int | dict:
    """
    Execute a parsed query against a list of issues.
    """
    results = issues
    
    # Apply filters
    if parsed.assignee:
        assignee_lower = parsed.assignee.lower()
        results = [i for i in results if i.assignee and assignee_lower in i.assignee.lower()]
    
    if parsed.author:
        author_lower = parsed.author.lower()
        results = [i for i in results if i.author and author_lower in i.author.lower()]
    
    if parsed.iteration:
        iter_lower = parsed.iteration.lower().replace(" ", "")
        results = [i for i in results if i.iteration and iter_lower in i.iteration.lower().replace(" ", "")]
    
    if parsed.status:
        if parsed.status == "open":
            results = [i for i in results if i.is_open]
        elif parsed.status == "closed":
            results = [i for i in results if i.is_closed]
        elif parsed.status == "blocked":
            results = [i for i in results if i.is_blocked]
        elif parsed.status == "in_progress":
            results = [i for i in results if i.status == IssueStatus.IN_PROGRESS]
    
    if parsed.issue_type:
        type_map = {
            "bug": IssueType.BUG,
            "story": IssueType.STORY,
            "task": IssueType.TASK,
            "spike": IssueType.SPIKE,
        }
        if parsed.issue_type in type_map:
            results = [i for i in results if i.issue_type == type_map[parsed.issue_type]]
    
    if parsed.label:
        label_lower = parsed.label.lower()
        results = [i for i in results if any(label_lower in l.lower() for l in i.labels)]
    
    if parsed.priority:
        priority_map = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
        }
        if parsed.priority in priority_map:
            results = [i for i in results if i.priority == priority_map[parsed.priority]]
    
    # Return based on query type
    if parsed.query_type == "count":
        return len(results)
    elif parsed.query_type == "summary":
        return {
            "total": len(results),
            "open": len([i for i in results if i.is_open]),
            "closed": len([i for i in results if i.is_closed]),
            "blocked": len([i for i in results if i.is_blocked]),
            "points": sum(i.story_points for i in results),
        }
    else:
        return results


def ask(
    question: str,
    issues: list[Issue],
    iteration: Optional["Iteration"] = None
) -> list[Issue] | int | dict | str:
    """
    Ask a natural language question about issues.
    
    Examples:
        ask("What is Emily working on?", issues)
        ask("How many bugs are left?", issues)
        ask("Show blocked issues", issues)
    
    Returns:
        - list[Issue] for "show" queries
        - int for "how many" queries
        - dict for "summary" queries
        - str if query cannot be parsed
    """
    parsed = parse_query(question)
    
    # If we couldn't parse anything meaningful, return helpful message
    if (not parsed.assignee and not parsed.author and not parsed.status 
        and not parsed.issue_type and not parsed.label and not parsed.priority
        and not parsed.iteration):
        # Default to listing all open issues
        if "all" in question.lower():
            return issues
        return [i for i in issues if i.is_open]
    
    return execute_query(parsed, issues, iteration)


def format_results(results: list[Issue] | int | dict | str, question: str = "") -> str:
    """
    Format query results as a human-readable string.
    """
    if isinstance(results, str):
        return results
    
    if isinstance(results, int):
        return f"{results}"
    
    if isinstance(results, dict):
        lines = []
        for key, value in results.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    if isinstance(results, list):
        if not results:
            return "No issues found."
        
        lines = []
        for issue in results:
            status_icon = {
                IssueStatus.TODO: "○",
                IssueStatus.IN_PROGRESS: "◐",
                IssueStatus.IN_REVIEW: "◑",
                IssueStatus.BLOCKED: "⊘",
                IssueStatus.DONE: "●",
                IssueStatus.CANCELLED: "✕",
            }.get(issue.status, "?")
            
            assignee = f" @{issue.assignee}" if issue.assignee else ""
            points = f" ({issue.story_points}pts)" if issue.story_points else ""
            
            lines.append(f"{status_icon} {issue.id}: {issue.title}{assignee}{points}")
        
        return "\n".join(lines)
    
    return str(results)

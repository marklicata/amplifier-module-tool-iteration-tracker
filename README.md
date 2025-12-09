# Amplifier Iteration Tracker

Iteration/sprint planning and tracking module for Amplifier. Provides an iteration-centric approach to managing work where everything revolves around the **Iteration** as the core entity.

## Installation

```bash
pip install amplifier-module-hooks-iteration-tracker
```

## Quick Start

```python
from amplifier_module_hooks_iteration_tracker import IterationBoard, Iteration, Issue

# Create a board and iterations
board = IterationBoard()
board.create_iteration("Sprint 3", start_date=date(2024, 3, 1), end_date=date(2024, 3, 14))

# Add issues to an iteration
board.add_issue(Issue(
    id="PROJ-101",
    title="Add OAuth login",
    assignee="Emily",
    story_points=5,
    iteration="Sprint 3",
    labels=["backend", "auth"]
))

# Get the iteration - everything flows from here
iteration = board.get_iteration("Sprint 3")

# Query the iteration
iteration.open()                 # What's left to do?
iteration.closed()               # What did we complete?
iteration.blocked()              # What's stuck?
iteration.by_assignee("emily")   # Emily's issues
iteration.bugs()                 # All bugs

# Statistics
iteration.total_points           # 50
iteration.completed_points       # 35
iteration.completion_percent     # 70.0
iteration.days_remaining         # 3

# Natural language queries
iteration.ask("What is Emily working on?")
iteration.ask("How many bugs are left?")
```

## Core Concepts

### The Iteration

The `Iteration` is the central entity. All queries and operations flow through it:

```python
iteration = board.get_iteration("Sprint 3")

# Status queries
iteration.open()           # All open issues
iteration.closed()         # All closed issues
iteration.done()           # Successfully completed
iteration.blocked()        # Blocked issues
iteration.in_progress()    # Currently being worked

# People queries
iteration.by_assignee("emily")   # Assigned to Emily
iteration.by_author("john")      # Created by John

# Type queries
iteration.bugs()           # Bugs only
iteration.stories()        # User stories
iteration.tasks()          # Tasks

# Label/priority queries
iteration.by_label("backend")    # Has backend label
iteration.critical()             # Critical priority
iteration.high_priority()        # High + critical

# Groupings
iteration.group_by_assignee()    # {"Emily": [...], "John": [...]}
iteration.group_by_status()      # {"todo": [...], "in_progress": [...]}
```

### The IterationBoard

Manages multiple iterations and provides cross-iteration queries:

```python
board = IterationBoard()

# Navigation
board.current()              # Active iteration
board.next()                 # Next planned
board.previous()             # Last completed

# Cross-iteration queries
board.by_assignee("emily")   # All of Emily's issues
board.blocked_issues()       # All blocked issues

# Velocity tracking
board.velocity_history(5)    # Last 5 iterations
board.average_velocity(3)    # Average of last 3
```

### Natural Language Queries

Ask questions in plain English:

```python
iteration.ask("What is Emily working on?")
iteration.ask("How many bugs are left?")
iteration.ask("Show blocked issues")
iteration.ask("What did we close?")

# Or at the board level
board.ask("What issues are in Sprint 3?")
```

## Common Queries

```python
# "What issues did we close in Sprint 2?"
board.get_iteration("Sprint 2").closed()

# "What is Emily working on this iteration?"
board.current().by_assignee("emily")

# "How many bugs are left?"
len(board.current().bugs().open())

# "Show me high priority items"
board.current().high_priority()

# "What's blocked?"
board.current().blocked()

# "Group by assignee for standup"
board.current().group_by_assignee()
```

## Fluent Query Builder

For complex queries, use the `IssueQuery` builder:

```python
from amplifier_module_hooks_iteration_tracker import IssueQuery

# Complex query with chaining
results = (
    IssueQuery(iteration.issues())
    .assignee("emily")
    .labels(["backend", "urgent"])
    .is_open()
    .by_priority()
    .limit(10)
    .execute()
)

# Aggregate queries
stats = IssueQuery(iteration.issues()).assignee("emily").stats()
# {'total': 5, 'open': 3, 'closed': 2, 'points': 13}
```

## Persistence

Save and load board state:

```python
from amplifier_module_hooks_iteration_tracker import IterationStorage

storage = IterationStorage("./data")
storage.save_board(board)

# Later...
board = storage.load_board()
```

## License

MIT

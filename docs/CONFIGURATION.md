# Configuration Guide

## Overview

The iteration tracker now supports configuration for GitHub repositories. You can specify which repositories to track, what labels to filter by, and other settings.

## Quick Start

```python
from amplifier_module_hooks_iteration_tracker import ConfigManager, TrackerConfig

# Initialize configuration manager
config_manager = ConfigManager("./data")

# Load existing config or create new one
config = config_manager.load()

# Add GitHub repositories to track
config.add_repo("myorg", "backend-api", labels=["sprint", "bug"])
config.add_repo("myorg", "frontend-app", labels=["sprint"])
config.add_repo("mycompany", "infrastructure")

# Save configuration
config_manager.save(config)
```

## Configuration Structure

### TrackerConfig

Main configuration object that holds all settings.

**Attributes:**
- `repos`: List of GitHub repositories to track
- `data_dir`: Directory where data files are stored (default: `"./data"`)
- `sync_interval`: Minutes between automatic syncs, 0 = manual only (default: `0`)

**Methods:**
```python
# Add a repository
config.add_repo(
    owner="myorg",           # GitHub owner (user or organization)
    repo="myrepo",           # Repository name
    enabled=True,            # Whether to track this repo
    labels=["sprint"],       # Optional: filter issues by labels
    default_iteration=None   # Optional: default iteration for new issues
)

# Remove a repository
config.remove_repo("myorg", "myrepo")

# Get specific repository config
repo_config = config.get_repo("myorg", "myrepo")

# Get only enabled repositories
enabled_repos = config.get_enabled_repos()
```

### GitHubRepoConfig

Configuration for a single repository.

**Attributes:**
- `owner`: Repository owner (user or organization)
- `repo`: Repository name
- `enabled`: Whether to track this repo (default: `True`)
- `labels`: Optional list of labels to filter issues
- `default_iteration`: Default iteration for new issues from this repo

**Properties:**
- `full_name`: Returns `"owner/repo"` format

## Usage Examples

### Basic Setup

```python
from amplifier_module_hooks_iteration_tracker import ConfigManager

# Create configuration
config_manager = ConfigManager("./data")
config = config_manager.load()

# Add repositories
config.add_repo("acme-corp", "api-service", labels=["sprint", "v2.0"])
config.add_repo("acme-corp", "web-app", labels=["sprint"])

# Configure settings
config.data_dir = "./project_data"
config.sync_interval = 15  # Sync every 15 minutes

# Save
config_manager.save(config)
```

### Managing Repositories

```python
# Disable a repository temporarily
repo = config.get_repo("acme-corp", "api-service")
repo.enabled = False
config_manager.save(config)

# Add labels to filter issues
repo = config.get_repo("acme-corp", "web-app")
repo.labels.extend(["critical", "production"])
config_manager.save(config)

# Set default iteration
repo.default_iteration = "Sprint 3"
config_manager.save(config)

# Remove a repository completely
config.remove_repo("acme-corp", "old-project")
config_manager.save(config)
```

### Listing Repositories

```python
# Get all configured repositories
for repo in config.repos:
    print(f"{repo.full_name}: enabled={repo.enabled}, labels={repo.labels}")

# Get only enabled repositories
for repo in config.get_enabled_repos():
    print(f"Tracking: {repo.full_name}")
```

### Integration with IterationBoard

```python
from amplifier_module_hooks_iteration_tracker import (
    ConfigManager,
    IterationBoard,
    IterationStorage,
)

# Load configuration
config_manager = ConfigManager("./data")
config = config_manager.load()

# Initialize storage and board with configured data directory
storage = IterationStorage(config.data_dir)
board = storage.load_board()

# Now you know which repos to sync from
for repo in config.get_enabled_repos():
    print(f"Syncing issues from {repo.full_name}...")
    # Your GitHub sync logic here
    # Filter by repo.labels if specified
```

## Configuration File Format

The configuration is saved as JSON in `{data_dir}/config.json`:

```json
{
  "repos": [
    {
      "owner": "myorg",
      "repo": "backend-api",
      "enabled": true,
      "labels": ["sprint", "bug"],
      "default_iteration": null
    },
    {
      "owner": "myorg",
      "repo": "frontend-app",
      "enabled": true,
      "labels": ["sprint"],
      "default_iteration": "Sprint 3"
    }
  ],
  "data_dir": "./data",
  "sync_interval": 0
}
```

## Command-Line Usage (Example)

You could create a CLI tool to manage configuration:

```python
#!/usr/bin/env python3
"""CLI tool for managing iteration tracker configuration."""

import sys
from amplifier_module_hooks_iteration_tracker import ConfigManager

def main():
    config_manager = ConfigManager("./data")
    config = config_manager.load()
    
    if len(sys.argv) < 2:
        print("Usage: config.py <command> [args]")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: config.py add <owner> <repo> [labels...]")
            return
        owner, repo = sys.argv[2], sys.argv[3]
        labels = sys.argv[4:] if len(sys.argv) > 4 else []
        config.add_repo(owner, repo, labels=labels)
        config_manager.save(config)
        print(f"Added {owner}/{repo}")
    
    elif command == "remove":
        if len(sys.argv) < 4:
            print("Usage: config.py remove <owner> <repo>")
            return
        owner, repo = sys.argv[2], sys.argv[3]
        if config.remove_repo(owner, repo):
            config_manager.save(config)
            print(f"Removed {owner}/{repo}")
        else:
            print(f"Repository {owner}/{repo} not found")
    
    elif command == "list":
        print("\nConfigured repositories:")
        for repo in config.repos:
            status = "✓" if repo.enabled else "✗"
            labels = f" (labels: {', '.join(repo.labels)})" if repo.labels else ""
            print(f"  {status} {repo.full_name}{labels}")
        print()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Keep config separate from code**: Store the config.json file outside your source control or add it to `.gitignore`
2. **Use labels for filtering**: Add relevant labels to focus on specific issue types
3. **Disable, don't remove**: When a project is on hold, disable the repo instead of removing it
4. **Document your repos**: Use descriptive repository names and maintain a list of what each repo is for
5. **Backup your config**: The config.json is small - back it up along with your data directory

## Next Steps

Once you have repositories configured, you'll want to:
1. Implement GitHub API integration to sync issues
2. Map GitHub issues to the `Issue` model
3. Update iterations based on GitHub milestones or labels
4. Set up automatic syncing based on `sync_interval`

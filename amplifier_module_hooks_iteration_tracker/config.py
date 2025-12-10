"""
Configuration management for the iteration tracker.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class GitHubRepoConfig:
    """
    Configuration for a single GitHub repository.
    
    Attributes:
        owner: Repository owner (user or organization)
        repo: Repository name
        enabled: Whether to track this repo
        labels: Optional list of labels to filter issues
        default_iteration: Default iteration for new issues
    """
    owner: str
    repo: str
    enabled: bool = True
    labels: list[str] = field(default_factory=list)
    default_iteration: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full repository name (owner/repo)."""
        return f"{self.owner}/{self.repo}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "GitHubRepoConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TrackerConfig:
    """
    Main configuration for the iteration tracker.
    
    Attributes:
        repos: List of GitHub repositories to track
        data_dir: Directory to store data files
        sync_interval: Minutes between automatic syncs (0 = manual only)
    """
    repos: list[GitHubRepoConfig] = field(default_factory=list)
    data_dir: str = "./data"
    sync_interval: int = 0
    
    def add_repo(
        self,
        owner: str,
        repo: str,
        enabled: bool = True,
        labels: Optional[list[str]] = None,
        default_iteration: Optional[str] = None,
    ) -> GitHubRepoConfig:
        """Add a GitHub repository to track."""
        repo_config = GitHubRepoConfig(
            owner=owner,
            repo=repo,
            enabled=enabled,
            labels=labels or [],
            default_iteration=default_iteration,
        )
        self.repos.append(repo_config)
        return repo_config
    
    def remove_repo(self, owner: str, repo: str) -> bool:
        """Remove a repository from tracking."""
        full_name = f"{owner}/{repo}"
        original_len = len(self.repos)
        self.repos = [r for r in self.repos if r.full_name != full_name]
        return len(self.repos) < original_len
    
    def get_repo(self, owner: str, repo: str) -> Optional[GitHubRepoConfig]:
        """Get configuration for a specific repository."""
        full_name = f"{owner}/{repo}"
        for repo_config in self.repos:
            if repo_config.full_name == full_name:
                return repo_config
        return None
    
    def get_enabled_repos(self) -> list[GitHubRepoConfig]:
        """Get all enabled repositories."""
        return [r for r in self.repos if r.enabled]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "repos": [r.to_dict() for r in self.repos],
            "data_dir": self.data_dir,
            "sync_interval": self.sync_interval,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrackerConfig":
        """Create from dictionary."""
        repos = [GitHubRepoConfig.from_dict(r) for r in data.get("repos", [])]
        return cls(
            repos=repos,
            data_dir=data.get("data_dir", "./data"),
            sync_interval=data.get("sync_interval", 0),
        )


class ConfigManager:
    """
    Manages loading and saving configuration.
    
    Example:
        manager = ConfigManager("./data")
        config = manager.load()
        config.add_repo("myorg", "myrepo")
        manager.save(config)
    """
    
    def __init__(self, config_dir: str | Path = "./data"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration file
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self.config_dir / "config.json"
    
    def load(self) -> TrackerConfig:
        """Load configuration from disk. Returns default config if file doesn't exist."""
        if not self._config_file.exists():
            return TrackerConfig()
        
        with open(self._config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return TrackerConfig.from_dict(data)
    
    def save(self, config: TrackerConfig) -> None:
        """Save configuration to disk."""
        data = config.to_dict()
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return self._config_file.exists()

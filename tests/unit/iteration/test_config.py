"""
Tests for configuration management.
"""

import json

from amplifier_module_hooks_iteration_tracker.config import (
    GitHubRepoConfig,
    TrackerConfig,
    ConfigManager,
)


class TestGitHubRepoConfig:
    """Tests for GitHubRepoConfig."""

    def test_create_repo_config(self):
        """Test creating a repository configuration."""
        config = GitHubRepoConfig(
            owner="myorg",
            repo="myrepo",
            enabled=True,
            labels=["bug", "feature"],
            default_iteration="Sprint 1",
        )
        
        assert config.owner == "myorg"
        assert config.repo == "myrepo"
        assert config.enabled is True
        assert config.labels == ["bug", "feature"]
        assert config.default_iteration == "Sprint 1"
        assert config.full_name == "myorg/myrepo"

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = GitHubRepoConfig(owner="myorg", repo="myrepo")
        data = config.to_dict()
        
        assert data["owner"] == "myorg"
        assert data["repo"] == "myrepo"
        assert data["enabled"] is True
        assert data["labels"] == []

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "owner": "myorg",
            "repo": "myrepo",
            "enabled": True,
            "labels": ["bug"],
            "default_iteration": "Sprint 1",
        }
        config = GitHubRepoConfig.from_dict(data)
        
        assert config.owner == "myorg"
        assert config.repo == "myrepo"
        assert config.enabled is True
        assert config.labels == ["bug"]
        assert config.default_iteration == "Sprint 1"


class TestTrackerConfig:
    """Tests for TrackerConfig."""

    def test_create_empty_config(self):
        """Test creating an empty configuration."""
        config = TrackerConfig()
        
        assert config.repos == []
        assert config.data_dir == "./data"
        assert config.sync_interval == 0

    def test_add_repo(self):
        """Test adding a repository."""
        config = TrackerConfig()
        repo = config.add_repo(
            owner="myorg",
            repo="myrepo",
            labels=["bug"],
            default_iteration="Sprint 1",
        )
        
        assert len(config.repos) == 1
        assert repo.owner == "myorg"
        assert repo.repo == "myrepo"
        assert repo.labels == ["bug"]
        assert repo.default_iteration == "Sprint 1"

    def test_remove_repo(self):
        """Test removing a repository."""
        config = TrackerConfig()
        config.add_repo("myorg", "repo1")
        config.add_repo("myorg", "repo2")
        
        assert len(config.repos) == 2
        
        removed = config.remove_repo("myorg", "repo1")
        assert removed is True
        assert len(config.repos) == 1
        assert config.repos[0].repo == "repo2"
        
        removed = config.remove_repo("myorg", "nonexistent")
        assert removed is False
        assert len(config.repos) == 1

    def test_get_repo(self):
        """Test getting a specific repository."""
        config = TrackerConfig()
        config.add_repo("myorg", "repo1")
        config.add_repo("myorg", "repo2")
        
        repo = config.get_repo("myorg", "repo1")
        assert repo is not None
        assert repo.repo == "repo1"
        
        repo = config.get_repo("myorg", "nonexistent")
        assert repo is None

    def test_get_enabled_repos(self):
        """Test getting enabled repositories."""
        config = TrackerConfig()
        config.add_repo("myorg", "repo1", enabled=True)
        config.add_repo("myorg", "repo2", enabled=False)
        config.add_repo("myorg", "repo3", enabled=True)
        
        enabled = config.get_enabled_repos()
        assert len(enabled) == 2
        assert all(r.enabled for r in enabled)
        assert {r.repo for r in enabled} == {"repo1", "repo3"}

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = TrackerConfig()
        config.add_repo("myorg", "myrepo")
        config.data_dir = "./custom_data"
        config.sync_interval = 15
        
        data = config.to_dict()
        
        assert data["data_dir"] == "./custom_data"
        assert data["sync_interval"] == 15
        assert len(data["repos"]) == 1
        assert data["repos"][0]["owner"] == "myorg"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "repos": [
                {"owner": "org1", "repo": "repo1", "enabled": True, "labels": [], "default_iteration": None},
                {"owner": "org2", "repo": "repo2", "enabled": False, "labels": ["bug"], "default_iteration": "Sprint 1"},
            ],
            "data_dir": "./custom_data",
            "sync_interval": 30,
        }
        config = TrackerConfig.from_dict(data)
        
        assert len(config.repos) == 2
        assert config.data_dir == "./custom_data"
        assert config.sync_interval == 30
        assert config.repos[0].owner == "org1"
        assert config.repos[1].enabled is False


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_create_manager(self, tmp_path):
        """Test creating a configuration manager."""
        manager = ConfigManager(tmp_path)
        
        assert manager.config_dir == tmp_path
        assert manager.config_dir.exists()

    def test_load_nonexistent_config(self, tmp_path):
        """Test loading when no config file exists."""
        manager = ConfigManager(tmp_path)
        config = manager.load()
        
        assert isinstance(config, TrackerConfig)
        assert len(config.repos) == 0

    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading configuration."""
        manager = ConfigManager(tmp_path)
        
        # Create and save config
        config = TrackerConfig()
        config.add_repo("myorg", "myrepo", labels=["bug"])
        config.data_dir = "./custom"
        config.sync_interval = 20
        
        manager.save(config)
        assert manager.config_exists()
        
        # Load and verify
        loaded_config = manager.load()
        assert len(loaded_config.repos) == 1
        assert loaded_config.repos[0].owner == "myorg"
        assert loaded_config.repos[0].repo == "myrepo"
        assert loaded_config.repos[0].labels == ["bug"]
        assert loaded_config.data_dir == "./custom"
        assert loaded_config.sync_interval == 20

    def test_config_file_format(self, tmp_path):
        """Test that config file is valid JSON."""
        manager = ConfigManager(tmp_path)
        
        config = TrackerConfig()
        config.add_repo("myorg", "myrepo")
        manager.save(config)
        
        # Read raw file and verify it's valid JSON
        config_file = tmp_path / "config.json"
        with open(config_file, "r") as f:
            data = json.load(f)
        
        assert "repos" in data
        assert "data_dir" in data
        assert "sync_interval" in data

    def test_config_exists(self, tmp_path):
        """Test checking if config exists."""
        manager = ConfigManager(tmp_path)
        
        assert not manager.config_exists()
        
        config = TrackerConfig()
        manager.save(config)
        
        assert manager.config_exists()

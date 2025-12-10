"""
Tests for the Iteration Tracker Manager
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from .manager import IterationTrackerManager, get_iterations_data_directory
from .board import IterationBoard
from .storage import IterationStorage


def test_get_iterations_data_directory():
    """Test that get_iterations_data_directory returns correct path."""
    data_dir = get_iterations_data_directory()
    
    # Verify it returns a Path object
    assert isinstance(data_dir, Path)
    
    # Verify it points to ~/.amplifier/iterations
    expected = Path.home() / ".amplifier" / "iterations"
    assert data_dir == expected
    
    # Verify the directory exists after calling the function
    assert data_dir.exists()
    assert data_dir.is_dir()


def test_manager_initialization():
    """Test that manager initializes with proper data directory."""
    config = {}
    manager = IterationTrackerManager(config)
    
    # Verify manager has board and storage
    assert isinstance(manager.board, IterationBoard)
    assert isinstance(manager.storage, IterationStorage)
    
    # Verify storage was initialized with correct data directory
    expected_dir = Path.home() / ".amplifier" / "iterations"
    assert manager.storage.data_dir == expected_dir


def test_manager_initialization_with_custom_config():
    """Test manager initialization with custom configuration."""
    config = {"some_setting": "value"}
    manager = IterationTrackerManager(config)
    
    # Verify config is stored
    assert manager.config == config
    
    # Verify storage still uses correct data directory
    expected_dir = Path.home() / ".amplifier" / "iterations"
    assert manager.storage.data_dir == expected_dir


@pytest.mark.asyncio
async def test_manager_lifecycle():
    """Test manager start and stop methods."""
    config = {}
    manager = IterationTrackerManager(config)
    
    # Should not raise any errors
    await manager.start()
    await manager.stop()


def test_storage_directory_creation():
    """Test that the storage directory is created if it doesn't exist."""
    # Even if the directory doesn't exist, calling the function should create it
    data_dir = get_iterations_data_directory()
    
    # The directory should exist now
    assert data_dir.exists()
    assert data_dir.is_dir()
    
    # Creating it again should not cause errors (idempotent)
    data_dir2 = get_iterations_data_directory()
    assert data_dir == data_dir2
    assert data_dir2.exists()


def test_manager_storage_operations():
    """Test that manager's storage can perform basic operations."""
    config = {}
    manager = IterationTrackerManager(config)
    
    # Verify storage can check for board existence
    board_exists = manager.storage.board_exists()
    assert isinstance(board_exists, bool)
    
    # Verify storage has correct data directory
    assert manager.storage.data_dir.exists()
    # On Windows, paths use backslashes
    assert str(manager.storage.data_dir).replace("\\", "/").endswith(".amplifier/iterations")

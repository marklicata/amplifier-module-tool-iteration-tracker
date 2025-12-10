"""
Tests for the Iteration Storage
"""

import tempfile
from pathlib import Path
import json

import pytest

from .storage import IterationStorage
from .board import IterationBoard
from .models import Iteration, IterationStatus


def test_storage_initialization():
    """Test storage initialization with data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Verify storage has correct data directory
        assert storage.data_dir == data_dir
        assert storage.data_dir.exists()
        
        # Verify board file path is set correctly
        expected_board_file = data_dir / "iteration_board.json"
        assert storage._board_file == expected_board_file


def test_storage_save_and_load_board():
    """Test saving and loading a board."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Create a board with some data
        board = IterationBoard()
        iteration = board.create_iteration(
            name="Test Iteration",
            goal="Test goal",
            status=IterationStatus.PLANNING
        )
        
        # Save the board
        storage.save_board(board)
        
        # Verify file was created
        assert storage._board_file.exists()
        
        # Load the board
        loaded_board = storage.load_board()
        
        # Verify board was loaded correctly
        iterations = loaded_board.list_iterations()
        assert len(iterations) == 1
        assert iterations[0].name == "Test Iteration"


def test_storage_load_empty_board():
    """Test loading when no board file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Load should return empty board when file doesn't exist
        board = storage.load_board()
        
        assert isinstance(board, IterationBoard)
        assert len(board.list_iterations()) == 0


def test_storage_board_exists():
    """Test board_exists method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Initially, board should not exist
        assert storage.board_exists() is False
        
        # Save a board
        board = IterationBoard()
        storage.save_board(board)
        
        # Now board should exist
        assert storage.board_exists() is True


def test_storage_delete_board():
    """Test deleting a board."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Save a board
        board = IterationBoard()
        storage.save_board(board)
        assert storage.board_exists() is True
        
        # Delete the board
        result = storage.delete_board()
        assert result is True
        assert storage.board_exists() is False
        
        # Deleting again should return False
        result = storage.delete_board()
        assert result is False


def test_storage_backup_board():
    """Test creating a backup of a board."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Save a board
        board = IterationBoard()
        board.create_iteration(
            name="Test Iteration",
            status=IterationStatus.ACTIVE
        )
        storage.save_board(board)
        
        # Create a backup
        backup_path = storage.backup_board(suffix="_manual")
        
        # Verify backup was created
        assert backup_path.exists()
        assert backup_path.parent == data_dir / "backups"
        assert "_manual" in backup_path.name
        
        # Verify backup contains same data
        with open(backup_path, "r") as f:
            backup_data = json.load(f)
        assert "iterations" in backup_data or "_iterations" in backup_data


def test_storage_list_backups():
    """Test listing backup files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Initially, no backups
        backups = storage.list_backups()
        assert len(backups) == 0
        
        # Save and backup a board multiple times
        board = IterationBoard()
        storage.save_board(board)
        
        storage.backup_board(suffix="_1")
        storage.backup_board(suffix="_2")
        
        # Now there should be backups
        backups = storage.list_backups()
        assert len(backups) == 2


def test_storage_restore_backup():
    """Test restoring from a backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        storage = IterationStorage(data_dir)
        
        # Create and save a board with data
        board = IterationBoard()
        board.create_iteration(
            name="Original Iteration",
            status=IterationStatus.ACTIVE
        )
        storage.save_board(board)
        
        # Create a backup
        backup_path = storage.backup_board()
        
        # Modify the board
        board = IterationBoard()
        board.create_iteration(
            name="Modified Iteration",
            status=IterationStatus.COMPLETED
        )
        storage.save_board(board)
        
        # Restore from backup
        restored_board = storage.restore_backup(backup_path)
        
        # Verify restored board has original data
        iterations = restored_board.list_iterations()
        assert len(iterations) == 1
        assert iterations[0].name == "Original Iteration"
        
        # Verify current board file also has original data
        current_board = storage.load_board()
        current_iterations = current_board.list_iterations()
        assert current_iterations[0].name == "Original Iteration"


def test_storage_directory_creation():
    """Test that storage creates data directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a subdirectory that doesn't exist yet
        data_dir = Path(tmpdir) / "nested" / "data" / "iterations"
        
        # Directory shouldn't exist yet
        assert not data_dir.exists()
        
        # Creating storage should create the directory
        storage = IterationStorage(data_dir)
        
        # Now directory should exist
        assert data_dir.exists()
        assert data_dir.is_dir()

"""
Persistence layer for iteration boards.
"""

import json
from pathlib import Path
from typing import Optional

from .board import IterationBoard


class IterationStorage:
    """
    Handles saving and loading iteration boards to disk.
    
    Example:
        storage = IterationStorage("./data")
        storage.save_board(board)
        board = storage.load_board()
    """
    
    def __init__(self, data_dir: str | Path):
        """
        Initialize storage.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._board_file = self.data_dir / "iteration_board.json"
    
    def save_board(self, board: IterationBoard) -> None:
        """Save board to disk."""
        data = board.to_dict()
        with open(self._board_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_board(self) -> IterationBoard:
        """Load board from disk. Returns empty board if file doesn't exist."""
        if not self._board_file.exists():
            return IterationBoard()
        
        with open(self._board_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return IterationBoard.from_dict(data)
    
    def board_exists(self) -> bool:
        """Check if a saved board exists."""
        return self._board_file.exists()
    
    def delete_board(self) -> bool:
        """Delete the saved board."""
        if self._board_file.exists():
            self._board_file.unlink()
            return True
        return False
    
    def backup_board(self, suffix: str = "") -> Path:
        """
        Create a backup of the current board.
        
        Args:
            suffix: Optional suffix for backup filename
            
        Returns:
            Path to backup file
        """
        if not self._board_file.exists():
            raise FileNotFoundError("No board to backup")
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"iteration_board_{timestamp}{suffix}.json"
        backup_path = self.data_dir / "backups" / backup_name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(self._board_file, backup_path)
        
        return backup_path
    
    def list_backups(self) -> list[Path]:
        """List all backup files."""
        backup_dir = self.data_dir / "backups"
        if not backup_dir.exists():
            return []
        return sorted(backup_dir.glob("iteration_board_*.json"))
    
    def restore_backup(self, backup_path: Path) -> IterationBoard:
        """Restore a board from a backup file."""
        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        board = IterationBoard.from_dict(data)
        self.save_board(board)
        return board

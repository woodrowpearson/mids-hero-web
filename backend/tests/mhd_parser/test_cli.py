"""Tests for MHD parser CLI."""

import io
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from app.mhd_parser.cli import MhdParserCLI, setup_logging


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_setup_logging(self):
        """Test logging setup."""
        # Should not raise
        setup_logging("INFO")
        setup_logging("DEBUG")
        
        with pytest.raises(ValueError):
            setup_logging("INVALID")
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        cli = MhdParserCLI()
        
        result = cli.parse_file(Path("nonexistent.mhd"))
        assert result is False
    
    def test_parse_file_success(self):
        """Test successful file parsing."""
        cli = MhdParserCLI()
        
        with tempfile.NamedTemporaryFile(suffix=".mhd", delete=False) as tmp:
            # Write a minimal text MHD file
            tmp.write(b"Version 1.0\nData line 1\nData line 2")
            tmp_path = Path(tmp.name)
        
        try:
            result = cli.parse_file(tmp_path, dry_run=True)
            assert result is True
        finally:
            tmp_path.unlink()
    
    def test_parse_file_with_json_export(self):
        """Test file parsing with JSON export."""
        cli = MhdParserCLI()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.mhd"
            test_file.write_bytes(b"Version 1.0\nTest data")
            
            # Parse with JSON export
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            result = cli.parse_file(test_file, output_dir, export_json=True)
            assert result is True
            
            # Check JSON was created
            json_file = output_dir / "test.json"
            assert json_file.exists()
    
    def test_parse_directory(self):
        """Test parsing directory of files."""
        cli = MhdParserCLI()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create test files
            (tmpdir_path / "file1.mhd").write_bytes(b"Version 1.0\nFile 1")
            (tmpdir_path / "file2.mhd").write_bytes(b"Version 1.0\nFile 2")
            (tmpdir_path / "other.txt").write_bytes(b"Not MHD")
            
            # Parse directory
            count = cli.parse_directory(tmpdir_path, "*.mhd", dry_run=True)
            assert count == 2
    
    def test_parse_directory_not_found(self):
        """Test parsing non-existent directory."""
        cli = MhdParserCLI()
        
        count = cli.parse_directory(Path("nonexistent"), dry_run=True)
        assert count == 0
    
    def test_validate_file_success(self):
        """Test file validation."""
        cli = MhdParserCLI()
        
        with tempfile.NamedTemporaryFile(suffix=".mhd", delete=False) as tmp:
            tmp.write(b"Version 1.0\nValid data")
            tmp_path = Path(tmp.name)
        
        try:
            result = cli.validate_file(tmp_path)
            assert result is True
        finally:
            tmp_path.unlink()
    
    def test_validate_file_invalid(self):
        """Test validation of invalid file."""
        cli = MhdParserCLI()
        
        with tempfile.NamedTemporaryFile(suffix=".mhd", delete=False) as tmp:
            # Write invalid binary data
            tmp.write(b"\xFF\xFF\xFF\xFF")
            tmp_path = Path(tmp.name)
        
        try:
            result = cli.validate_file(tmp_path)
            assert result is False
        finally:
            tmp_path.unlink()
    
    @patch('sys.argv', ['cli.py', 'parse', 'test.mhd', '--dry-run'])
    @patch('pathlib.Path.is_file')
    @patch('app.mhd_parser.cli.MhdParserCLI.parse_file')
    def test_main_parse_file(self, mock_parse, mock_is_file):
        """Test main entry point for file parsing."""
        mock_is_file.return_value = True
        mock_parse.return_value = True
        
        from app.mhd_parser.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_parse.assert_called_once()
    
    @patch('sys.argv', ['cli.py', '--log-level', 'DEBUG', 'validate', 'test.mhd'])
    @patch('pathlib.Path.is_file')
    @patch('app.mhd_parser.cli.MhdParserCLI.validate_file')
    def test_main_validate_file(self, mock_validate, mock_is_file):
        """Test main entry point for file validation."""
        mock_is_file.return_value = True
        mock_validate.return_value = True
        
        from app.mhd_parser.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_validate.assert_called_once()
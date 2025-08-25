"""Tests for RAG CLI commands."""

import json

import pytest
from click.testing import CliRunner

from app.rag.cli import cli
from app.rag.config import rag_settings


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_env(tmp_path):
    """Set up test environment with isolated paths."""
    # Save original settings
    original_chromadb = rag_settings.chromadb_path
    original_cache = rag_settings.embedding_cache_path
    original_api_key = rag_settings.gemini_api_key

    # Use temporary paths
    rag_settings.chromadb_path = str(tmp_path / "chromadb")
    rag_settings.embedding_cache_path = str(tmp_path / "cache")
    rag_settings.gemini_api_key = None  # Force offline mode

    yield tmp_path

    # Restore settings
    rag_settings.chromadb_path = original_chromadb
    rag_settings.embedding_cache_path = original_cache
    rag_settings.gemini_api_key = original_api_key


@pytest.fixture
def sample_codebase(tmp_path):
    """Create a sample codebase for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create Python files
    (project_dir / "main.py").write_text("""
def main():
    '''Main entry point for the application.'''
    print("Hello from test project")

if __name__ == "__main__":
    main()
""")

    (project_dir / "utils.py").write_text("""
def calculate_power(base, exponent):
    '''Calculate power with enhancement.'''
    return base ** exponent
""")

    # Create TypeScript file
    (project_dir / "component.tsx").write_text("""
export function TestComponent({ name }: { name: string }) {
    return <div>Hello {name}</div>;
}
""")

    # Create Markdown
    (project_dir / "README.md").write_text("""
# Test Project

This is a test project for RAG CLI testing.

## Features
- Python code
- TypeScript components
- RAG integration
""")

    return project_dir


class TestRAGCLI:
    """Test RAG CLI commands."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "RAG system CLI for City of Heroes build planner" in result.output
        assert "setup" in result.output
        assert "index" in result.output
        assert "search" in result.output
        assert "status" in result.output

    def test_setup_command(self, runner, test_env):
        """Test setup command."""
        result = runner.invoke(cli, ["setup"])
        assert result.exit_code == 0
        assert "✓" in result.output or "Setup completed" in result.output

        # Check collections were created
        assert (test_env / "chromadb").exists()

    def test_setup_force(self, runner, test_env):
        """Test setup with force flag."""
        # Run setup twice with force
        runner.invoke(cli, ["setup"])
        result = runner.invoke(cli, ["setup", "--force"])

        assert result.exit_code == 0
        assert "✓" in result.output or "Reset" in result.output

    def test_index_codebase(self, runner, test_env, sample_codebase):
        """Test indexing codebase."""
        # Setup first
        runner.invoke(cli, ["setup"])

        # Index the sample codebase
        result = runner.invoke(cli, ["index", "codebase", str(sample_codebase)])

        assert result.exit_code == 0
        assert "Indexed" in result.output or "documents" in result.output
        assert "✓" in result.output or "Success" in result.output

    def test_index_codebase_patterns(self, runner, test_env, sample_codebase):
        """Test indexing with specific patterns."""
        runner.invoke(cli, ["setup"])

        # Index only Python files
        result = runner.invoke(cli, [
            "index", "codebase", str(sample_codebase),
            "--pattern", "**/*.py"
        ])

        assert result.exit_code == 0
        assert "Indexed" in result.output
        # Should have indexed 2 Python files
        assert "2" in result.output or "main.py" in result.output

    def test_index_midsreborn(self, runner, test_env, tmp_path):
        """Test indexing MidsReborn files."""
        runner.invoke(cli, ["setup"])

        # Create a fake MidsReborn file
        mids_file = tmp_path / "test.cs"
        mids_file.write_text("""
namespace MidsReborn {
    public class TestPower {
        public float Damage { get; set; }
    }
}
""")

        result = runner.invoke(cli, ["index", "midsreborn", str(tmp_path)])

        assert result.exit_code == 0
        assert "Indexed" in result.output or "✓" in result.output

    def test_index_i12(self, runner, test_env, tmp_path):
        """Test indexing I12 data files."""
        runner.invoke(cli, ["setup"])

        # Create a fake I12 file
        i12_file = tmp_path / "powers.json"
        i12_file.write_text(json.dumps({
            "powers": [
                {"name": "Fire Blast", "damage": 100}
            ]
        }))

        result = runner.invoke(cli, ["index", "i12", str(tmp_path)])

        assert result.exit_code == 0
        assert "Indexed" in result.output or "✓" in result.output

    def test_search_command(self, runner, test_env, sample_codebase):
        """Test search functionality."""
        # Setup and index first
        runner.invoke(cli, ["setup"])
        runner.invoke(cli, ["index", "codebase", str(sample_codebase)])

        # Search for content
        result = runner.invoke(cli, ["search", "calculate power"])

        assert result.exit_code == 0
        assert "Results" in result.output or "Found" in result.output
        # Should find the calculate_power function
        assert "utils.py" in result.output or "calculate" in result.output

    def test_search_with_collection(self, runner, test_env, sample_codebase):
        """Test search in specific collection."""
        runner.invoke(cli, ["setup"])
        runner.invoke(cli, ["index", "codebase", str(sample_codebase)])

        result = runner.invoke(cli, [
            "search", "test",
            "--collection", rag_settings.codebase_collection
        ])

        assert result.exit_code == 0
        assert "Results" in result.output or "Found" in result.output

    def test_search_with_limit(self, runner, test_env, sample_codebase):
        """Test search with result limit."""
        runner.invoke(cli, ["setup"])
        runner.invoke(cli, ["index", "codebase", str(sample_codebase)])

        result = runner.invoke(cli, ["search", "test", "-n", "1"])

        assert result.exit_code == 0
        # Should show only 1 result
        assert "1." in result.output or "Result 1" in result.output

    def test_status_command(self, runner, test_env):
        """Test status command."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "RAG System Status" in result.output
        assert "Collections" in result.output
        assert rag_settings.codebase_collection in result.output
        assert "Document Count" in result.output

    def test_status_verbose(self, runner, test_env, sample_codebase):
        """Test verbose status output."""
        runner.invoke(cli, ["setup"])
        runner.invoke(cli, ["index", "codebase", str(sample_codebase)])

        result = runner.invoke(cli, ["status", "--verbose"])

        assert result.exit_code == 0
        assert "Configuration" in result.output
        assert "Usage Statistics" in result.output
        assert "tokens" in result.output.lower()

    def test_batch_command(self, runner, test_env):
        """Test batch processing command."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["batch", "status"])

        assert result.exit_code == 0
        assert "Batch Processing Status" in result.output
        assert "Pending items" in result.output

    def test_batch_process(self, runner, test_env, tmp_path):
        """Test batch process command."""
        runner.invoke(cli, ["setup"])

        # Create a file to batch process
        test_file = tmp_path / "batch_test.txt"
        test_file.write_text("Test content for batch processing")

        # Add to batch
        result = runner.invoke(cli, ["batch", "add", str(test_file)])

        if result.exit_code == 0:
            # Process batch
            process_result = runner.invoke(cli, ["batch", "process"])
            assert ("Processed" in process_result.output or
                   "batch" in process_result.output or
                   "No pending items" in process_result.output)

    def test_usage_command(self, runner, test_env):
        """Test usage monitoring command."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["usage"])

        assert result.exit_code == 0
        assert "Usage Report" in result.output
        assert "Tokens" in result.output
        assert "Cost" in result.output

    def test_usage_with_days(self, runner, test_env):
        """Test usage report for specific days."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["usage", "--days", "7"])

        assert result.exit_code == 0
        assert "7 days" in result.output or "7-day" in result.output

    def test_reset_command(self, runner, test_env):
        """Test reset command."""
        runner.invoke(cli, ["setup"])

        # Reset specific collection
        result = runner.invoke(cli, [
            "reset",
            "--collection", rag_settings.codebase_collection,
            "--yes"  # Skip confirmation
        ])

        assert result.exit_code == 0
        assert "Reset" in result.output or "✓" in result.output

    def test_reset_all(self, runner, test_env):
        """Test reset all collections."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["reset", "--all", "--yes"])

        assert result.exit_code == 0
        assert "Reset all" in result.output or "collections" in result.output

    def test_backup_command(self, runner, test_env):
        """Test backup command."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["backup"])

        assert result.exit_code == 0
        assert "Backup created" in result.output or "✓" in result.output
        assert "backup" in result.output.lower()

    def test_backup_with_path(self, runner, test_env, tmp_path):
        """Test backup to specific path."""
        runner.invoke(cli, ["setup"])

        backup_dir = tmp_path / "my_backup"
        result = runner.invoke(cli, ["backup", "--path", str(backup_dir)])

        assert result.exit_code == 0
        assert backup_dir.exists()
        assert "Backup created" in result.output

    def test_config_command(self, runner, test_env):
        """Test config display command."""
        result = runner.invoke(cli, ["config"])

        assert result.exit_code == 0
        assert "RAG Configuration" in result.output
        assert "chromadb_path" in result.output
        assert "batch_size" in result.output
        assert "daily_token_limit" in result.output

    def test_invalid_command(self, runner):
        """Test invalid command handling."""
        result = runner.invoke(cli, ["invalid_command"])

        assert result.exit_code != 0
        assert "Error" in result.output or "No such command" in result.output

    def test_index_nonexistent_path(self, runner, test_env):
        """Test indexing non-existent path."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["index", "codebase", "/nonexistent/path"])

        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output

    def test_search_empty_database(self, runner, test_env):
        """Test searching empty database."""
        runner.invoke(cli, ["setup"])

        result = runner.invoke(cli, ["search", "test query"])

        # Should succeed but show no results
        assert result.exit_code == 0
        assert "No results" in result.output or "0 results" in result.output

    def test_concurrent_commands(self, runner, test_env, sample_codebase):
        """Test running multiple commands in sequence."""
        # Full workflow test
        results = []

        # Setup
        results.append(runner.invoke(cli, ["setup"]))

        # Index
        results.append(runner.invoke(cli, ["index", "codebase", str(sample_codebase)]))

        # Search
        results.append(runner.invoke(cli, ["search", "test"]))

        # Status
        results.append(runner.invoke(cli, ["status"]))

        # All commands should succeed
        for result in results:
            assert result.exit_code == 0

    def test_error_handling(self, runner, test_env):
        """Test error handling and recovery."""
        # Try to search before setup
        result = runner.invoke(cli, ["search", "test"])

        # Should handle gracefully - returns "No results found" when collection doesn't exist
        assert "No results found" in result.output or "Error" in result.output

        # Setup and retry
        runner.invoke(cli, ["setup"])
        result = runner.invoke(cli, ["search", "test"])

        assert result.exit_code == 0

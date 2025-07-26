#!/usr/bin/env python3
"""Test that session management uses project directory correctly."""

from pathlib import Path
from session_summarizer import SessionSummarizer
from session_continuity import SessionContinuityManager
from threshold_config import ThresholdManager
from auto_summarizer import AutoSummarizer


def test_project_directory_usage():
    """Test that all components use project directory."""
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / ".git").exists():
            break
        project_root = project_root.parent
    
    expected_sessions_dir = project_root / ".claude" / "sessions"
    expected_thresholds_path = project_root / ".claude" / "thresholds.json"
    
    print("🧪 Testing Project Directory Usage")
    print(f"   Project root: {project_root}")
    print(f"   Expected sessions: {expected_sessions_dir}")
    
    # Test SessionSummarizer
    summarizer = SessionSummarizer(api_key="test-key")
    assert summarizer.state_dir == expected_sessions_dir, f"SessionSummarizer using wrong dir: {summarizer.state_dir}"
    print("✅ SessionSummarizer uses project directory")
    
    # Test SessionContinuityManager
    continuity = SessionContinuityManager()
    assert continuity.state_dir == expected_sessions_dir, f"SessionContinuityManager using wrong dir: {continuity.state_dir}"
    print("✅ SessionContinuityManager uses project directory")
    
    # Test ThresholdManager
    thresholds = ThresholdManager()
    assert thresholds.config_path == expected_thresholds_path, f"ThresholdManager using wrong path: {thresholds.config_path}"
    print("✅ ThresholdManager uses project directory")
    
    # Test AutoSummarizer
    auto_summarizer = AutoSummarizer(session_id="test_project_dir")
    assert auto_summarizer.state_dir == expected_sessions_dir, f"AutoSummarizer using wrong dir: {auto_summarizer.state_dir}"
    print("✅ AutoSummarizer uses project directory")
    
    # Check that files are created in correct location
    test_files = [
        expected_sessions_dir / "session_metadata.json",
        expected_thresholds_path,
    ]
    
    print("\n📁 Checking file locations:")
    for file_path in test_files:
        if file_path.exists():
            print(f"   ✓ {file_path.relative_to(project_root)}")
        else:
            print(f"   ✗ {file_path.relative_to(project_root)} (not created yet)")
    
    print("\n✅ All components correctly use project directory!")


if __name__ == "__main__":
    test_project_directory_usage()
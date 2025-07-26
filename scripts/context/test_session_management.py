#!/usr/bin/env python3
"""Integration tests for session management components."""

import json
import os
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Import all components
from session_summarizer import SessionSummarizer
from session_continuity import SessionContinuityManager
from threshold_config import ThresholdManager, AdaptiveThresholdManager
from summary_validator import SummaryQualityValidator, QualityMetrics
from auto_summarizer import AutoSummarizer, ConversationHook


class TestSessionManagement(unittest.TestCase):
    """Integration tests for session management system."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_session_summarizer_basic(self):
        """Test basic session summarization."""
        summarizer = SessionSummarizer(
            api_key="test-key",  # Mock will handle this
            state_dir=self.test_path
        )

        # Test conversation
        conversation = [
            {"role": "user", "content": "Create a Python function to calculate factorial"},
            {"role": "assistant", "content": "I'll create a factorial function in factorial.py"},
            {"role": "user", "content": "Add error handling for negative numbers"},
            {"role": "assistant", "content": "I've added error handling. The function now raises ValueError for negative inputs."},
        ]

        # Test token counting
        tokens = sum(summarizer.count_tokens(msg["content"]) for msg in conversation)
        self.assertGreater(tokens, 0)

        # Test key information extraction
        key_info = summarizer.extract_key_information(conversation)
        self.assertIn("files_modified", key_info)
        self.assertIn("commands_run", key_info)

        # Test session state saving
        session_id = "test_session_001"
        state_file = summarizer.save_session_state(
            session_id, "Test summary", {"test": "metadata"}
        )
        self.assertTrue(state_file.exists())

        # Test loading state
        loaded_state = summarizer.load_session_state(session_id)
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state["summary"], "Test summary")

    def test_session_continuity(self):
        """Test session continuity management."""
        manager = SessionContinuityManager(
            state_dir=self.test_path,
            session_timeout_hours=24
        )

        # Create session
        session_id = manager.create_session("test_session")
        self.assertEqual(session_id, "test_session")
        self.assertEqual(manager.get_active_session(), session_id)

        # Update session
        manager.update_session(session_id, {"task": "Testing continuity"})
        info = manager.get_session_info(session_id)
        self.assertEqual(info["task"], "Testing continuity")

        # Find related sessions
        manager.create_session("test_session_2")
        related = manager.find_related_sessions({"status": "active"})
        self.assertGreaterEqual(len(related), 2)

        # Test session linking
        manager.link_sessions(session_id, "test_session_2")
        info = manager.get_session_info(session_id)
        self.assertIn("test_session_2", info["related_sessions"])

    def test_threshold_configuration(self):
        """Test threshold configuration system."""
        config_path = self.test_path / "thresholds.json"
        manager = ThresholdManager(config_path)

        # Test defaults
        self.assertEqual(manager.get("max_context_tokens"), 90000)
        self.assertEqual(manager.get("summary_trigger_percent"), 0.8)

        # Test updates
        manager.set("max_context_tokens", 100000)
        self.assertEqual(manager.get("max_context_tokens"), 100000)

        # Test persistence
        manager2 = ThresholdManager(config_path)
        self.assertEqual(manager2.get("max_context_tokens"), 100000)

        # Test validation
        self.assertTrue(manager.validate())

        # Test calculations
        token_threshold = manager.get_token_threshold()
        self.assertEqual(token_threshold, 80000)  # 100000 * 0.8

    def test_adaptive_thresholds(self):
        """Test adaptive threshold management."""
        config_path = self.test_path / "adaptive_thresholds.json"
        manager = AdaptiveThresholdManager(config_path)

        # Record performance metrics
        for i in range(15):
            manager.record_summary_performance(
                time_seconds=25.0 + i,
                token_count=50000 + i * 1000,
                quality_score=0.8 - i * 0.01
            )

        # Check if thresholds adapted
        # Should have adjusted due to high summary times
        self.assertLess(
            manager.config.summary_trigger_percent,
            0.8  # Should be less than default
        )

    def test_summary_quality_validation(self):
        """Test summary quality validation."""
        validator = SummaryQualityValidator()

        conversation = [
            {"role": "user", "content": "Create a REST API endpoint for user registration"},
            {"role": "assistant", "content": "I'll create the endpoint in /api/register.py"},
            {"role": "user", "content": "Add email validation"},
            {"role": "assistant", "content": "Added email validation using regex pattern"},
        ]

        key_info = {
            "files_modified": ["/api/register.py"],
            "commands_run": [],
            "todos": ["Add unit tests"],
            "errors_encountered": []
        }

        # Test good summary
        good_summary = "Created user registration API endpoint in /api/register.py with email validation. TODO: Add unit tests."
        metrics, issues = validator.validate_summary(good_summary, conversation, key_info)
        self.assertGreater(metrics.overall_score, 0.7)
        self.assertLessEqual(len(issues), 1)  # Allow minor issues for "good" summary

        # Test poor summary
        poor_summary = "Did something."
        metrics, issues = validator.validate_summary(poor_summary, conversation, key_info)
        self.assertLess(metrics.overall_score, 0.5)
        self.assertGreater(len(issues), 0)

    @patch('openai.OpenAI')
    def test_auto_summarizer(self, mock_openai):
        """Test automatic summarization."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test summary"))]
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = AutoSummarizer(
            session_id="test_auto",
            state_dir=self.test_path
        )

        # Add messages
        messages = [
            ("user", "Help me debug this error"),
            ("assistant", "I'll help you debug. What's the error message?"),
            ("user", "TypeError in line 42"),
            ("assistant", "The error is due to incorrect type. Fixed in debug.py"),
        ]

        for role, content in messages:
            summarizer.add_message(role, content)

        # Check status
        status = summarizer.get_status()
        self.assertEqual(status["buffer_size"], 4)
        self.assertFalse(status["should_summarize"])

        # Test conversation hook
        hook = ConversationHook(summarizer)
        hook.on_user_message("Another message")
        hook.on_assistant_message("Response to message")

        # Verify state saved
        state_file = self.test_path / "test_auto_auto_state.json"
        self.assertTrue(state_file.exists())

    def test_integration_flow(self):
        """Test complete integration flow."""
        # Set up components
        config_path = self.test_path / "integration_thresholds.json"
        threshold_manager = ThresholdManager(config_path)
        threshold_manager.set("min_messages_for_summary", 3)
        threshold_manager.set("summary_trigger_percent", 0.5)

        summarizer = SessionSummarizer(
            api_key="test-key",
            state_dir=self.test_path,
            max_context_tokens=1000,
            summary_threshold=0.5
        )

        continuity = SessionContinuityManager(state_dir=self.test_path)
        session_id = continuity.create_session("integration_test")

        # Simulate conversation
        conversation = [
            {"role": "user", "content": "Help me create a Django model"},
            {"role": "assistant", "content": "I'll create a User model in models.py"},
            {"role": "user", "content": "Add email field"},
            {"role": "assistant", "content": "Added EmailField to the User model"},
        ]

        # Check if should summarize
        should_summarize = summarizer.should_summarize(conversation)
        
        # Extract and validate
        key_info = summarizer.extract_key_information(conversation)
        self.assertIsInstance(key_info["files_modified"], list)

        # Save state
        summarizer.save_session_state(
            session_id,
            "Created Django User model with email field",
            key_info
        )

        # Restore context
        restored_id, context = continuity.restore_context(session_id)
        self.assertEqual(restored_id, session_id)
        self.assertIsNotNone(context)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Running Session Management Integration Tests\n")
        run_tests()
        print("\n✅ All tests completed")
    else:
        print("Session Management Test Suite")
        print("Usage: python test_session_management.py test")
#!/usr/bin/env python3
"""Automatic Summary Injection for Claude Context Management.

This module provides functionality to automatically monitor conversations,
generate summaries when needed, and inject them seamlessly into the context.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from threading import Thread, Event

from session_summarizer import SessionSummarizer
from session_continuity import SessionContinuityManager
from threshold_config import ThresholdManager
from summary_validator import SummaryQualityValidator


class AutoSummarizer:
    """Automatically monitors and summarizes conversations."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        state_dir: Optional[Path] = None,
        callback: Optional[Callable[[str], None]] = None,
    ):
        """Initialize AutoSummarizer.

        Args:
            session_id: Session to monitor
            state_dir: Directory for state storage
            callback: Callback function for summary notifications
        """
        self.state_dir = state_dir or self._get_project_sessions_dir()
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.summarizer = SessionSummarizer(api_key=os.getenv("OPENAI_API_KEY", "test-key"), state_dir=self.state_dir)
        self.continuity = SessionContinuityManager(state_dir=self.state_dir)
        self.thresholds = ThresholdManager()
        self.validator = SummaryQualityValidator()

        # Session management
        self.session_id = session_id or self.continuity.create_session()
        self.callback = callback

        # Monitoring state
        self.conversation_buffer: List[Dict[str, str]] = []
        self.last_summary_time = time.time()
        self.monitoring = False
        self.monitor_thread: Optional[Thread] = None
        self.stop_event = Event()

        # Load previous state if resuming
        self._restore_state()

    def _get_project_sessions_dir(self) -> Path:
        """Get the project-specific sessions directory."""
        # Find project root by looking for .git
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current / ".claude" / "sessions"
            current = current.parent
        
        # Fallback to current directory if no git root found
        return Path.cwd() / ".claude" / "sessions"

    def _restore_state(self):
        """Restore state from previous session if available."""
        state_file = self.state_dir / f"{self.session_id}_auto_state.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                    self.conversation_buffer = state.get("conversation_buffer", [])
                    self.last_summary_time = state.get("last_summary_time", time.time())
            except Exception:
                pass

    def _save_state(self):
        """Save current state to disk."""
        state_file = self.state_dir / f"{self.session_id}_auto_state.json"
        state = {
            "session_id": self.session_id,
            "conversation_buffer": self.conversation_buffer,
            "last_summary_time": self.last_summary_time,
            "timestamp": datetime.now().isoformat(),
        }
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def add_message(self, role: str, content: str):
        """Add a message to the conversation buffer.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
        """
        self.conversation_buffer.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_state()

    def should_summarize_now(self) -> Tuple[bool, str]:
        """Check if summarization should happen now.

        Returns:
            Tuple of (should_summarize, reason)
        """
        # Check token count
        total_tokens = sum(
            self.summarizer.count_tokens(msg["content"])
            for msg in self.conversation_buffer
        )
        token_threshold = self.thresholds.get_token_threshold()

        if total_tokens >= token_threshold:
            return True, f"Token limit reached ({total_tokens}/{token_threshold})"

        # Check message count
        message_count = len(self.conversation_buffer)
        min_messages = self.thresholds.get("min_messages_for_summary", 20)

        if message_count >= min_messages:
            # Check time since last summary
            hours_since_summary = (time.time() - self.last_summary_time) / 3600
            auto_interval = self.thresholds.get("auto_summary_interval_hours", 2.0)

            if hours_since_summary >= auto_interval:
                return True, f"Time interval reached ({hours_since_summary:.1f}h)"

        # Check for critical token threshold
        critical_threshold = self.thresholds.get_critical_token_threshold()
        if total_tokens >= critical_threshold:
            return True, f"Critical token limit ({total_tokens}/{critical_threshold})"

        return False, "No summarization needed"

    def generate_and_validate_summary(self) -> Optional[Tuple[str, Dict]]:
        """Generate and validate a summary.

        Returns:
            Tuple of (summary, metadata) or None if failed
        """
        if len(self.conversation_buffer) < 5:
            return None  # Too few messages

        # Extract key information
        key_info = self.summarizer.extract_key_information(self.conversation_buffer)

        # Generate summary
        summary = self.summarizer.generate_summary(self.conversation_buffer, key_info)

        if not summary:
            return None

        # Validate quality
        metrics, issues = self.validator.validate_summary(
            summary, self.conversation_buffer, key_info
        )

        # Try to improve if needed
        if metrics.overall_score < self.thresholds.get("min_summary_quality_score", 0.7):
            improved = self.validator.improve_summary(summary, metrics, issues)
            if improved:
                summary = improved
                # Re-validate
                metrics, issues = self.validator.validate_summary(
                    summary, self.conversation_buffer, key_info
                )

        # Prepare metadata
        metadata = {
            "quality_metrics": metrics.to_dict(),
            "issues": issues,
            "message_count": len(self.conversation_buffer),
            "token_count": sum(
                self.summarizer.count_tokens(msg["content"])
                for msg in self.conversation_buffer
            ),
            **key_info,
        }

        return summary, metadata

    def perform_auto_summary(self) -> Optional[str]:
        """Perform automatic summarization.

        Returns:
            Summary text or None if failed
        """
        should_summarize, reason = self.should_summarize_now()
        if not should_summarize:
            return None

        print(f"[AutoSummarizer] Triggering summary: {reason}")

        # Generate and validate summary
        result = self.generate_and_validate_summary()
        if not result:
            return None

        summary, metadata = result

        # Save state
        self.summarizer.save_session_state(self.session_id, summary, metadata)

        # Update continuity
        self.continuity.update_session({
            "last_summary": datetime.now().isoformat(),
            "summary_reason": reason,
        })

        # Prune conversation buffer
        keep_messages = self.thresholds.get("max_messages_to_keep", 10)
        self.conversation_buffer = self.conversation_buffer[-keep_messages:]
        self.last_summary_time = time.time()
        self._save_state()

        # Notify callback if provided
        if self.callback:
            self.callback(summary)

        return summary

    def start_monitoring(self):
        """Start automatic monitoring in background thread."""
        if self.monitoring:
            return

        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop automatic monitoring."""
        self.monitoring = False
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring and not self.stop_event.is_set():
            try:
                # Check if summarization needed
                should_summarize, _ = self.should_summarize_now()
                if should_summarize:
                    self.perform_auto_summary()

                # Sleep for a short interval
                self.stop_event.wait(30)  # Check every 30 seconds
            except Exception as e:
                print(f"[AutoSummarizer] Error in monitor loop: {e}")

    def inject_summary_context(self, conversation: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Inject summary context into conversation.

        Args:
            conversation: Current conversation

        Returns:
            Updated conversation with summary context
        """
        # Get recent summaries
        recent_sessions = self.summarizer.get_recent_sessions(limit=3)
        if not recent_sessions:
            return conversation

        # Format context message
        context_parts = ["[Context from previous sessions:]"]
        for session in recent_sessions:
            summary = session.get("summary", "")[:200]
            timestamp = session.get("timestamp", "")
            context_parts.append(f"- {timestamp}: {summary}...")

        context_message = {
            "role": "system",
            "content": "\n".join(context_parts),
        }

        # Insert at beginning of conversation
        return [context_message] + conversation

    def get_status(self) -> Dict:
        """Get current auto-summarizer status.

        Returns:
            Status dictionary
        """
        total_tokens = sum(
            self.summarizer.count_tokens(msg["content"])
            for msg in self.conversation_buffer
        )
        
        should_summarize, reason = self.should_summarize_now()

        return {
            "session_id": self.session_id,
            "monitoring": self.monitoring,
            "buffer_size": len(self.conversation_buffer),
            "total_tokens": total_tokens,
            "token_threshold": self.thresholds.get_token_threshold(),
            "should_summarize": should_summarize,
            "reason": reason,
            "last_summary": datetime.fromtimestamp(self.last_summary_time).isoformat(),
        }


class ConversationHook:
    """Hook for integrating with Claude's conversation flow."""

    def __init__(self, auto_summarizer: AutoSummarizer):
        """Initialize conversation hook.

        Args:
            auto_summarizer: AutoSummarizer instance
        """
        self.auto_summarizer = auto_summarizer

    def on_user_message(self, content: str):
        """Called when user sends a message."""
        self.auto_summarizer.add_message("user", content)

    def on_assistant_message(self, content: str):
        """Called when assistant sends a message."""
        self.auto_summarizer.add_message("assistant", content)
        
        # Check if we need to summarize
        summary = self.auto_summarizer.perform_auto_summary()
        if summary:
            print(f"\n[Auto-Summary Generated]\n{summary}\n")

    def on_conversation_start(self) -> Optional[str]:
        """Called at conversation start.

        Returns:
            Context message to inject or None
        """
        # Try to restore context
        _, context = self.auto_summarizer.continuity.restore_context()
        if context:
            return self.auto_summarizer.continuity.format_context_message(context)
        return None


def main():
    """Example usage and testing."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Automatic Summarizer\n")

        # Create auto-summarizer with callback
        def summary_callback(summary: str):
            print(f"\n📝 Summary generated: {summary[:100]}...\n")

        auto_summarizer = AutoSummarizer(callback=summary_callback)

        # Simulate conversation
        print("Simulating conversation...")
        messages = [
            ("user", "Help me create a new API endpoint"),
            ("assistant", "I'll help you create an API endpoint. What functionality do you need?"),
            ("user", "I need to create a user registration endpoint"),
            ("assistant", "I'll create a user registration endpoint in /api/users/register"),
            ("user", "Add validation for email and password"),
            ("assistant", "I've added validation. Email must be valid and password must be 8+ chars"),
        ]

        for role, content in messages:
            print(f"{role}: {content}")
            auto_summarizer.add_message(role, content)

        # Check status
        status = auto_summarizer.get_status()
        print(f"\nStatus: {json.dumps(status, indent=2)}")

        # Force summary generation
        print("\nForcing summary generation...")
        summary = auto_summarizer.perform_auto_summary()
        if summary:
            print(f"Generated summary: {summary}")

        # Test monitoring
        print("\nStarting monitoring...")
        auto_summarizer.start_monitoring()
        time.sleep(2)
        auto_summarizer.stop_monitoring()

        # Test conversation hook
        print("\nTesting conversation hook...")
        hook = ConversationHook(auto_summarizer)
        
        context = hook.on_conversation_start()
        if context:
            print(f"Initial context: {context}")

        hook.on_user_message("What did we work on before?")
        hook.on_assistant_message("Previously, we created a user registration endpoint with validation.")

        print("\n✅ Automatic summarizer test completed")
    else:
        print("Automatic Summary Injection Module")
        print("Usage: python auto_summarizer.py test")


if __name__ == "__main__":
    main()
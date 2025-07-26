#!/usr/bin/env python3
"""Session Summarizer for Claude Context Management.

This module provides functionality to automatically summarize long conversations
and manage context efficiently to stay within token limits.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import openai
from tiktoken import encoding_for_model


class SessionSummarizer:
    """Manages session summarization for Claude conversations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_context_tokens: int = 90000,
        summary_threshold: float = 0.8,
        state_dir: Optional[Path] = None,
    ):
        """Initialize the SessionSummarizer.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for summarization
            max_context_tokens: Maximum allowed context tokens
            summary_threshold: Threshold (0-1) for triggering summarization
            state_dir: Directory for storing session state
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for summarization")

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        self.max_context_tokens = max_context_tokens
        self.summary_threshold = summary_threshold
        self.state_dir = state_dir or self._get_project_sessions_dir()
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize tokenizer
        try:
            self.encoding = encoding_for_model(model)
        except KeyError:
            # Fallback for newer models
            self.encoding = encoding_for_model("gpt-3.5-turbo")

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

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def should_summarize(self, conversation: List[Dict[str, str]]) -> bool:
        """Determine if conversation should be summarized.

        Args:
            conversation: List of message dictionaries with 'role' and 'content'

        Returns:
            True if summarization is needed
        """
        total_tokens = sum(
            self.count_tokens(msg.get("content", "")) for msg in conversation
        )
        threshold_tokens = int(self.max_context_tokens * self.summary_threshold)
        return total_tokens >= threshold_tokens

    def extract_key_information(self, conversation: List[Dict[str, str]]) -> Dict:
        """Extract key information from conversation.

        Args:
            conversation: List of message dictionaries

        Returns:
            Dictionary containing extracted information
        """
        info = {
            "files_modified": set(),
            "commands_run": [],
            "decisions_made": [],
            "todos": [],
            "errors_encountered": [],
        }

        for msg in conversation:
            content = msg.get("content", "")
            role = msg.get("role", "")

            # Extract file paths
            file_paths = re.findall(r"(?:\/[\w\-\.\/]+\.[\w]+)", content)
            info["files_modified"].update(file_paths)

            # Extract commands (bash, git, npm, etc.)
            if role == "assistant":
                commands = re.findall(r"```bash\n(.*?)\n```", content, re.DOTALL)
                info["commands_run"].extend(commands)

            # Extract TODOs
            todos = re.findall(r"(?:TODO|FIXME|XXX):\s*(.+)", content)
            info["todos"].extend(todos)

            # Extract errors
            if "error" in content.lower() or "exception" in content.lower():
                info["errors_encountered"].append(content[:200])

        # Convert set to list for JSON serialization
        info["files_modified"] = list(info["files_modified"])
        return info

    def generate_summary(
        self, conversation: List[Dict[str, str]], key_info: Optional[Dict] = None
    ) -> str:
        """Generate a summary of the conversation.

        Args:
            conversation: List of message dictionaries
            key_info: Optional pre-extracted key information

        Returns:
            Summary text
        """
        if not key_info:
            key_info = self.extract_key_information(conversation)

        # Prepare context for summarization
        context_parts = [
            "Please summarize this coding session concisely, focusing on:",
            "1. Main objectives and what was accomplished",
            "2. Key technical decisions made",
            "3. Files created or modified",
            "4. Any unresolved issues or next steps",
            "",
            f"Files modified: {', '.join(key_info['files_modified'][:10])}",
            f"Commands run: {len(key_info['commands_run'])}",
            f"Errors encountered: {len(key_info['errors_encountered'])}",
            "",
            "Conversation to summarize:",
        ]

        # Add conversation snippets (limit to recent messages)
        for msg in conversation[-20:]:  # Last 20 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:500]  # Truncate long messages
            context_parts.append(f"{role}: {content}")

        prompt = "\n".join(context_parts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

    def save_session_state(
        self, session_id: str, summary: str, metadata: Dict
    ) -> Path:
        """Save session state to disk.

        Args:
            session_id: Unique session identifier
            summary: Generated summary
            metadata: Additional metadata

        Returns:
            Path to saved state file
        """
        state_file = self.state_dir / f"{session_id}_state.json"
        state = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "metadata": metadata,
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

        return state_file

    def load_session_state(self, session_id: str) -> Optional[Dict]:
        """Load session state from disk.

        Args:
            session_id: Session identifier

        Returns:
            Session state dictionary or None if not found
        """
        state_file = self.state_dir / f"{session_id}_state.json"
        if state_file.exists():
            with open(state_file) as f:
                return json.load(f)
        return None

    def get_recent_sessions(self, limit: int = 5) -> List[Dict]:
        """Get recent session summaries.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session state dictionaries
        """
        sessions = []
        for state_file in sorted(
            self.state_dir.glob("*_state.json"), key=os.path.getmtime, reverse=True
        )[:limit]:
            with open(state_file) as f:
                sessions.append(json.load(f))
        return sessions

    def prune_conversation(
        self, conversation: List[Dict[str, str]], summary: str
    ) -> Tuple[List[Dict[str, str]], str]:
        """Prune conversation while preserving context.

        Args:
            conversation: Original conversation
            summary: Generated summary

        Returns:
            Tuple of (pruned_conversation, context_message)
        """
        # Keep only recent messages plus summary
        keep_messages = 10  # Keep last 10 messages
        pruned = conversation[-keep_messages:] if len(conversation) > keep_messages else conversation

        # Create context message
        context_message = f"[Previous conversation summarized: {summary}]"

        return pruned, context_message

    def summarize_and_continue(
        self, session_id: str, conversation: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, str]], Optional[str]]:
        """Main entry point for session summarization.

        Args:
            session_id: Unique session identifier
            conversation: Current conversation

        Returns:
            Tuple of (updated_conversation, summary)
        """
        if not self.should_summarize(conversation):
            return conversation, None

        # Extract key information
        key_info = self.extract_key_information(conversation)

        # Generate summary
        summary = self.generate_summary(conversation, key_info)

        # Save session state
        metadata = {
            "original_message_count": len(conversation),
            "token_count": sum(
                self.count_tokens(msg.get("content", "")) for msg in conversation
            ),
            **key_info,
        }
        self.save_session_state(session_id, summary, metadata)

        # Prune conversation
        pruned_conversation, context_msg = self.prune_conversation(
            conversation, summary
        )

        # Insert context message at the beginning
        updated_conversation = [
            {"role": "system", "content": context_msg}
        ] + pruned_conversation

        return updated_conversation, summary


def main():
    """Example usage and testing."""
    import sys

    # Check if running as script
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode
        summarizer = SessionSummarizer(api_key="test-api-key")

        # Create test conversation
        test_conversation = [
            {"role": "user", "content": "Help me create a React component"},
            {
                "role": "assistant",
                "content": "I'll help you create a React component. Let me create a file at /src/components/MyComponent.tsx",
            },
            {"role": "user", "content": "Add props for name and age"},
            {
                "role": "assistant",
                "content": "I'll add the props. Here's the updated component with name and age props.",
            },
        ]

        # Test token counting
        print(f"Token count: {sum(summarizer.count_tokens(msg['content']) for msg in test_conversation)}")

        # Test summarization
        if summarizer.should_summarize(test_conversation):
            print("Summarization triggered")
            summary = summarizer.generate_summary(test_conversation)
            print(f"Summary: {summary}")

        print("✅ Session summarizer test completed")
    else:
        print("Session Summarizer Module")
        print("Usage: python session_summarizer.py test")


if __name__ == "__main__":
    main()
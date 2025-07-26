#!/usr/bin/env python3
"""Session Continuity for Claude Context Management.

This module provides functionality to maintain continuity between Claude sessions,
allowing seamless resumption of work with proper context restoration.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from session_summarizer import SessionSummarizer


class SessionContinuityManager:
    """Manages session continuity across Claude conversations."""

    def __init__(
        self,
        state_dir: Optional[Path] = None,
        session_timeout_hours: int = 24,
        max_context_restoration: int = 5,
    ):
        """Initialize SessionContinuityManager.

        Args:
            state_dir: Directory for storing session state
            session_timeout_hours: Hours before a session is considered stale
            max_context_restoration: Maximum previous sessions to consider
        """
        self.state_dir = state_dir or self._get_project_sessions_dir()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.max_context_restoration = max_context_restoration
        self.summarizer = SessionSummarizer(api_key=os.getenv("OPENAI_API_KEY", "test-key"), state_dir=self.state_dir)

        # Session metadata file
        self.metadata_file = self.state_dir / "session_metadata.json"
        self.metadata = self._load_metadata()

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

    def _load_metadata(self) -> Dict:
        """Load session metadata from disk."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return {"sessions": {}, "active_session": None}

    def _save_metadata(self):
        """Save session metadata to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session.

        Args:
            session_id: Optional custom session ID

        Returns:
            Session ID
        """
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.metadata["sessions"][session_id] = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "working_directory": os.getcwd(),
            "git_branch": self._get_git_branch(),
            "related_sessions": [],
        }
        self.metadata["active_session"] = session_id
        self._save_metadata()

        return session_id

    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_active_session(self) -> Optional[str]:
        """Get the currently active session ID."""
        active_id = self.metadata.get("active_session")
        if not active_id:
            return None

        # Check if session is still valid
        session_info = self.metadata["sessions"].get(active_id)
        if not session_info:
            return None

        last_updated = datetime.fromisoformat(session_info["last_updated"])
        if datetime.now() - last_updated > self.session_timeout:
            # Session is stale, mark as inactive
            session_info["status"] = "inactive"
            self.metadata["active_session"] = None
            self._save_metadata()
            return None

        return active_id

    def update_session(self, session_id: str, updates: Dict):
        """Update session information.

        Args:
            session_id: Session to update
            updates: Dictionary of updates
        """
        if session_id in self.metadata["sessions"]:
            self.metadata["sessions"][session_id].update(updates)
            self.metadata["sessions"][session_id]["last_updated"] = (
                datetime.now().isoformat()
            )
            self._save_metadata()

    def link_sessions(self, session_id: str, related_session_id: str):
        """Link two related sessions.

        Args:
            session_id: Primary session
            related_session_id: Related session to link
        """
        if session_id in self.metadata["sessions"]:
            related = self.metadata["sessions"][session_id].get(
                "related_sessions", []
            )
            if related_session_id not in related:
                related.append(related_session_id)
                self.metadata["sessions"][session_id]["related_sessions"] = related
                self._save_metadata()

    def find_related_sessions(
        self, criteria: Dict, limit: Optional[int] = None
    ) -> List[str]:
        """Find sessions matching criteria.

        Args:
            criteria: Search criteria (git_branch, working_directory, etc.)
            limit: Maximum results to return

        Returns:
            List of matching session IDs
        """
        matches = []
        for session_id, session_info in self.metadata["sessions"].items():
            if all(
                session_info.get(key) == value for key, value in criteria.items()
            ):
                matches.append(session_id)

        # Sort by last updated (most recent first)
        matches.sort(
            key=lambda x: self.metadata["sessions"][x]["last_updated"], reverse=True
        )

        if limit:
            matches = matches[:limit]

        return matches

    def restore_context(
        self, session_id: Optional[str] = None
    ) -> Tuple[str, Optional[Dict]]:
        """Restore context from a session or find the best match.

        Args:
            session_id: Specific session to restore, or None to auto-detect

        Returns:
            Tuple of (session_id, context_data)
        """
        # If no session specified, try to find the best match
        if not session_id:
            # First check for active session
            session_id = self.get_active_session()

            # If no active session, find recent related sessions
            if not session_id:
                criteria = {"git_branch": self._get_git_branch()}
                related = self.find_related_sessions(
                    criteria, limit=self.max_context_restoration
                )
                if related:
                    session_id = related[0]

        if not session_id:
            # No session to restore, create new one
            return self.create_session(), None

        # Load session state
        state = self.summarizer.load_session_state(session_id)
        if not state:
            return session_id, None

        # Prepare context for restoration
        context = {
            "session_id": session_id,
            "summary": state.get("summary", ""),
            "metadata": state.get("metadata", {}),
            "timestamp": state.get("timestamp", ""),
        }

        # Check for related sessions
        session_info = self.metadata["sessions"].get(session_id, {})
        related_sessions = session_info.get("related_sessions", [])

        if related_sessions:
            # Load summaries from related sessions
            related_summaries = []
            for related_id in related_sessions[-3:]:  # Last 3 related sessions
                related_state = self.summarizer.load_session_state(related_id)
                if related_state:
                    related_summaries.append(
                        {
                            "session_id": related_id,
                            "summary": related_state.get("summary", ""),
                            "timestamp": related_state.get("timestamp", ""),
                        }
                    )
            context["related_sessions"] = related_summaries

        return session_id, context

    def format_context_message(self, context: Dict) -> str:
        """Format context data into a system message.

        Args:
            context: Context data from restore_context

        Returns:
            Formatted message for conversation
        """
        parts = [
            f"[Resuming session {context['session_id']} from {context['timestamp']}]",
            f"Previous work summary: {context['summary']}",
        ]

        # Add key information
        metadata = context.get("metadata", {})
        if metadata.get("files_modified"):
            parts.append(
                f"Files previously modified: {', '.join(metadata['files_modified'][:5])}"
            )

        if metadata.get("todos"):
            parts.append(f"Outstanding TODOs: {', '.join(metadata['todos'][:3])}")

        # Add related session info if available
        if context.get("related_sessions"):
            parts.append("\nRelated sessions:")
            for related in context["related_sessions"][:2]:
                parts.append(f"- {related['session_id']}: {related['summary'][:100]}...")

        return "\n".join(parts)

    def save_conversation_checkpoint(
        self, session_id: str, conversation: List[Dict[str, str]], force: bool = False
    ):
        """Save a checkpoint of the current conversation.

        Args:
            session_id: Current session ID
            conversation: Current conversation
            force: Force checkpoint even if not at threshold
        """
        # Update session metadata
        self.update_session(session_id, {"message_count": len(conversation)})

        # Check if we should create a checkpoint
        should_checkpoint = force or len(conversation) % 50 == 0  # Every 50 messages

        if should_checkpoint:
            checkpoint_file = (
                self.state_dir / f"{session_id}_checkpoint_{len(conversation)}.json"
            )
            checkpoint_data = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "message_count": len(conversation),
                "conversation": conversation[-20:],  # Last 20 messages
            }
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a session.

        Args:
            session_id: Session to query

        Returns:
            Session information or None
        """
        return self.metadata["sessions"].get(session_id)

    def list_sessions(
        self, status: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """List sessions with optional filtering.

        Args:
            status: Filter by status (active/inactive)
            limit: Maximum results

        Returns:
            List of session information dictionaries
        """
        sessions = []
        for session_id, info in self.metadata["sessions"].items():
            if status is None or info.get("status") == status:
                sessions.append({"session_id": session_id, **info})

        # Sort by last updated
        sessions.sort(key=lambda x: x["last_updated"], reverse=True)

        return sessions[:limit]


def main():
    """Example usage and testing."""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = SessionContinuityManager()
        
        if command == "test":
            # Test mode
            # Create a session
            session_id = manager.create_session()
            print(f"Created session: {session_id}")

            # Update session
            manager.update_session(
                session_id, {"task": "Implementing session continuity"}
            )

            # Find related sessions
            related = manager.find_related_sessions(
                {"git_branch": manager._get_git_branch()}
            )
            print(f"Found {len(related)} related sessions")

            # Restore context
            restored_id, context = manager.restore_context()
            print(f"Restored session: {restored_id}")
            if context:
                print(f"Context: {manager.format_context_message(context)}")

            # List sessions
            sessions = manager.list_sessions(limit=5)
            print(f"\nRecent sessions:")
            for session in sessions:
                print(
                    f"  - {session['session_id']}: {session['status']} "
                    f"(updated {session['last_updated']})"
                )

            print("\n✅ Session continuity test completed")
            
        elif command == "list":
            # List sessions
            sessions = manager.list_sessions(limit=10)
            if sessions:
                print("Recent sessions:")
                for session in sessions:
                    print(
                        f"  - {session['session_id']}: {session['status']} "
                        f"(updated {session['last_updated']})"
                    )
            else:
                print("No sessions found")
                
        elif command == "continue":
            # Continue session
            session_id = sys.argv[2] if len(sys.argv) > 2 else None
            restored_id, context = manager.restore_context(session_id)
            print(f"Continuing session: {restored_id}")
            if context:
                print(manager.format_context_message(context))
            else:
                print("No previous context to restore")
                
        else:
            print(f"Unknown command: {command}")
            print("Usage: python session_continuity.py [test|list|continue [session_id]]")
    else:
        print("Session Continuity Manager")
        print("Usage: python session_continuity.py [test|list|continue [session_id]]")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Configurable Thresholds for Session Management.

This module provides a configuration system for managing various thresholds
used in session summarization and context management.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Optional, Any, List


@dataclass
class ThresholdConfig:
    """Configuration for session management thresholds."""

    # Token thresholds
    max_context_tokens: int = 90000
    summary_trigger_percent: float = 0.8
    critical_token_percent: float = 0.95
    min_tokens_for_summary: int = 10000

    # Message thresholds
    checkpoint_interval: int = 50
    min_messages_for_summary: int = 20
    max_messages_to_keep: int = 10

    # Time thresholds (in hours)
    session_timeout_hours: int = 24
    auto_summary_interval_hours: float = 2.0
    stale_session_hours: int = 72

    # Quality thresholds
    min_summary_quality_score: float = 0.7
    max_summary_retries: int = 3
    summary_model_temperature: float = 0.3

    # Performance thresholds
    max_summary_time_seconds: float = 30.0
    max_parallel_summaries: int = 3
    cache_ttl_hours: int = 48

    # File and size thresholds
    max_state_file_size_mb: float = 10.0
    max_checkpoint_files: int = 5
    max_related_sessions: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThresholdConfig":
        """Create from dictionary."""
        return cls(**data)

    def validate(self) -> List[str]:
        """Validate configuration values.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Token validations
        if self.max_context_tokens <= 0:
            errors.append("max_context_tokens must be positive")
        if not 0 < self.summary_trigger_percent <= 1:
            errors.append("summary_trigger_percent must be between 0 and 1")
        if not 0 < self.critical_token_percent <= 1:
            errors.append("critical_token_percent must be between 0 and 1")
        if self.summary_trigger_percent >= self.critical_token_percent:
            errors.append(
                "summary_trigger_percent must be less than critical_token_percent"
            )

        # Time validations
        if self.session_timeout_hours <= 0:
            errors.append("session_timeout_hours must be positive")
        if self.auto_summary_interval_hours <= 0:
            errors.append("auto_summary_interval_hours must be positive")

        # Quality validations
        if not 0 <= self.min_summary_quality_score <= 1:
            errors.append("min_summary_quality_score must be between 0 and 1")
        if not 0 <= self.summary_model_temperature <= 2:
            errors.append("summary_model_temperature must be between 0 and 2")

        return errors


class ThresholdManager:
    """Manages threshold configurations with persistence and environment overrides."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize ThresholdManager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self._get_project_config_path()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self._apply_env_overrides()

    def _get_project_config_path(self) -> Path:
        """Get the project-specific config path."""
        # Find project root by looking for .git
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current / ".claude" / "thresholds.json"
            current = current.parent
        
        # Fallback to current directory if no git root found
        return Path.cwd() / ".claude" / "thresholds.json"

    def _load_config(self) -> ThresholdConfig:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                    return ThresholdConfig.from_dict(data)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        # Return default config
        return ThresholdConfig()

    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        env_mappings = {
            "CLAUDE_MAX_CONTEXT_TOKENS": ("max_context_tokens", int),
            "CLAUDE_SUMMARY_TRIGGER_PERCENT": ("summary_trigger_percent", float),
            "CLAUDE_SESSION_TIMEOUT_HOURS": ("session_timeout_hours", int),
            "CLAUDE_CHECKPOINT_INTERVAL": ("checkpoint_interval", int),
            "CLAUDE_MIN_SUMMARY_QUALITY": ("min_summary_quality_score", float),
            "CLAUDE_SUMMARY_TEMPERATURE": ("summary_model_temperature", float),
        }

        for env_var, (attr_name, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                try:
                    setattr(self.config, attr_name, type_func(value))
                except ValueError:
                    print(f"Warning: Invalid value for {env_var}: {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a threshold value.

        Args:
            key: Threshold key
            default: Default value if not found

        Returns:
            Threshold value
        """
        return getattr(self.config, key, default)

    def set(self, key: str, value: Any):
        """Set a threshold value.

        Args:
            key: Threshold key
            value: New value
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self._save_config()
        else:
            raise KeyError(f"Unknown threshold: {key}")

    def update(self, updates: Dict[str, Any]):
        """Update multiple thresholds.

        Args:
            updates: Dictionary of updates
        """
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Ignoring unknown threshold: {key}")
        self._save_config()

    def reset(self, key: Optional[str] = None):
        """Reset thresholds to defaults.

        Args:
            key: Specific key to reset, or None for all
        """
        if key:
            default_config = ThresholdConfig()
            if hasattr(default_config, key):
                setattr(self.config, key, getattr(default_config, key))
                self._save_config()
        else:
            self.config = ThresholdConfig()
            self._save_config()

    def validate(self) -> bool:
        """Validate current configuration.

        Returns:
            True if valid, False otherwise
        """
        errors = self.config.validate()
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        return True

    def get_token_threshold(self) -> int:
        """Get the token threshold for triggering summarization."""
        return int(self.config.max_context_tokens * self.config.summary_trigger_percent)

    def get_critical_token_threshold(self) -> int:
        """Get the critical token threshold."""
        return int(self.config.max_context_tokens * self.config.critical_token_percent)

    def should_checkpoint(self, message_count: int) -> bool:
        """Determine if a checkpoint should be created.

        Args:
            message_count: Current message count

        Returns:
            True if checkpoint should be created
        """
        return message_count % self.config.checkpoint_interval == 0

    def is_session_stale(self, hours_since_update: float) -> bool:
        """Determine if a session is stale.

        Args:
            hours_since_update: Hours since last update

        Returns:
            True if session is stale
        """
        return hours_since_update > self.config.stale_session_hours

    def print_config(self):
        """Print current configuration."""
        print("Current Threshold Configuration:")
        print("=" * 40)
        for key, value in self.config.to_dict().items():
            print(f"{key:30s}: {value}")


class AdaptiveThresholdManager(ThresholdManager):
    """Advanced threshold manager with adaptive capabilities."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize AdaptiveThresholdManager."""
        super().__init__(config_path)
        self.metrics_file = self.config_path.parent / "threshold_metrics.json"
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load performance metrics."""
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                return json.load(f)
        return {
            "summary_times": [],
            "token_counts": [],
            "quality_scores": [],
            "checkpoint_sizes": [],
        }

    def _save_metrics(self):
        """Save performance metrics."""
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def record_summary_performance(
        self, time_seconds: float, token_count: int, quality_score: float
    ):
        """Record summary generation performance.

        Args:
            time_seconds: Time taken to generate summary
            token_count: Token count of conversation
            quality_score: Quality score of summary
        """
        self.metrics["summary_times"].append(time_seconds)
        self.metrics["token_counts"].append(token_count)
        self.metrics["quality_scores"].append(quality_score)

        # Keep only recent metrics (last 100)
        for key in ["summary_times", "token_counts", "quality_scores"]:
            self.metrics[key] = self.metrics[key][-100:]

        self._save_metrics()
        self._adapt_thresholds()

    def _adapt_thresholds(self):
        """Adapt thresholds based on performance metrics."""
        if len(self.metrics["summary_times"]) < 10:
            return  # Not enough data

        # Adapt summary trigger based on performance
        avg_time = sum(self.metrics["summary_times"][-10:]) / 10
        if avg_time > self.config.max_summary_time_seconds:
            # Summaries taking too long, trigger earlier
            new_trigger = max(0.5, self.config.summary_trigger_percent - 0.05)
            self.config.summary_trigger_percent = new_trigger

        # Adapt quality threshold based on scores
        if self.metrics["quality_scores"]:
            avg_quality = sum(self.metrics["quality_scores"][-10:]) / min(
                10, len(self.metrics["quality_scores"])
            )
            if avg_quality < self.config.min_summary_quality_score:
                # Quality too low, adjust temperature
                self.config.summary_model_temperature = min(
                    1.0, self.config.summary_model_temperature + 0.1
                )

        self._save_config()


def main():
    """Example usage and testing."""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = ThresholdManager()
        
        if command == "test":
            print("Testing Threshold Configuration System\n")

            # Test basic configuration
            print("Default configuration:")
            manager.print_config()

            # Test updates
            print("\nUpdating thresholds...")
            manager.update(
                {
                    "max_context_tokens": 100000,
                    "summary_trigger_percent": 0.75,
                    "checkpoint_interval": 25,
                }
            )

            # Test getters
            print(f"\nToken threshold: {manager.get_token_threshold()}")
            print(f"Critical threshold: {manager.get_critical_token_threshold()}")
            print(f"Should checkpoint at 50 messages: {manager.should_checkpoint(50)}")

            # Test validation
            print(f"\nConfiguration valid: {manager.validate()}")

            # Test adaptive manager
            print("\nTesting Adaptive Threshold Manager...")
            adaptive = AdaptiveThresholdManager()
            
            # Simulate some performance data
            for i in range(5):
                adaptive.record_summary_performance(
                    time_seconds=20.0 + i * 2,
                    token_count=50000 + i * 10000,
                    quality_score=0.8 - i * 0.05,
                )

            print("\n✅ Threshold configuration test completed")
            
        elif command == "config":
            # Show current configuration
            manager.print_config()
            
        elif command == "set" and len(sys.argv) >= 4:
            # Set a threshold value
            key = sys.argv[2]
            value = sys.argv[3]
            
            # Try to parse value as number
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # Keep as string
                
            try:
                manager.set(key, value)
                print(f"✅ Set {key} = {value}")
                manager.print_config()
            except KeyError as e:
                print(f"❌ Error: {e}")
                
        else:
            print(f"Unknown command: {command}")
            print("Usage: python threshold_config.py [test|config|set <key> <value>]")
    else:
        print("Threshold Configuration Module")
        print("Usage: python threshold_config.py [test|config|set <key> <value>]")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Documentation synthesis script for AI workflows."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import anthropic
    import yaml
except ImportError:
    print("Error: Required packages not installed")
    print("Run: pip install anthropic pyyaml")
    sys.exit(1)


class DocSynthesizer:
    """Synthesize documentation based on code changes."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load workflow configuration."""
        config_path = Path(".new-project/workflows/config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {"doc_synthesis": {"max_tokens": 2000}}

    def analyze_changes(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize changed files."""
        categories = {"code": [], "config": [], "docs": [], "tests": []}

        for file in files:
            path = Path(file)
            if path.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                if "test" in file.lower():
                    categories["tests"].append(file)
                else:
                    categories["code"].append(file)
            elif path.suffix in [".yaml", ".yml", ".json"]:
                categories["config"].append(file)
            elif path.suffix == ".md":
                categories["docs"].append(file)

        return categories

    def generate_doc_updates(self, changes: Dict[str, List[str]]) -> str:
        """Generate documentation updates using Claude."""
        if not any(changes.values()):
            return ""

        prompt = self.build_prompt(changes)

        try:
            response = self.client.messages.create(
                model=self.config.get("doc_synthesis", {}).get(
                    "model", "claude-3-5-sonnet-20241022"
                ),
                max_tokens=self.config.get("doc_synthesis", {}).get("max_tokens", 2000),
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text
        except Exception as e:
            print(f"Error generating docs: {e}")
            return ""

    def build_prompt(self, changes: Dict[str, List[str]]) -> str:
        """Build prompt for documentation synthesis."""
        prompt = "Based on these file changes, suggest documentation updates:\n\n"

        if changes["code"]:
            prompt += f"Code files modified: {', '.join(changes['code'][:10])}\n"
        if changes["config"]:
            prompt += f"Config files modified: {', '.join(changes['config'][:5])}\n"
        if changes["tests"]:
            prompt += f"Test files modified: {', '.join(changes['tests'][:5])}\n"

        prompt += """
Please provide:
1. Summary of what changed
2. Any README.md updates needed
3. Any API documentation updates
4. Migration notes if applicable

Format as markdown sections that can be directly added to documentation.
Focus on user-facing changes and important technical details.
"""

        return prompt

    def update_changelog(self, summary: str):
        """Update CHANGELOG.md with changes."""
        changelog_path = Path("CHANGELOG.md")

        if not changelog_path.exists():
            # Create initial changelog
            content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

{summary}
"""
            changelog_path.write_text(content)
        else:
            # Insert after Unreleased section
            content = changelog_path.read_text()
            if "## [Unreleased]" in content:
                parts = content.split("## [Unreleased]", 1)
                if len(parts) == 2:
                    # Find next section
                    next_section_idx = parts[1].find("\n## [")
                    if next_section_idx > -1:
                        existing = parts[1][:next_section_idx].strip()
                        rest = parts[1][next_section_idx:]
                        new_content = f"{parts[0]}## [Unreleased]\n\n{existing}\n\n{summary}\n{rest}"
                    else:
                        new_content = f"{parts[0]}## [Unreleased]\n\n{parts[1].strip()}\n\n{summary}"

                    changelog_path.write_text(new_content)

    def run(self, files: List[str], mode: str = "auto"):
        """Run documentation synthesis."""
        print("Analyzing changes...")
        changes = self.analyze_changes(files)

        print("Generating documentation updates...")
        updates = self.generate_doc_updates(changes)

        if not updates:
            print("No documentation updates needed")
            return

        if mode == "auto":
            # Auto mode - update changelog
            print("Updating CHANGELOG.md...")
            self.update_changelog(updates)

            # Save full update for review
            updates_path = Path(".new-project/doc-updates.md")
            updates_path.parent.mkdir(parents=True, exist_ok=True)
            updates_path.write_text(
                f"# Documentation Updates - {datetime.now()}\n\n{updates}"
            )

            print(f"Documentation updates saved to {updates_path}")
        else:
            # Manual mode - just print
            print("\n" + "=" * 60)
            print("Suggested Documentation Updates:")
            print("=" * 60 + "\n")
            print(updates)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synthesize documentation from code changes"
    )
    parser.add_argument(
        "--files", required=True, help="Space-separated list of changed files"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "manual"],
        default="manual",
        help="Auto mode updates files, manual mode prints suggestions",
    )

    args = parser.parse_args()

    # Parse files
    files = args.files.strip().split()

    synthesizer = DocSynthesizer()
    synthesizer.run(files, args.mode)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Summary Quality Validation for Claude Context Management.

This module provides functionality to validate and score the quality of generated
summaries to ensure they maintain essential context and information.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import openai


@dataclass
class QualityMetrics:
    """Metrics for summary quality assessment."""

    completeness_score: float  # 0-1, coverage of key information
    coherence_score: float  # 0-1, logical flow and structure
    relevance_score: float  # 0-1, focus on important content
    conciseness_score: float  # 0-1, brevity without loss of meaning
    accuracy_score: float  # 0-1, factual correctness
    overall_score: float  # 0-1, weighted average

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "completeness": self.completeness_score,
            "coherence": self.coherence_score,
            "relevance": self.relevance_score,
            "conciseness": self.conciseness_score,
            "accuracy": self.accuracy_score,
            "overall": self.overall_score,
        }


class SummaryQualityValidator:
    """Validates and scores summary quality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        min_quality_threshold: float = 0.7,
        weights: Optional[Dict[str, float]] = None,
    ):
        """Initialize the validator.

        Args:
            api_key: OpenAI API key for advanced validation
            min_quality_threshold: Minimum acceptable quality score
            weights: Custom weights for score calculation
        """
        self.api_key = api_key
        self.min_quality_threshold = min_quality_threshold
        self.weights = weights or {
            "completeness": 0.3,
            "coherence": 0.2,
            "relevance": 0.2,
            "conciseness": 0.15,
            "accuracy": 0.15,
        }

        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None

    def validate_summary(
        self,
        summary: str,
        original_conversation: List[Dict[str, str]],
        key_information: Dict,
    ) -> Tuple[QualityMetrics, List[str]]:
        """Validate summary quality.

        Args:
            summary: Generated summary text
            original_conversation: Original conversation
            key_information: Extracted key information

        Returns:
            Tuple of (quality_metrics, issues_found)
        """
        issues = []

        # Calculate individual scores
        completeness = self._assess_completeness(summary, key_information)
        coherence = self._assess_coherence(summary)
        relevance = self._assess_relevance(summary, original_conversation)
        conciseness = self._assess_conciseness(summary, original_conversation)
        accuracy = self._assess_accuracy(summary, key_information)

        # Calculate overall score
        overall = (
            self.weights["completeness"] * completeness
            + self.weights["coherence"] * coherence
            + self.weights["relevance"] * relevance
            + self.weights["conciseness"] * conciseness
            + self.weights["accuracy"] * accuracy
        )

        metrics = QualityMetrics(
            completeness_score=completeness,
            coherence_score=coherence,
            relevance_score=relevance,
            conciseness_score=conciseness,
            accuracy_score=accuracy,
            overall_score=overall,
        )

        # Check for specific issues
        if completeness < 0.6:
            issues.append("Summary missing key information")
        if coherence < 0.5:
            issues.append("Summary lacks logical structure")
        if relevance < 0.6:
            issues.append("Summary contains irrelevant information")
        if conciseness < 0.5:
            issues.append("Summary is too verbose")
        if accuracy < 0.7:
            issues.append("Summary contains potential inaccuracies")

        return metrics, issues

    def _assess_completeness(self, summary: str, key_info: Dict) -> float:
        """Assess if summary covers key information.

        Args:
            summary: Summary text
            key_info: Key information dictionary

        Returns:
            Completeness score (0-1)
        """
        score = 0.0
        total_items = 0

        # Check files mentioned
        if key_info.get("files_modified"):
            files_in_summary = sum(
                1 for f in key_info["files_modified"] if f in summary
            )
            score += files_in_summary / len(key_info["files_modified"])
            total_items += 1

        # Check commands mentioned
        if key_info.get("commands_run"):
            # Look for command indicators
            command_keywords = ["ran", "executed", "command", "script", "bash"]
            has_command_mention = any(keyword in summary.lower() for keyword in command_keywords)
            score += 1.0 if has_command_mention else 0.0
            total_items += 1

        # Check TODOs mentioned
        if key_info.get("todos"):
            todo_keywords = ["todo", "pending", "remaining", "next", "unfinished"]
            has_todo_mention = any(keyword in summary.lower() for keyword in todo_keywords)
            score += 1.0 if has_todo_mention else 0.0
            total_items += 1

        # Check errors mentioned
        if key_info.get("errors_encountered"):
            error_keywords = ["error", "issue", "problem", "failed", "exception"]
            has_error_mention = any(keyword in summary.lower() for keyword in error_keywords)
            score += 1.0 if has_error_mention else 0.0
            total_items += 1

        return score / total_items if total_items > 0 else 0.8

    def _assess_coherence(self, summary: str) -> float:
        """Assess logical flow and structure.

        Args:
            summary: Summary text

        Returns:
            Coherence score (0-1)
        """
        # Basic coherence checks
        sentences = re.split(r'[.!?]+', summary)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5  # Too short to assess

        score = 1.0

        # Check for very short sentences (might indicate fragmentation)
        short_sentences = sum(1 for s in sentences if len(s.split()) < 3)
        if short_sentences > len(sentences) / 2:
            score -= 0.2

        # Check for very long sentences (might indicate run-ons)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        if long_sentences > len(sentences) / 3:
            score -= 0.2

        # Check for transitional phrases
        transitions = [
            "however", "therefore", "additionally", "furthermore",
            "first", "second", "finally", "next", "then"
        ]
        has_transitions = any(t in summary.lower() for t in transitions)
        if has_transitions:
            score += 0.1

        # Check for logical structure indicators
        structure_indicators = [
            "objective", "accomplished", "implemented", "created",
            "modified", "issue", "next step", "result"
        ]
        structure_count = sum(1 for ind in structure_indicators if ind in summary.lower())
        if structure_count >= 3:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _assess_relevance(
        self, summary: str, conversation: List[Dict[str, str]]
    ) -> float:
        """Assess relevance to original conversation.

        Args:
            summary: Summary text
            conversation: Original conversation

        Returns:
            Relevance score (0-1)
        """
        # Extract main topics from conversation
        all_content = " ".join(msg.get("content", "") for msg in conversation)
        
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b\w+\b', all_content.lower())
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        top_words = [word for word, _ in top_keywords]

        # Check how many top keywords appear in summary
        summary_lower = summary.lower()
        keyword_matches = sum(1 for word in top_words if word in summary_lower)

        return min(1.0, keyword_matches / 10)  # Expect at least 10 keyword matches

    def _assess_conciseness(
        self, summary: str, conversation: List[Dict[str, str]]
    ) -> float:
        """Assess appropriate brevity.

        Args:
            summary: Summary text
            conversation: Original conversation

        Returns:
            Conciseness score (0-1)
        """
        conversation_length = sum(
            len(msg.get("content", "")) for msg in conversation
        )
        summary_length = len(summary)

        # Ideal compression ratio between 5:1 and 20:1
        if conversation_length == 0:
            return 0.5

        ratio = conversation_length / summary_length

        if 5 <= ratio <= 20:
            return 1.0
        elif ratio < 5:
            # Too verbose
            return max(0.3, ratio / 5)
        else:
            # Too brief
            return max(0.3, 20 / ratio)

    def _assess_accuracy(self, summary: str, key_info: Dict) -> float:
        """Assess factual accuracy.

        Args:
            summary: Summary text
            key_info: Key information dictionary

        Returns:
            Accuracy score (0-1)
        """
        score = 1.0

        # Check for number consistency
        numbers_in_summary = re.findall(r'\b\d+\b', summary)
        
        # Verify file counts if mentioned
        if "files" in summary.lower() and key_info.get("files_modified"):
            actual_count = len(key_info["files_modified"])
            for num in numbers_in_summary:
                if abs(int(num) - actual_count) <= 1:  # Allow off-by-one
                    break
            else:
                if numbers_in_summary and "file" in summary.lower():
                    score -= 0.2

        # Check for contradiction indicators
        contradiction_phrases = [
            "not", "didn't", "failed", "couldn't", "unable"
        ]
        negative_count = sum(1 for phrase in contradiction_phrases if phrase in summary.lower())
        
        # If there are many negatives but no errors reported, might be inaccurate
        if negative_count > 2 and not key_info.get("errors_encountered"):
            score -= 0.1

        return max(0.0, score)

    def improve_summary(
        self, summary: str, metrics: QualityMetrics, issues: List[str]
    ) -> Optional[str]:
        """Attempt to improve a low-quality summary.

        Args:
            summary: Original summary
            metrics: Quality metrics
            issues: Identified issues

        Returns:
            Improved summary or None if cannot improve
        """
        if not self.client:
            return None

        if metrics.overall_score >= self.min_quality_threshold:
            return summary  # Already good enough

        # Create improvement prompt
        prompt_parts = [
            "Please improve this summary by addressing the following issues:",
        ]
        for issue in issues:
            prompt_parts.append(f"- {issue}")

        prompt_parts.extend([
            "",
            f"Original summary: {summary}",
            "",
            "Provide an improved summary that:",
            "1. Maintains all factual information",
            "2. Improves clarity and structure",
            "3. Ensures completeness of key details",
            "4. Remains concise (under 500 words)",
        ])

        prompt = "\n".join(prompt_parts)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return None

    def batch_validate(
        self, summaries: List[Tuple[str, List[Dict], Dict]]
    ) -> List[Tuple[QualityMetrics, List[str]]]:
        """Validate multiple summaries.

        Args:
            summaries: List of (summary, conversation, key_info) tuples

        Returns:
            List of (metrics, issues) tuples
        """
        results = []
        for summary, conversation, key_info in summaries:
            metrics, issues = self.validate_summary(summary, conversation, key_info)
            results.append((metrics, issues))
        return results


def main():
    """Example usage and testing."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Summary Quality Validator\n")

        # Create validator
        validator = SummaryQualityValidator()

        # Test data
        test_conversation = [
            {"role": "user", "content": "Help me create a React component"},
            {"role": "assistant", "content": "I'll create a component in /src/components/Button.tsx"},
            {"role": "user", "content": "Add props for color and size"},
            {"role": "assistant", "content": "I've added the props. The component now accepts color and size."},
        ]

        test_key_info = {
            "files_modified": ["/src/components/Button.tsx"],
            "commands_run": ["npm install"],
            "todos": ["Add tests for Button component"],
            "errors_encountered": [],
        }

        # Test summaries of varying quality
        test_summaries = [
            "Created a React Button component in /src/components/Button.tsx with color and size props. TODO: Add tests.",
            "Made a component.",
            "The assistant helped create a React component located in the src/components/Button.tsx file. The component was enhanced with properties for color and size customization. A todo item was noted to add tests for the component later.",
        ]

        print("Validating test summaries:\n")
        for i, summary in enumerate(test_summaries, 1):
            print(f"Summary {i}: {summary[:50]}...")
            metrics, issues = validator.validate_summary(
                summary, test_conversation, test_key_info
            )
            print(f"  Overall score: {metrics.overall_score:.2f}")
            print(f"  Metrics: {metrics.to_dict()}")
            if issues:
                print(f"  Issues: {', '.join(issues)}")
            print()

        # Test improvement
        print("Testing summary improvement...")
        bad_summary = test_summaries[1]
        metrics, issues = validator.validate_summary(
            bad_summary, test_conversation, test_key_info
        )
        print(f"Original: {bad_summary}")
        print(f"Score: {metrics.overall_score:.2f}")
        
        improved = validator.improve_summary(bad_summary, metrics, issues)
        if improved and improved != bad_summary:
            print(f"Improved: {improved}")
        else:
            print("Could not improve (API key required)")

        print("\n✅ Summary quality validation test completed")
    else:
        print("Summary Quality Validator Module")
        print("Usage: python summary_validator.py test")


if __name__ == "__main__":
    main()
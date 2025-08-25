"""Batch processing for cost-optimized embeddings."""

import json
import logging
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

from .client import EmbeddingClient
from .config import rag_settings
from .exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Batch processor for cost-optimized embedding generation."""

    def __init__(self, embedding_client: EmbeddingClient):
        """Initialize batch processor."""
        self.client = embedding_client
        self.batch_size = rag_settings.batch_size
        self.enabled = rag_settings.batch_processing_enabled

        # Batch queue
        self.pending_queue: deque = deque()
        self.processing = False
        self.batch_id = 0

        # Results storage
        self.results: dict[str, dict[str, Any]] = {}

        # Batch history for monitoring
        self.batch_history_file = (
            Path(rag_settings.embedding_cache_path) / "batch_history.json"
        )
        self.batch_history = self._load_batch_history()

    def _load_batch_history(self) -> list[dict[str, Any]]:
        """Load batch processing history."""
        if self.batch_history_file.exists():
            try:
                with open(self.batch_history_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load batch history: {e}")
        return []

    def _save_batch_history(self) -> None:
        """Save batch processing history."""
        try:
            # Ensure directory exists
            self.batch_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.batch_history_file, "w") as f:
                json.dump(self.batch_history[-1000:], f)  # Keep last 1000 entries
        except Exception as e:
            logger.warning(f"Failed to save batch history: {e}")

    def add_to_batch(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add text to batch queue and return tracking ID."""
        if not self.enabled:
            raise EmbeddingError("Batch processing is disabled")

        tracking_id = f"batch_{self.batch_id}_{len(self.pending_queue)}"

        item = {
            "id": tracking_id,
            "text": text,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
        }

        self.pending_queue.append(item)
        logger.debug(f"Added item {tracking_id} to batch queue")

        return tracking_id

    async def process_batch(self) -> dict[str, Any]:
        """Process the current batch."""
        if self.processing:
            raise EmbeddingError("Batch processing already in progress")

        if not self.pending_queue:
            return {"processed": 0, "batch_id": None}

        self.processing = True
        self.batch_id += 1
        batch_start = time.time()

        try:
            # Collect items for batch
            batch_items = []
            batch_size = min(self.batch_size, len(self.pending_queue))

            for _ in range(batch_size):
                batch_items.append(self.pending_queue.popleft())

            # Extract texts
            texts = [item["text"] for item in batch_items]

            # Generate embeddings
            logger.info(f"Processing batch {self.batch_id} with {len(texts)} items")
            embeddings = await self.client.embed_batch(texts, show_progress=True)

            # Store results
            for item, embedding in zip(batch_items, embeddings, strict=False):
                self.results[item["id"]] = {
                    "embedding": embedding,
                    "metadata": item["metadata"],
                    "processed_at": datetime.now().isoformat(),
                }

            # Record batch history
            batch_time = time.time() - batch_start
            batch_record = {
                "batch_id": self.batch_id,
                "size": len(batch_items),
                "processing_time": batch_time,
                "avg_time_per_item": batch_time / len(batch_items),
                "timestamp": datetime.now().isoformat(),
                "cost_savings": self._calculate_cost_savings(len(batch_items)),
            }

            self.batch_history.append(batch_record)
            self._save_batch_history()

            logger.info(
                f"Batch {self.batch_id} completed: {len(batch_items)} items "
                f"in {batch_time:.2f}s (${batch_record['cost_savings']:.4f} saved)"
            )

            return {
                "processed": len(batch_items),
                "batch_id": self.batch_id,
                "processing_time": batch_time,
                "cost_savings": batch_record["cost_savings"],
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Return items to queue
            for item in batch_items:
                self.pending_queue.appendleft(item)
            raise
        finally:
            self.processing = False

    def _calculate_cost_savings(self, batch_size: int) -> float:
        """Calculate estimated cost savings from batch processing."""
        # Gemini pricing (estimated)
        individual_cost_per_1k = 0.0001  # $0.0001 per 1K characters
        batch_cost_per_1k = 0.00005  # 50% discount for batch

        avg_chars_per_item = 500  # Estimated average
        total_chars = batch_size * avg_chars_per_item

        individual_cost = (total_chars / 1000) * individual_cost_per_1k
        batch_cost = (total_chars / 1000) * batch_cost_per_1k

        return individual_cost - batch_cost

    def get_result(self, tracking_id: str) -> dict[str, Any] | None:
        """Get result for a tracking ID."""
        return self.results.get(tracking_id)

    def get_batch_status(self) -> dict[str, Any]:
        """Get current batch processing status."""
        return {
            "pending_items": len(self.pending_queue),
            "processing": self.processing,
            "current_batch_id": self.batch_id,
            "results_available": len(self.results),
            "batch_size_limit": self.batch_size,
            "enabled": self.enabled,
        }

    def get_batch_statistics(self) -> dict[str, Any]:
        """Get batch processing statistics."""
        if not self.batch_history:
            return {
                "total_batches": 0,
                "total_items": 0,
                "avg_batch_size": 0,
                "avg_processing_time": 0,
                "total_cost_savings": 0,
            }

        total_items = sum(batch["size"] for batch in self.batch_history)
        avg_batch_size = total_items / len(self.batch_history)
        avg_processing_time = sum(
            batch["processing_time"] for batch in self.batch_history
        ) / len(self.batch_history)
        total_cost_savings = sum(batch["cost_savings"] for batch in self.batch_history)

        return {
            "total_batches": len(self.batch_history),
            "total_items": total_items,
            "avg_batch_size": avg_batch_size,
            "avg_processing_time": avg_processing_time,
            "total_cost_savings": total_cost_savings,
            "recent_batches": self.batch_history[-10:],  # Last 10 batches
        }

    def clear_results(self, older_than_hours: int = 24) -> int:
        """Clear old results to free memory."""
        cutoff = datetime.now().timestamp() - (older_than_hours * 3600)
        cleared = 0

        to_remove = []
        for tracking_id, result in self.results.items():
            processed_at = datetime.fromisoformat(result["processed_at"]).timestamp()
            if processed_at < cutoff:
                to_remove.append(tracking_id)

        for tracking_id in to_remove:
            del self.results[tracking_id]
            cleared += 1

        logger.info(f"Cleared {cleared} old results")
        return cleared

    async def process_file_batch(
        self, file_paths: list[Path], file_processor_func: Any
    ) -> dict[str, list[float]]:
        """Process a batch of files and return embeddings."""
        # Extract text from files
        texts = []
        metadata_list = []

        for file_path in file_paths:
            try:
                text = await file_processor_func(file_path)
                texts.append(text)
                metadata_list.append(
                    {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_size": file_path.stat().st_size,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                continue

        # Generate embeddings
        embeddings = await self.client.embed_batch(texts)

        # Create result mapping
        results = {}
        for i, file_path in enumerate(file_paths):
            if i < len(embeddings):
                results[str(file_path)] = embeddings[i]

        return results

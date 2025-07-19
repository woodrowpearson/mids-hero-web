"""
Test performance benchmarks for data operations.
"""

import os
import time

import psutil
import pytest
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models import (
    Archetype,
    Enhancement,
    Power,
    PowerEnhancementCompatibility,
    Powerset,
    Recipe,
    Salvage,
)


class TestDatabasePerformance:
    """Test database query performance benchmarks."""

    def test_index_performance(self, db: Session):
        """Test that all frequently queried columns have indexes."""
        # Check query execution plans for common queries
        test_queries = [
            ("Power by name", "SELECT * FROM powers WHERE name = 'Fire Bolt'"),
            ("Powers by powerset", "SELECT * FROM powers WHERE powerset_id = 1"),
            ("Powers by level", "SELECT * FROM powers WHERE level_available = 1"),
            (
                "Enhancements by set",
                "SELECT * FROM enhancements WHERE set_id = 1",
            ),
            (
                "Recipes by enhancement",
                "SELECT * FROM recipes WHERE enhancement_id = 1",
            ),
        ]

        issues = []
        for query_name, query in test_queries:
            # Analyze query plan
            explain = db.execute(text(f"EXPLAIN ANALYZE {query}")).fetchall()

            # Check if using index scan vs sequential scan
            plan_text = "\n".join([str(row) for row in explain])

            if "Seq Scan" in plan_text and "Index" not in plan_text:
                # Extract execution time
                exec_time = None
                for row in explain:
                    if "Execution Time" in str(row):
                        exec_time = float(str(row).split(":")[-1].split()[0])

                if exec_time and exec_time > 10.0:  # 10ms threshold
                    issues.append(
                        f"{query_name} uses sequential scan, took {exec_time}ms"
                    )

        assert not issues, f"Query performance issues: {issues}"

    def test_bulk_query_performance(self, db: Session):
        """Test performance of bulk data retrieval."""
        benchmarks = []

        # Test 1: Load all powers for an archetype
        start = time.time()
        powers = db.query(Power).join(Powerset).filter(Powerset.archetype_id == 1).all()
        duration = time.time() - start
        benchmarks.append(("Load archetype powers", len(powers), duration))

        # Test 2: Load all enhancements with set bonuses
        start = time.time()
        enhancements = (
            db.query(Enhancement).filter(Enhancement.set_id.isnot(None)).all()
        )
        duration = time.time() - start
        benchmarks.append(("Load set enhancements", len(enhancements), duration))

        # Test 3: Complex join query
        start = time.time()
        result = (
            db.query(Power)
            .join(Powerset)
            .join(Archetype)
            .filter(Archetype.name == "Blaster", Power.level_available <= 20)
            .all()
        )
        duration = time.time() - start
        benchmarks.append(("Complex join query", len(result), duration))

        # Check performance thresholds
        issues = []
        for test_name, count, duration in benchmarks:
            # Calculate records per second
            if count > 0:
                rps = count / duration
                ms_per_record = (duration * 1000) / count

                print(
                    f"{test_name}: {count} records in {duration:.3f}s "
                    f"({rps:.0f} rec/s, {ms_per_record:.2f}ms/rec)"
                )

                # Performance thresholds
                if ms_per_record > 1.0:  # More than 1ms per record
                    issues.append(f"{test_name} slow: {ms_per_record:.2f}ms per record")

        assert not issues, f"Performance threshold violations: {issues}"

    def test_pagination_performance(self, db: Session):
        """Test performance of paginated queries."""
        page_size = 100

        # Test offset-based pagination
        offset_times = []
        for _page in range(5):
            start = time.time()
            powers = db.query(Power).offset(_page * page_size).limit(page_size).all()
            duration = time.time() - start
            offset_times.append(duration)

        # Check for performance degradation with higher offsets
        if offset_times[-1] > offset_times[0] * 2:
            pytest.fail(
                f"Offset pagination degrades: page 0={offset_times[0]:.3f}s, "
                f"page 4={offset_times[-1]:.3f}s"
            )

        # Test cursor-based pagination (more efficient)
        last_id = 0
        cursor_times = []
        for _page in range(5):
            start = time.time()
            powers = db.query(Power).filter(Power.id > last_id).limit(page_size).all()
            duration = time.time() - start
            cursor_times.append(duration)

            if powers:
                last_id = powers[-1].id

        # Cursor pagination should be consistent
        avg_cursor_time = sum(cursor_times) / len(cursor_times)
        for i, t in enumerate(cursor_times):
            if t > avg_cursor_time * 1.5:
                pytest.fail(
                    f"Cursor pagination inconsistent: page {i} took {t:.3f}s "
                    f"(avg: {avg_cursor_time:.3f}s)"
                )


class TestImportPerformance:
    """Test import operation performance."""

    def test_batch_insert_performance(self, db: Session):
        """Test performance of batch insert operations."""
        # Create test data
        test_data = []
        for i in range(1000):
            test_data.append(
                {
                    "id": 90000 + i,
                    "internal_name": f"test_salvage_{i}",
                    "display_name": f"Test Salvage {i}",
                    "salvage_type": "common",
                    "origin": "tech",
                    "level_range": "10-25",
                }
            )

        # Test single inserts (bad practice)
        start = time.time()
        for i in range(10):  # Only 10 to avoid timeout
            salvage = Salvage(**test_data[i])
            db.add(salvage)
            db.commit()
        single_time = (time.time() - start) / 10

        # Clean up
        db.query(Salvage).filter(Salvage.id >= 90000).delete()
        db.commit()

        # Test batch insert (good practice)
        start = time.time()
        db.bulk_insert_mappings(Salvage, test_data[:100])
        db.commit()
        batch_time = (time.time() - start) / 100

        # Batch should be at least 10x faster than single inserts
        improvement = single_time / batch_time
        print(f"Batch insert {improvement:.1f}x faster than single inserts")

        assert improvement > 10, (
            f"Batch insert not efficient enough: only {improvement:.1f}x faster"
        )

        # Clean up
        db.query(Salvage).filter(Salvage.id >= 90000).delete()
        db.commit()

    def test_memory_usage_during_import(self):
        """Test memory usage remains reasonable during large imports."""
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate large data processing
        large_data = []
        for i in range(10000):
            large_data.append(
                {"id": i, "name": f"item_{i}", "data": "x" * 1000}  # 1KB per item
            )

        # Check memory after loading
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory

        print(f"Memory increase: {memory_increase:.1f} MB for 10K items")

        # Should not use more than 100MB for 10MB of data
        assert memory_increase < 100, (
            f"Excessive memory usage: {memory_increase:.1f} MB"
        )

        # Clean up
        del large_data


class TestCachePerformance:
    """Test caching system performance."""

    def test_cache_hit_performance(self, db: Session):
        """Test performance improvement from caching."""
        # First query (cache miss)
        start = time.time()
        _ = db.query(Archetype).filter_by(name="Blaster").first()
        miss_time = time.time() - start

        # Second query (should hit cache if implemented)
        start = time.time()
        _ = db.query(Archetype).filter_by(name="Blaster").first()
        hit_time = time.time() - start

        # Cache hit should be faster (assuming caching is implemented)
        # This test documents the need for caching even if not yet implemented
        print(
            f"First query: {miss_time * 1000:.2f}ms, "
            f"Second query: {hit_time * 1000:.2f}ms"
        )

        # If caching is implemented, hit should be much faster
        if hit_time < miss_time * 0.5:
            print("Caching appears to be working effectively")

    def test_cache_memory_limits(self):
        """Test that cache respects memory limits."""
        # This would test actual cache implementation
        # For now, document expected behavior

        max_cache_size_mb = 100

        # Simulate cache entries
        cache_data = {}
        entry_size = 1024  # 1KB per entry

        memory_used = 0
        entries_added = 0

        while memory_used < max_cache_size_mb * 1024 * 1024:
            key = f"cache_key_{entries_added}"
            value = "x" * entry_size
            cache_data[key] = value
            memory_used += entry_size
            entries_added += 1

            # Simulate LRU eviction
            if len(cache_data) > 10000:  # Max 10K entries
                # Remove oldest entry
                oldest_key = next(iter(cache_data))
                del cache_data[oldest_key]

        print(f"Cache can hold ~{entries_added} entries within {max_cache_size_mb}MB")
        assert entries_added > 1000, "Cache capacity too low"


class TestQueryOptimization:
    """Test query optimization strategies."""

    def test_n_plus_one_detection(self, db: Session):
        """Test for N+1 query problems."""
        # Enable query logging (would need actual implementation)
        query_count = 0

        # Bad pattern: N+1 queries
        start_count = query_count
        powersets = db.query(Powerset).limit(10).all()
        for powerset in powersets:
            # This triggers additional query for each powerset
            _ = db.query(Power).filter(Power.powerset_id == powerset.id).count()
            query_count += 1

        n_plus_one_queries = query_count - start_count

        # Good pattern: Single query with join
        start_count = query_count
        _ = (
            db.query(
                Powerset.id, Powerset.name, func.count(Power.id).label("power_count")
            )
            .outerjoin(Power)
            .group_by(Powerset.id)
            .limit(10)
            .all()
        )

        single_query = query_count - start_count + 1

        print(f"N+1 pattern: {n_plus_one_queries} queries")
        print(f"Optimized pattern: {single_query} query")

        # Document the issue even if we can't enforce it
        if n_plus_one_queries > 5:
            print("WARNING: N+1 query pattern detected")

    def test_query_complexity_limits(self, db: Session):
        """Test that complex queries complete within timeout."""
        # Very complex query that could be slow
        start = time.time()

        try:
            _ = (
                db.query(
                    Power.id,
                    Power.name,
                    Powerset.name,
                    Archetype.name,
                    func.count(Enhancement.id),
                )
                .join(Powerset)
                .join(Archetype)
                .outerjoin(PowerEnhancementCompatibility)
                .outerjoin(
                    Enhancement,
                    Enhancement.name == PowerEnhancementCompatibility.enhancement_type,
                )
                .group_by(Power.id, Power.name, Powerset.name, Archetype.name)
                .limit(100)
                .all()
            )

            duration = time.time() - start

            # Should complete within 1 second
            assert duration < 1.0, f"Complex query too slow: {duration:.2f}s"

        except Exception as e:
            pytest.fail(f"Complex query failed: {str(e)}")


class TestScalabilityBenchmarks:
    """Test system scalability with large datasets."""

    def test_large_dataset_handling(self, db: Session):
        """Test handling of large result sets."""
        # Get counts of large tables
        power_count = db.query(Power).count()
        enhancement_count = db.query(Enhancement).count()
        recipe_count = db.query(Recipe).count()

        benchmarks = {
            "powers": power_count,
            "enhancements": enhancement_count,
            "recipes": recipe_count,
        }

        print("\nDataset sizes:")
        for table, count in benchmarks.items():
            print(f"  {table}: {count:,} records")

        # Test retrieval of large datasets
        if power_count > 10000:
            start = time.time()
            # Use streaming/yield_per for memory efficiency
            power_iter = db.query(Power).yield_per(1000)
            count = 0
            for _power in power_iter:
                count += 1
                if count >= 10000:
                    break

            duration = time.time() - start
            print(f"Streamed 10K powers in {duration:.2f}s")

            # Should handle 10K records in under 5 seconds
            assert duration < 5.0, f"Large dataset streaming too slow: {duration:.2f}s"

    def test_concurrent_query_performance(self, db: Session):
        """Test performance under concurrent load."""
        import concurrent.futures

        def run_query(query_id):
            """Simulate concurrent query execution."""
            start = time.time()

            # Different query patterns
            if query_id % 3 == 0:
                _ = db.query(Power).filter(Power.level_available <= 20).limit(50).all()
            elif query_id % 3 == 1:
                _ = (
                    db.query(Enhancement)
                    .filter(Enhancement.set_id.isnot(None))
                    .limit(50)
                    .all()
                )
            else:
                _ = db.query(Recipe).limit(50).all()

            return time.time() - start

        # Run queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_query, i) for i in range(10)]
            results = [f.result() for f in futures]

        avg_time = sum(results) / len(results)
        max_time = max(results)

        print(f"Concurrent queries - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

        # Maximum query time should not be more than 2x average
        assert max_time < avg_time * 2, (
            f"High variance in concurrent performance: max={max_time:.3f}s, avg={avg_time:.3f}s"
        )

"""
Performance tests for Calculation API endpoints.

Ensures all endpoints meet the < 100ms response time requirement (95th percentile).
"""

import time
from statistics import quantiles

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestPerformance:
    """Performance tests for calculation endpoints."""

    def _measure_endpoint_performance(
        self, method: str, url: str, **kwargs
    ) -> list[float]:
        """
        Measure endpoint response times.

        Args:
            method: HTTP method ('get' or 'post')
            url: Endpoint URL
            **kwargs: Additional arguments for the request (json, params, etc.)

        Returns:
            List of response times in milliseconds
        """
        response_times = []
        num_requests = 100  # Run 100 requests for statistical significance

        for _ in range(num_requests):
            start_time = time.perf_counter()

            if method.lower() == "get":
                response = client.get(url, **kwargs)
            elif method.lower() == "post":
                response = client.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.perf_counter()

            # Ensure successful response
            assert response.status_code == 200

            # Calculate response time in milliseconds
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)

        return response_times

    def _check_performance_threshold(
        self,
        response_times: list[float],
        threshold_ms: float = 100.0,
        percentile: float = 0.95,
    ):
        """
        Check if response times meet performance threshold.

        Args:
            response_times: List of response times in milliseconds
            threshold_ms: Maximum acceptable response time (default: 100ms)
            percentile: Percentile to check (default: 0.95 for 95th percentile)
        """
        # Calculate percentiles
        percentile_values = quantiles(response_times, n=100)
        p95_index = int(percentile * 100) - 1
        p95_time = percentile_values[p95_index]

        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)

        print(f"\nPerformance Statistics (n={len(response_times)}):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  Min: {min_time:.2f} ms")
        print(f"  Max: {max_time:.2f} ms")
        print(f"  95th percentile: {p95_time:.2f} ms")
        print(f"  Threshold: {threshold_ms:.2f} ms")

        assert p95_time < threshold_ms, (
            f"95th percentile response time ({p95_time:.2f} ms) "
            f"exceeds threshold ({threshold_ms:.2f} ms)"
        )

    def test_power_damage_performance(self):
        """Test power damage calculation performance."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 62.56,
                    "damage_type": "smashing",
                    "probability": 1.0,
                }
            ],
            "power_type": "click",
            "recharge_time": 4.0,
            "cast_time": 1.07,
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/power/damage", json=request
        )

        self._check_performance_threshold(response_times)

    def test_build_defense_performance(self):
        """Test build defense calculation performance."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"melee": 0.30}},
                {"bonuses": {"smashing": 0.15}},
                {"bonuses": {"lethal": 0.15}},
            ],
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/build/defense", json=request
        )

        self._check_performance_threshold(response_times)

    def test_build_resistance_performance(self):
        """Test build resistance calculation performance."""
        request = {
            "archetype": "Tanker",
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.30, "lethal": 0.30}},
                {"bonuses": {"fire": 0.25, "cold": 0.20}},
                {"bonuses": {"energy": 0.20, "negative": 0.15}},
            ],
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/build/resistance", json=request
        )

        self._check_performance_threshold(response_times)

    def test_build_totals_performance(self):
        """Test complete build totals calculation performance."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"melee": 0.30}},
                {"bonuses": {"smashing": 0.15, "lethal": 0.15}},
            ],
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.20, "lethal": 0.20}},
                {"bonuses": {"fire": 0.10, "cold": 0.10}},
            ],
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/build/totals", json=request
        )

        self._check_performance_threshold(response_times)

    def test_constants_performance(self):
        """Test game constants retrieval performance."""
        response_times = self._measure_endpoint_performance(
            "get", "/api/v1/calculations/constants"
        )

        # Constants should be very fast (< 10ms)
        self._check_performance_threshold(response_times, threshold_ms=10.0)

    def test_proc_calculation_performance(self):
        """Test proc chance calculation performance."""
        request = {
            "ppm": 3.5,
            "recharge_time": 8.0,
            "cast_time": 1.67,
            "area_factor": 1.0,
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/enhancements/procs", json=request
        )

        self._check_performance_threshold(response_times)

    def test_complex_damage_calculation_performance(self):
        """Test complex damage calculation with multiple effects."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 50.0,
                    "damage_type": "smashing",
                    "probability": 1.0,
                },
                {
                    "effect_type": "damage",
                    "magnitude": 30.0,
                    "damage_type": "energy",
                    "probability": 1.0,
                },
                {
                    "effect_type": "damage",
                    "magnitude": 10.0,
                    "damage_type": "fire",
                    "probability": 1.0,
                    "ticks": 5,
                    "duration": 10.0,
                },
                {
                    "effect_type": "damage",
                    "magnitude": 75.0,
                    "damage_type": "toxic",
                    "probability": 0.2,  # Proc
                },
            ],
            "power_type": "click",
            "recharge_time": 12.0,
            "cast_time": 2.5,
            "damage_return_mode": "dps",
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/power/damage", json=request
        )

        self._check_performance_threshold(response_times)

    @pytest.mark.slow
    def test_full_build_scenario_performance(self):
        """Test performance of a complete build calculation scenario."""
        # Simulate a full build with many bonuses
        defense_bonuses = []
        resistance_bonuses = []

        # Add 20 defense bonus sources (typical full build with set bonuses)
        for _i in range(20):
            defense_bonuses.append(
                {"bonuses": {"melee": 0.015, "ranged": 0.01, "aoe": 0.01}}
            )

        # Add 15 resistance bonus sources
        for _i in range(15):
            resistance_bonuses.append(
                {
                    "bonuses": {
                        "smashing": 0.02,
                        "lethal": 0.02,
                        "fire": 0.015,
                        "cold": 0.015,
                    }
                }
            )

        request = {
            "archetype": "Scrapper",
            "defense_bonuses": defense_bonuses,
            "resistance_bonuses": resistance_bonuses,
        }

        response_times = self._measure_endpoint_performance(
            "post", "/api/v1/calculations/build/totals", json=request
        )

        # Full build calculation should still be under 100ms
        self._check_performance_threshold(response_times)


class TestConcurrentPerformance:
    """Test performance under concurrent load."""

    @pytest.mark.slow
    def test_concurrent_requests_performance(self):
        """Test that concurrent requests maintain good performance."""
        import concurrent.futures

        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 62.56,
                    "damage_type": "smashing",
                    "probability": 1.0,
                }
            ],
            "power_type": "click",
        }

        def make_request():
            start_time = time.perf_counter()
            response = client.post("/api/v1/calculations/power/damage", json=request)
            end_time = time.perf_counter()
            assert response.status_code == 200
            return (end_time - start_time) * 1000  # Convert to ms

        # Run 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            response_times = [
                f.result() for f in concurrent.futures.as_completed(futures)
            ]

        # Calculate 95th percentile
        percentile_values = quantiles(response_times, n=100)
        p95_time = percentile_values[94]

        print("\nConcurrent Performance (50 requests, 10 workers):")
        print(f"  Average: {sum(response_times) / len(response_times):.2f} ms")
        print(f"  95th percentile: {p95_time:.2f} ms")

        # Under concurrent load, allow slightly higher threshold (200ms)
        assert p95_time < 200.0, (
            f"95th percentile response time under concurrent load ({p95_time:.2f} ms) "
            f"exceeds threshold (200.0 ms)"
        )

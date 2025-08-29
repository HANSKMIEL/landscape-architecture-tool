#!/usr/bin/env python3
"""
Test CI/CD stability and performance under various conditions
"""

import gc
import os
import threading
import time
from unittest.mock import patch

import pytest

from src.main import create_app
from src.models.landscape import Plant
from src.models.user import db
from tests.conftest import _cleanup_database


class TestCIStability:
    """Test CI/CD pipeline stability and robustness"""

    def test_memory_usage_monitoring(self, app_context):
        """Monitor memory usage during test execution"""
        import psutil
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform some database operations
        for i in range(10):
            plant = Plant(
                name=f"Memory Test Plant {i}",
                common_name=f"Memory Plant {i}",
                category="Memory"
            )
            db.session.add(plant)
        
        db.session.commit()
        
        # Force garbage collection
        gc.collect()
        
        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for this test)
        assert memory_increase < 50, f"Memory usage increased by {memory_increase:.2f}MB"

    def test_database_cleanup_performance(self, app_context):
        """Test database cleanup performance"""
        # Create multiple records
        plants = []
        for i in range(20):
            plant = Plant(
                name=f"Cleanup Test Plant {i}",
                common_name=f"Cleanup Plant {i}",
                category="Cleanup"
            )
            plants.append(plant)
            db.session.add(plant)
        
        db.session.commit()
        
        # Measure cleanup time
        start_time = time.time()
        _cleanup_database()
        cleanup_time = time.time() - start_time
        
        # Cleanup should complete quickly (under 10 seconds)
        assert cleanup_time < 10, f"Database cleanup took {cleanup_time:.2f}s (too slow)"
        
        # Verify cleanup was effective
        remaining_count = db.session.query(Plant).count()
        assert remaining_count == 0, f"Cleanup incomplete - {remaining_count} plants remain"

    def test_concurrent_test_simulation(self, app_context):
        """Simulate concurrent test execution"""
        results = []
        errors = []
        
        def test_worker(worker_id):
            try:
                # Each worker creates and cleans up data
                plant = Plant(
                    name=f"Concurrent Worker {worker_id}",
                    common_name=f"Worker {worker_id} Plant",
                    category="Concurrent"
                )
                db.session.add(plant)
                db.session.commit()
                
                # Verify creation
                count = db.session.query(Plant).filter_by(name=f"Concurrent Worker {worker_id}").count()
                results.append((worker_id, count))
                
                # Clean up this worker's data
                db.session.delete(plant)
                db.session.commit()
                
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=test_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all workers to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per thread
            assert not thread.is_alive(), "Worker thread did not complete in time"
        
        # Check results
        assert len(errors) == 0, f"Worker errors: {errors}"
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # Verify all workers succeeded
        for worker_id, count in results:
            assert count == 1, f"Worker {worker_id} failed to create plant"

    def test_ci_environment_detection(self):
        """Test CI environment detection and configuration"""
        # Check if running in CI
        is_ci = os.environ.get("CI") == "true"
        
        if is_ci:
            # In CI, verify specific optimizations are in place
            assert "PYTHONPATH" in os.environ, "PYTHONPATH should be set in CI"
            assert os.environ.get("FLASK_ENV") == "testing", "FLASK_ENV should be testing in CI"
            
            # Check for CI-specific timeout configurations
            app = create_app()
            engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
            
            if "postgresql" in str(app.config.get("SQLALCHEMY_DATABASE_URI", "")):
                # PostgreSQL-specific CI checks
                assert "pool_timeout" in engine_options, "PostgreSQL should have pool_timeout configured"
                assert engine_options.get("pool_pre_ping") is True, "PostgreSQL should have pool_pre_ping enabled"

    def test_timeout_resilience(self, app_context):
        """Test timeout resilience under various conditions"""
        # Test database operation timeouts
        start_time = time.time()
        
        try:
            # Perform operations that should complete quickly
            for i in range(5):
                plant = Plant(
                    name=f"Timeout Test Plant {i}",
                    common_name=f"Timeout Plant {i}",
                    category="Timeout"
                )
                db.session.add(plant)
            
            db.session.commit()
            
            # Query operations
            plants = db.session.query(Plant).filter_by(category="Timeout").all()
            assert len(plants) == 5
            
        except Exception as e:
            pytest.fail(f"Database operations failed: {e}")
        
        total_time = time.time() - start_time
        # Operations should complete in reasonable time (under 5 seconds)
        assert total_time < 5, f"Database operations took {total_time:.2f}s (too slow)"

    def test_error_recovery(self, app_context):
        """Test error recovery and cleanup"""
        # Simulate various error conditions and verify recovery
        
        # Test 1: Session error recovery
        try:
            # Force a session error
            with patch.object(db.session, 'commit', side_effect=Exception("Simulated commit error")):
                plant = Plant(name="Error Test", category="Error")
                db.session.add(plant)
                db.session.commit()
        except Exception:
            # Should be able to recover
            db.session.rollback()
        
        # Verify session is still functional
        test_plant = Plant(name="Recovery Test", category="Recovery")
        db.session.add(test_plant)
        db.session.commit()
        
        count = db.session.query(Plant).count()
        assert count == 1, "Session recovery failed"

    @pytest.mark.timeout(60)
    def test_overall_test_suite_timing(self, app_context):
        """Test that individual operations complete within expected timeframes"""
        operations = []
        
        # Test various database operations with timing
        start = time.time()
        
        # Create operation
        plant = Plant(name="Timing Test", category="Timing")
        db.session.add(plant)
        db.session.commit()
        operations.append(("create", time.time() - start))
        
        # Query operation
        start = time.time()
        found_plant = db.session.query(Plant).filter_by(name="Timing Test").first()
        operations.append(("query", time.time() - start))
        assert found_plant is not None
        
        # Update operation
        start = time.time()
        found_plant.common_name = "Updated Timing Test"
        db.session.commit()
        operations.append(("update", time.time() - start))
        
        # Delete operation
        start = time.time()
        db.session.delete(found_plant)
        db.session.commit()
        operations.append(("delete", time.time() - start))
        
        # All operations should be fast (under 1 second each)
        for operation, duration in operations:
            assert duration < 1.0, f"{operation} operation took {duration:.3f}s (too slow)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
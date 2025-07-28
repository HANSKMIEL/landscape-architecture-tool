#!/usr/bin/env python3
"""
Tests for performance optimization framework
"""

import time
import unittest
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.performance import (
    PerformanceMetrics, 
    PerformanceMonitoringMiddleware,
    monitor_db_performance,
    cache_result,
    performance_metrics
)
from src.utils.cache import CacheService, cached, cache_api_response
from src.services.performance_analytics import PerformanceAnalyticsService


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics collection"""
    
    def setUp(self):
        self.metrics = PerformanceMetrics(max_history=10)
    
    def test_add_request_time(self):
        """Test request time tracking"""
        self.metrics.add_request_time("/api/test", "GET", 0.5, 200)
        
        self.assertEqual(len(self.metrics.request_times), 1)
        request = self.metrics.request_times[0]
        self.assertEqual(request['endpoint'], "/api/test")
        self.assertEqual(request['method'], "GET")
        self.assertEqual(request['duration'], 0.5)
        self.assertEqual(request['status_code'], 200)
    
    def test_add_db_query_time(self):
        """Test database query time tracking"""
        self.metrics.add_db_query_time("SELECT * FROM test", 0.1)
        
        self.assertEqual(len(self.metrics.db_query_times), 1)
        query = self.metrics.db_query_times[0]
        self.assertEqual(query['query'], "SELECT * FROM test")
        self.assertEqual(query['duration'], 0.1)
    
    def test_endpoint_stats(self):
        """Test endpoint statistics calculation"""
        # Add multiple requests to same endpoint
        self.metrics.add_request_time("/api/test", "GET", 0.5, 200)
        self.metrics.add_request_time("/api/test", "GET", 0.3, 200)
        self.metrics.add_request_time("/api/test", "GET", 0.7, 200)
        
        stats = self.metrics.endpoint_stats["GET /api/test"]
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['total_time'], 1.5)
        self.assertEqual(stats['avg_time'], 0.5)
        self.assertEqual(stats['max_time'], 0.7)
        self.assertEqual(stats['min_time'], 0.3)
    
    def test_slow_query_tracking(self):
        """Test slow query tracking"""
        with patch('src.utils.performance.current_app') as mock_app:
            mock_app.config.get.return_value = 0.05  # 50ms threshold
            
            # Add a slow query
            self.metrics.add_db_query_time("SELECT * FROM big_table", 0.1)
            
            self.assertEqual(len(self.metrics.slow_queries), 1)
    
    def test_get_summary(self):
        """Test performance summary generation"""
        # Add some test data
        self.metrics.add_request_time("/api/test", "GET", 0.5, 200)
        self.metrics.add_db_query_time("SELECT * FROM test", 0.1)
        self.metrics.add_memory_usage()
        
        summary = self.metrics.get_summary(5)
        
        self.assertIn('requests', summary)
        self.assertIn('database', summary)
        self.assertIn('memory', summary)
        self.assertEqual(summary['requests']['total_requests'], 1)
        self.assertEqual(summary['database']['total_queries'], 1)


class TestCacheService(unittest.TestCase):
    """Test caching service"""
    
    def setUp(self):
        self.cache = CacheService(default_timeout=1)
    
    def test_memory_cache_set_get(self):
        """Test memory cache set and get operations"""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        
        self.assertEqual(result, "test_value")
        self.assertEqual(self.cache.cache_stats['sets'], 1)
        self.assertEqual(self.cache.cache_stats['hits'], 1)
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        self.cache.set("test_key", "test_value", timeout=0.1)
        
        # Should exist immediately
        result = self.cache.get("test_key")
        self.assertEqual(result, "test_value")
        
        # Should expire after timeout
        time.sleep(0.2)
        result = self.cache.get("test_key")
        self.assertIsNone(result)
    
    def test_cache_delete(self):
        """Test cache deletion"""
        self.cache.set("test_key", "test_value")
        self.assertTrue(self.cache.delete("test_key"))
        
        result = self.cache.get("test_key")
        self.assertIsNone(result)
    
    def test_cache_clear(self):
        """Test cache clearing"""
        self.cache.set("test_key1", "value1")
        self.cache.set("test_key2", "value2")
        
        cleared = self.cache.clear()
        self.assertEqual(cleared, 2)
        
        self.assertIsNone(self.cache.get("test_key1"))
        self.assertIsNone(self.cache.get("test_key2"))
    
    def test_cache_stats(self):
        """Test cache statistics"""
        self.cache.set("test_key", "test_value")
        self.cache.get("test_key")
        self.cache.get("nonexistent_key")
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['stats']['sets'], 1)
        self.assertEqual(stats['stats']['hits'], 1)
        self.assertEqual(stats['stats']['misses'], 1)
        self.assertEqual(stats['hit_rate'], 0.5)


class TestCachedDecorator(unittest.TestCase):
    """Test cached decorator"""
    
    def test_cached_function(self):
        """Test function result caching"""
        call_count = 0
        
        @cached(timeout=1)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increase
        
        # Different argument should execute function
        result3 = test_function(10)
        self.assertEqual(result3, 20)
        self.assertEqual(call_count, 2)


class TestDbPerformanceMonitor(unittest.TestCase):
    """Test database performance monitoring"""
    
    def test_monitor_db_performance_decorator(self):
        """Test database performance monitoring decorator"""
        
        @monitor_db_performance
        def mock_db_operation():
            time.sleep(0.01)  # Simulate database operation
            return "result"
        
        with patch('src.utils.performance.current_app') as mock_app:
            mock_app.config.get.return_value = True
            
            with patch('src.utils.performance.performance_metrics') as mock_metrics:
                result = mock_db_operation()
                
                self.assertEqual(result, "result")
                mock_metrics.add_db_query_time.assert_called_once()
                
                # Check that duration was recorded
                call_args = mock_metrics.add_db_query_time.call_args
                self.assertGreater(call_args[1]['duration'], 0)


class TestPerformanceAnalytics(unittest.TestCase):
    """Test performance analytics service"""
    
    def setUp(self):
        self.analytics = PerformanceAnalyticsService()
    
    def test_determine_severity(self):
        """Test alert severity determination"""
        self.assertEqual(self.analytics._determine_severity(3.0, 1.0), 'critical')
        self.assertEqual(self.analytics._determine_severity(2.5, 1.0), 'high')
        self.assertEqual(self.analytics._determine_severity(1.6, 1.0), 'medium')
        self.assertEqual(self.analytics._determine_severity(1.2, 1.0), 'low')
    
    def test_calculate_health_score(self):
        """Test health score calculation"""
        # Test good performance
        good_metrics = {
            'requests': {'avg_response_time': 0.2, 'error_rate': 0.001},
            'memory': {'current_memory_mb': 100},
            'database': {'avg_query_time': 0.05}
        }
        good_cache_stats = {'hit_rate': 0.9}
        
        score = self.analytics._calculate_health_score(good_metrics, good_cache_stats)
        self.assertGreater(score, 90)
        
        # Test poor performance
        poor_metrics = {
            'requests': {'avg_response_time': 3.0, 'error_rate': 0.15},
            'memory': {'current_memory_mb': 600},
            'database': {'avg_query_time': 0.6}
        }
        poor_cache_stats = {'hit_rate': 0.3}
        
        score = self.analytics._calculate_health_score(poor_metrics, poor_cache_stats)
        self.assertLess(score, 50)
    
    def test_update_thresholds(self):
        """Test threshold updates"""
        new_thresholds = {
            'slow_request_threshold': 1.5,
            'slow_query_threshold': 0.2
        }
        
        success = self.analytics.update_thresholds(new_thresholds)
        self.assertTrue(success)
        self.assertEqual(self.analytics.thresholds['slow_request_threshold'], 1.5)
        self.assertEqual(self.analytics.thresholds['slow_query_threshold'], 0.2)
    
    def test_resolve_alert(self):
        """Test alert resolution"""
        # Create a mock alert
        alert = {
            'id': 'test_alert_123',
            'type': 'slow_request',
            'severity': 'medium',
            'message': 'Test alert',
            'timestamp': '2023-01-01T10:00:00',
            'resolved': False
        }
        self.analytics.alerts.append(alert)
        
        # Resolve the alert
        success = self.analytics.resolve_alert('test_alert_123')
        self.assertTrue(success)
        self.assertTrue(alert['resolved'])
        
        # Try to resolve non-existent alert
        success = self.analytics.resolve_alert('nonexistent_alert')
        self.assertFalse(success)


class TestCacheResult(unittest.TestCase):
    """Test cache_result decorator"""
    
    def test_cache_result_decorator(self):
        """Test cache_result decorator functionality"""
        call_count = 0
        
        @cache_result(timeout=1)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate expensive operation
            return x + y
        
        # First call should execute function
        start_time = time.time()
        result1 = expensive_function(1, 2)
        first_call_time = time.time() - start_time
        
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache (much faster)
        start_time = time.time()
        result2 = expensive_function(1, 2)
        second_call_time = time.time() - start_time
        
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Should not increase
        self.assertLess(second_call_time, first_call_time / 2)  # Should be much faster


if __name__ == '__main__':
    unittest.main()
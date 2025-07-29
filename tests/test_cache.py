"""
Tests for API response caching functionality
"""

import pytest
import time
import json
from unittest.mock import patch, MagicMock

from src.services.cache_service import CacheService, cache_response, invalidate_cache_for_model


class TestCacheService:
    """Test the caching service functionality"""

    def test_memory_cache_initialization(self):
        """Test cache service initializes with memory cache when Redis unavailable"""
        cache = CacheService(redis_url="memory://")
        assert cache.enabled is True
        assert cache.redis_client is None
        assert hasattr(cache, '_memory_cache')

    def test_cache_set_and_get_memory(self):
        """Test basic cache operations with memory backend"""
        cache = CacheService(redis_url="memory://")
        
        # Test setting and getting values
        test_data = {"test": "data", "number": 123}
        result = cache.set("test_key", test_data, timeout=300)
        assert result is True
        
        retrieved = cache.get("test_key")
        assert retrieved == test_data

    def test_cache_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        cache = CacheService(redis_url="memory://")
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_delete(self):
        """Test cache deletion"""
        cache = CacheService(redis_url="memory://")
        
        cache.set("delete_test", {"data": "to_delete"})
        assert cache.get("delete_test") is not None
        
        cache.delete("delete_test")
        assert cache.get("delete_test") is None

    def test_cache_memory_limit(self):
        """Test that memory cache limits its size"""
        cache = CacheService(redis_url="memory://")
        
        # Fill cache beyond limit
        for i in range(1200):  # More than the 1000 limit
            cache.set(f"key_{i}", f"value_{i}")
        
        # Cache should have been trimmed
        assert len(cache._memory_cache) <= 1000

    def test_cache_key_generation(self):
        """Test cache key generation"""
        cache = CacheService(redis_url="memory://")
        
        # Mock request context
        with patch('src.services.cache_service.request') as mock_request:
            mock_request.args = {"param1": "value1", "param2": "value2"}
            
            key1 = cache._generate_cache_key("test_endpoint", extra="param")
            key2 = cache._generate_cache_key("test_endpoint", extra="param")
            key3 = cache._generate_cache_key("test_endpoint", extra="different")
            
            # Same parameters should generate same key
            assert key1 == key2
            # Different parameters should generate different key
            assert key1 != key3

    def test_invalidate_pattern_memory(self):
        """Test pattern-based cache invalidation with memory backend"""
        cache = CacheService(redis_url="memory://")
        
        # Set up test data
        cache.set("api_cache:plants:key1", {"data": "plants1"})
        cache.set("api_cache:plants:key2", {"data": "plants2"})
        cache.set("api_cache:projects:key1", {"data": "projects1"})
        
        # Invalidate plants cache
        cache.invalidate_pattern("api_cache:plants*")
        
        # Plants cache should be gone, projects cache should remain
        assert cache.get("api_cache:plants:key1") is None
        assert cache.get("api_cache:plants:key2") is None
        assert cache.get("api_cache:projects:key1") is not None

    @patch('src.services.cache_service.redis')
    def test_redis_cache_operations(self, mock_redis):
        """Test cache operations with Redis backend"""
        # Mock Redis client
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        
        cache = CacheService(redis_url="redis://localhost:6379")
        
        # Test set operation
        test_data = {"test": "data"}
        cache.set("test_key", test_data, timeout=300)
        
        mock_redis_client.setex.assert_called_once()
        args = mock_redis_client.setex.call_args
        assert args[0][0] == "test_key"
        assert args[0][1] == 300
        # The data should be JSON serialized
        assert json.loads(args[0][2]) == test_data

    @patch('src.services.cache_service.redis')
    def test_redis_cache_get(self, mock_redis):
        """Test cache get operation with Redis backend"""
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        
        # Mock return value
        test_data = {"test": "data"}
        mock_redis_client.get.return_value = json.dumps(test_data).encode('utf-8')
        
        cache = CacheService(redis_url="redis://localhost:6379")
        result = cache.get("test_key")
        
        mock_redis_client.get.assert_called_once_with("test_key")
        assert result == test_data

    def test_cache_disabled_when_initialization_fails(self):
        """Test that cache gracefully disables when initialization fails"""
        with patch('src.services.cache_service.redis') as mock_redis:
            mock_redis.from_url.side_effect = Exception("Redis connection failed")
            
            cache = CacheService(redis_url="redis://localhost:6379")
            assert cache.enabled is False
            assert cache.redis_client is None

    def test_cache_performance_improvement(self):
        """Test that caching actually improves performance"""
        cache = CacheService(redis_url="memory://")
        
        # Simulate expensive operation
        def expensive_operation():
            time.sleep(0.1)  # 100ms operation
            return {"result": "expensive_data", "timestamp": time.time()}
        
        # First call - should be slow
        start_time = time.time()
        result1 = expensive_operation()
        cache.set("expensive_key", result1)
        first_call_time = time.time() - start_time
        
        # Second call - should be fast (from cache)
        start_time = time.time()
        result2 = cache.get("expensive_key")
        second_call_time = time.time() - start_time
        
        # Cache should be significantly faster
        assert second_call_time < first_call_time / 10  # At least 10x faster
        assert result1 == result2


class TestCacheDecorator:
    """Test the cache_response decorator"""

    def test_cache_decorator_memory_backend(self, app):
        """Test cache decorator with memory backend"""
        with app.app_context():
            # Initialize cache service
            from src.services.cache_service import init_cache_service
            init_cache_service(app)
            
            call_count = 0
            
            @cache_response(timeout=300)
            def test_function():
                nonlocal call_count
                call_count += 1
                return {"result": "test_data", "call_count": call_count}
            
            with patch('src.services.cache_service.request') as mock_request:
                mock_request.endpoint = "test_endpoint"
                mock_request.args = {}
                
                # First call - should execute function
                result1 = test_function()
                assert call_count == 1
                assert result1["call_count"] == 1
                
                # Second call - should use cache
                result2 = test_function()
                assert call_count == 1  # Function not called again
                assert result2["call_count"] == 1  # Cached result

    def test_cache_decorator_with_different_params(self, app):
        """Test that decorator creates different cache keys for different parameters"""
        with app.app_context():
            from src.services.cache_service import init_cache_service
            init_cache_service(app)
            
            call_count = 0
            
            @cache_response(timeout=300)
            def test_function():
                nonlocal call_count
                call_count += 1
                return {"result": "test_data", "call_count": call_count}
            
            with patch('src.services.cache_service.request') as mock_request:
                mock_request.endpoint = "test_endpoint"
                
                # First call with param1
                mock_request.args = {"param": "value1"}
                result1 = test_function()
                assert call_count == 1
                
                # Second call with param2 - should execute function again
                mock_request.args = {"param": "value2"}
                result2 = test_function()
                assert call_count == 2
                
                # Third call with param1 again - should use cache
                mock_request.args = {"param": "value1"}
                result3 = test_function()
                assert call_count == 2  # No additional call

    def test_cache_invalidation_function(self, app):
        """Test cache invalidation for model updates"""
        with app.app_context():
            from src.services.cache_service import init_cache_service, cache_service
            init_cache_service(app)
            
            # Set up test cache entries
            cache_service.set("api_cache:plants:key1", {"data": "plants1"})
            cache_service.set("api_cache:plants:key2", {"data": "plants2"})
            cache_service.set("api_cache:suppliers:key1", {"data": "suppliers1"})
            
            # Verify data is cached
            assert cache_service.get("api_cache:plants:key1") is not None
            assert cache_service.get("api_cache:suppliers:key1") is not None
            
            # Invalidate plants cache
            invalidate_cache_for_model("plants")
            
            # Plants cache should be invalidated, suppliers should remain
            assert cache_service.get("api_cache:plants:key1") is None
            assert cache_service.get("api_cache:plants:key2") is None
            assert cache_service.get("api_cache:suppliers:key1") is not None
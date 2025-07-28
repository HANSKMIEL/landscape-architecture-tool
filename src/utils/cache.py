#!/usr/bin/env python3
"""
Enhanced caching service for performance optimization
"""

import json
import time
import hashlib
import logging
from typing import Any, Dict, Optional, Union, Callable
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """Enhanced caching service with multiple backends"""
    
    def __init__(self, redis_client=None, default_timeout: int = 300):
        self.redis_client = redis_client
        self.default_timeout = default_timeout
        self.memory_cache = {}
        self.memory_cache_times = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def _get_cache_key(self, key: str, prefix: str = "cache") -> str:
        """Generate standardized cache key"""
        return f"{prefix}:{key}"
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        try:
            return json.dumps(value, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize cache value: {e}")
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        cache_key = self._get_cache_key(key)
        
        # Try Redis first if available
        if self.redis_client:
            try:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return self._deserialize(value.decode('utf-8'))
            except Exception as e:
                logger.warning(f"Redis cache get error: {e}")
                self.cache_stats['errors'] += 1
        
        # Fall back to memory cache
        now = time.time()
        if cache_key in self.memory_cache:
            cache_time = self.memory_cache_times.get(cache_key, 0)
            if now - cache_time < self.default_timeout:
                self.cache_stats['hits'] += 1
                return self.memory_cache[cache_key]
            else:
                # Expired, remove from memory cache
                del self.memory_cache[cache_key]
                del self.memory_cache_times[cache_key]
        
        self.cache_stats['misses'] += 1
        return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache"""
        cache_key = self._get_cache_key(key)
        timeout = timeout or self.default_timeout
        serialized_value = self._serialize(value)
        
        # Try Redis first if available
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, timeout, serialized_value)
                self.cache_stats['sets'] += 1
                return True
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")
                self.cache_stats['errors'] += 1
        
        # Fall back to memory cache
        self.memory_cache[cache_key] = value
        self.memory_cache_times[cache_key] = time.time()
        self.cache_stats['sets'] += 1
        
        # Prevent memory cache from growing too large
        if len(self.memory_cache) > 1000:
            self._cleanup_memory_cache()
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._get_cache_key(key)
        deleted = False
        
        # Delete from Redis if available
        if self.redis_client:
            try:
                deleted = bool(self.redis_client.delete(cache_key))
            except Exception as e:
                logger.warning(f"Redis cache delete error: {e}")
                self.cache_stats['errors'] += 1
        
        # Delete from memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            del self.memory_cache_times[cache_key]
            deleted = True
        
        if deleted:
            self.cache_stats['deletes'] += 1
        
        return deleted
    
    def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        cleared = 0
        
        # Clear Redis if available
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"cache:{pattern}")
                if keys:
                    cleared += self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis cache clear error: {e}")
                self.cache_stats['errors'] += 1
        
        # Clear memory cache
        if pattern == "*":
            cleared += len(self.memory_cache)
            self.memory_cache.clear()
            self.memory_cache_times.clear()
        else:
            # Simple pattern matching for memory cache
            keys_to_delete = []
            for key in self.memory_cache.keys():
                if pattern in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                del self.memory_cache_times[key]
                cleared += 1
        
        return cleared
    
    def _cleanup_memory_cache(self):
        """Clean up old entries from memory cache"""
        now = time.time()
        keys_to_delete = []
        
        for key, cache_time in self.memory_cache_times.items():
            if now - cache_time > self.default_timeout:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.memory_cache[key]
            del self.memory_cache_times[key]
        
        # If still too large, remove oldest entries
        if len(self.memory_cache) > 1000:
            sorted_keys = sorted(
                self.memory_cache_times.items(),
                key=lambda x: x[1]
            )
            keys_to_remove = sorted_keys[:len(sorted_keys) // 2]
            
            for key, _ in keys_to_remove:
                del self.memory_cache[key]
                del self.memory_cache_times[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_operations = (
            self.cache_stats['hits'] + 
            self.cache_stats['misses'] + 
            self.cache_stats['sets'] + 
            self.cache_stats['deletes']
        )
        
        hit_rate = 0.0
        if self.cache_stats['hits'] + self.cache_stats['misses'] > 0:
            hit_rate = self.cache_stats['hits'] / (
                self.cache_stats['hits'] + self.cache_stats['misses']
            )
        
        return {
            'stats': self.cache_stats.copy(),
            'hit_rate': hit_rate,
            'total_operations': total_operations,
            'memory_cache_size': len(self.memory_cache),
            'redis_available': self.redis_client is not None
        }


# Global cache service instance
cache_service = CacheService()


def init_cache_service(redis_client=None, default_timeout: int = 300):
    """Initialize cache service with Redis client"""
    global cache_service
    cache_service = CacheService(redis_client, default_timeout)
    return cache_service


def cached(timeout: int = 300, key_prefix: str = "func"):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                'func': f"{func.__module__}.{func.__name__}",
                'args': args,
                'kwargs': kwargs
            }
            key_str = json.dumps(key_data, sort_keys=True, default=str)
            cache_key = f"{key_prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
            
            # Try to get from cache
            result = cache_service.get(cache_key)
            if result is not None:
                return result
            
            # Calculate and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, timeout)
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: cache_service.clear(f"{key_prefix}:*")
        wrapper.cache_info = lambda: cache_service.get_stats()
        
        return wrapper
    return decorator


def cache_api_response(timeout: int = 300):
    """Decorator to cache API response"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Generate cache key from request
            cache_key_data = {
                'endpoint': request.endpoint,
                'method': request.method,
                'args': request.args.to_dict(),
                'path': request.path
            }
            
            if request.method in ['POST', 'PUT', 'PATCH']:
                # Don't cache modifying operations
                return func(*args, **kwargs)
            
            cache_key_str = json.dumps(cache_key_data, sort_keys=True)
            cache_key = f"api:{hashlib.md5(cache_key_str.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_response = cache_service.get(cache_key)
            if cached_response is not None:
                response = jsonify(cached_response)
                response.headers['X-Cache'] = 'HIT'
                return response
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Only cache successful responses
            if hasattr(result, 'status_code') and result.status_code == 200:
                try:
                    response_data = result.get_json()
                    cache_service.set(cache_key, response_data, timeout)
                    result.headers['X-Cache'] = 'MISS'
                except Exception as e:
                    logger.warning(f"Failed to cache API response: {e}")
            
            return result
        
        return wrapper
    return decorator


class QueryCache:
    """Specialized cache for database queries"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.query_stats = {
            'cached_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time_saved': 0.0
        }
    
    def cache_query(self, timeout: int = 600):
        """Decorator to cache database query results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key_data = {
                    'query_func': f"{func.__module__}.{func.__name__}",
                    'args': str(args),
                    'kwargs': str(sorted(kwargs.items()))
                }
                key_str = json.dumps(key_data, sort_keys=True)
                cache_key = f"query:{hashlib.md5(key_str.encode()).hexdigest()}"
                
                # Try to get from cache
                start_time = time.time()
                cached_result = self.cache_service.get(cache_key)
                
                if cached_result is not None:
                    self.query_stats['cache_hits'] += 1
                    query_time = time.time() - start_time
                    self.query_stats['total_time_saved'] += query_time
                    return cached_result
                
                # Execute query and cache result
                result = func(*args, **kwargs)
                self.cache_service.set(cache_key, result, timeout)
                
                self.query_stats['cache_misses'] += 1
                self.query_stats['cached_queries'] += 1
                
                return result
            
            return wrapper
        return decorator
    
    def invalidate_related(self, table_names: Union[str, list]):
        """Invalidate cache entries related to specific tables"""
        if isinstance(table_names, str):
            table_names = [table_names]
        
        for table_name in table_names:
            pattern = f"query:*{table_name}*"
            cleared = self.cache_service.clear(pattern)
            logger.info(f"Cleared {cleared} cache entries for table {table_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query cache statistics"""
        total_queries = self.query_stats['cache_hits'] + self.query_stats['cache_misses']
        hit_rate = 0.0
        
        if total_queries > 0:
            hit_rate = self.query_stats['cache_hits'] / total_queries
        
        return {
            'query_stats': self.query_stats.copy(),
            'hit_rate': hit_rate,
            'total_queries': total_queries
        }


# Global query cache instance
query_cache = QueryCache(cache_service)


def invalidate_cache_on_change(table_names: Union[str, list]):
    """Decorator to invalidate cache when data changes"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Invalidate related cache entries after successful execution
            query_cache.invalidate_related(table_names)
            return result
        return wrapper
    return decorator
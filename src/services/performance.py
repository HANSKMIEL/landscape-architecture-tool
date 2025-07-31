"""
Performance optimization utilities for the landscape architecture tool.
Provides caching, query optimization, and performance monitoring capabilities.
"""

import functools
import json
import logging
import os
import time
from typing import Any, Callable, Dict, Optional

import redis
from flask import current_app, request

# Simple in-memory cache as fallback
_memory_cache = {}


class PerformanceCache:
    """Simple caching service with Redis primary and memory fallback."""

    def __init__(self):
        self.redis_client = None
        # Only try Redis if explicitly configured
        redis_url = os.environ.get("REDIS_URL")
        if redis_url and not redis_url.startswith("memory://"):
            try:
                # Try to connect to Redis if available
                self.redis_client = redis.Redis(
                    host="localhost",
                    port=6379,
                    db=1,
                    decode_responses=True,
                    socket_connect_timeout=1,
                )
                # Test connection
                self.redis_client.ping()
            except redis.exceptions.ConnectionError:
                # Silently fall back to memory cache in development
                self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except (redis.RedisError, json.JSONDecodeError, TypeError):
                pass

        # Fallback to memory cache
        return _memory_cache.get(key)

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in cache with timeout in seconds."""
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    self.redis_client.setex(key, timeout, json.dumps(value))
                    return True
                except (redis.RedisError, json.JSONEncodeError, TypeError):
                    pass

            # Fallback to memory cache (no timeout support in simple implementation)
            _memory_cache[key] = value
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_client:
                try:
                    self.redis_client.delete(key)
                except Exception:
                    pass

            _memory_cache.pop(key, None)
            return True
        except Exception:
            return False

    def clear(self) -> bool:
        """Clear all cache."""
        try:
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                except Exception:
                    pass

            _memory_cache.clear()
            return True
        except Exception:
            return False


def cached(cache: PerformanceCache, timeout: int = 300, key_prefix: str = None):
    """
    Decorator for caching function results.

    Args:
        cache: Instance of PerformanceCache to use.
       timeout: Cache timeout in seconds (default: 5 minutes)
       key_prefix: Optional prefix for cache keys
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            args_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{key_prefix or func.__name__}:{hash(args_str)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def cache_api_response(timeout: int = 300):
    """
    Decorator for caching API responses.

    Args:
        timeout: Cache timeout in seconds
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Only cache GET requests
            if request.method != "GET":
                return func(*args, **kwargs)

            # Generate cache key from URL and query parameters
            cache_key = f"api:{request.path}:{hash(str(request.args))}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)

            # Only cache successful responses
            if hasattr(result, "status_code") and result.status_code == 200:
                cache.set(
                    cache_key,
                    result.get_json() if hasattr(result, "get_json") else result,
                    timeout,
                )

            return result

        return wrapper

    return decorator


class QueryPerformanceMonitor:
    """Simple query performance monitoring."""

    @staticmethod
    def monitor_db_performance(func: Callable) -> Callable:
        """Decorator to monitor database query performance."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log slow queries (configurable threshold)
                try:
                    slow_query_threshold = float(
                        current_app.config.get("SLOW_QUERY_THRESHOLD", 0.1)
                    )
                except RuntimeError:
                    # No Flask context, use default threshold
                    slow_query_threshold = 0.1

                if execution_time > slow_query_threshold:
                    try:
                        current_app.logger.warning(
                            f"Slow query detected: {func.__name__} took "
                            f"{execution_time:.3f}s"
                        )
                    except RuntimeError:
                        logging.warning(
                            f"Slow query detected: {func.__name__} took "
                            f"{execution_time:.3f}s"
                        )

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                try:
                    current_app.logger.error(
                        f"Query error in {func.__name__} after "
                        f"{execution_time:.3f}s: {str(e)}"
                    )
                except RuntimeError:
                    logging.getLogger(__name__).error(
                        f"Query error in {func.__name__} after "
                        f"{execution_time:.3f}s: {str(e)}"
                    )
                raise

        return wrapper


# Performance monitoring decorator
monitor_db_performance = QueryPerformanceMonitor.monitor_db_performance


def get_cache_stats() -> Dict[str, Any]:
    """Get cache performance statistics."""
    stats = {
        "redis_available": cache.redis_client is not None,
        "memory_cache_size": len(_memory_cache),
        "cache_backend": "Redis + Memory" if cache.redis_client else "Memory only",
    }

    if cache.redis_client:
        try:
            info = cache.redis_client.info()
            stats.update(
                {
                    "redis_used_memory": info.get("used_memory_human", "Unknown"),
                    "redis_keyspace_hits": info.get("keyspace_hits", 0),
                    "redis_keyspace_misses": info.get("keyspace_misses", 0),
                }
            )

            # Calculate hit rate
            hits = stats["redis_keyspace_hits"]
            misses = stats["redis_keyspace_misses"]
            if hits + misses > 0:
                stats["cache_hit_rate"] = round(hits / (hits + misses) * 100, 2)
        except Exception:
            pass

    return stats


def clear_cache_by_pattern(pattern: str) -> bool:
    """Clear cache entries matching a pattern."""
    try:
        if cache.redis_client:
            try:
                keys = cache.redis_client.keys(pattern)
                if keys:
                    cache.redis_client.delete(*keys)
            except Exception:
                pass

        # Clear memory cache entries (simple pattern matching)
        keys_to_delete = [
            k for k in _memory_cache.keys() if pattern.replace("*", "") in k
        ]
        for key in keys_to_delete:
            del _memory_cache[key]

        return True
    except Exception:
        return False


# Global cache instance with lazy initialization
_cache_instance = None


def get_cache() -> PerformanceCache:
    """Get or initialize the global PerformanceCache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = PerformanceCache()
    return _cache_instance


# Expose cache instance at module level for imports
cache = get_cache()


# Utility functions for common caching patterns
def cache_dashboard_stats(func):
    """Cache dashboard statistics for 2 minutes."""
    return cached(cache, timeout=120, key_prefix="dashboard_stats")(func)


def cache_plant_data(func):
    """Cache plant data for 10 minutes."""
    return cached(cache, timeout=600, key_prefix="plants")(func)


def cache_project_data(func):
    """Cache project data for 5 minutes."""
    return cached(cache, timeout=300, key_prefix="projects")(func)


# Invalidation helpers
def invalidate_dashboard_cache():
    """Invalidate dashboard-related cache entries."""
    clear_cache_by_pattern("dashboard_stats:*")
    clear_cache_by_pattern("api:/api/dashboard/*")


def invalidate_plant_cache():
    """Invalidate plant-related cache entries."""
    clear_cache_by_pattern("plants:*")
    clear_cache_by_pattern("api:/api/plants*")


def invalidate_project_cache():
    """Invalidate project-related cache entries."""
    clear_cache_by_pattern("projects:*")
    clear_cache_by_pattern("api:/api/projects*")

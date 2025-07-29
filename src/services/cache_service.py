"""
API Response Caching Service
Implements Redis-based caching for frequently accessed endpoints
"""

import json
import logging
import redis
from functools import wraps
from flask import request, current_app
from typing import Any, Optional, Callable
import hashlib


logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for API responses"""
    
    def __init__(self, redis_url: str = None):
        """Initialize cache service with Redis connection"""
        try:
            if redis_url and redis_url != "memory://":
                self.redis_client = redis.from_url(redis_url)
            else:
                # Fallback to in-memory cache for development
                self.redis_client = None
                self._memory_cache = {}
                logger.info("Using in-memory cache (Redis not available)")
                
            self.enabled = True
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, endpoint: str, **kwargs) -> str:
        """Generate a unique cache key based on endpoint and parameters"""
        # Include request args in cache key
        params = dict(request.args) if request else {}
        params.update(kwargs)
        
        # Create a deterministic key
        key_data = {
            'endpoint': endpoint,
            'params': sorted(params.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"api_cache:{endpoint}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None
            
        try:
            if self.redis_client:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached.decode('utf-8'))
            else:
                # Use memory cache
                return self._memory_cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set cached value with optional timeout (default 5 minutes)"""
        if not self.enabled:
            return False
            
        try:
            if self.redis_client:
                serialized = json.dumps(value, default=str)
                self.redis_client.setex(key, timeout, serialized)
            else:
                # Use memory cache (no timeout in simple implementation)
                self._memory_cache[key] = value
                # Keep memory cache size reasonable
                if len(self._memory_cache) > 1000:
                    # Remove oldest half of entries
                    keys = list(self._memory_cache.keys())
                    for k in keys[:500]:
                        del self._memory_cache[k]
            
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        if not self.enabled:
            return False
            
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate all keys matching a pattern"""
        if not self.enabled:
            return False
            
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Pattern matching for memory cache
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                for k in keys_to_delete:
                    del self._memory_cache[k]
            return True
        except Exception as e:
            logger.warning(f"Cache invalidation failed for pattern {pattern}: {e}")
            return False


# Global cache service instance
cache_service = None


def init_cache_service(app):
    """Initialize cache service with Flask app"""
    global cache_service
    redis_url = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    cache_service = CacheService(redis_url)
    return cache_service


def cache_response(timeout: int = 300, key_suffix: str = None):
    """Decorator to cache API responses
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_suffix: Optional suffix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_service or not cache_service.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            endpoint = request.endpoint or func.__name__
            if key_suffix:
                endpoint = f"{endpoint}_{key_suffix}"
            
            cache_key = cache_service._generate_cache_key(endpoint, **kwargs)
            
            # Try to get from cache
            cached_response = cache_service.get(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_response
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            # Only cache successful responses (200 status)
            if hasattr(result, 'status_code'):
                if result.status_code == 200:
                    cache_service.set(cache_key, result.get_json(), timeout)
            else:
                # For direct JSON responses
                cache_service.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_for_model(model_name: str):
    """Invalidate cache for all endpoints related to a model"""
    if cache_service and cache_service.enabled:
        pattern = f"api_cache:*{model_name.lower()}*"
        cache_service.invalidate_pattern(pattern)
        logger.info(f"Invalidated cache for model: {model_name}")


# Cache configuration for different endpoints
CACHE_TIMEOUTS = {
    'plants': 600,  # 10 minutes - plant data changes infrequently
    'suppliers': 900,  # 15 minutes - supplier data very stable
    'products': 300,  # 5 minutes - product data may change more often
    'clients': 1800,  # 30 minutes - client data very stable
    'projects': 180,  # 3 minutes - project data changes more frequently
    'dashboard': 120,  # 2 minutes - dashboard needs fresher data
    'analytics': 1800,  # 30 minutes - analytics can be cached longer
}


def get_cache_timeout(endpoint: str) -> int:
    """Get appropriate cache timeout for endpoint"""
    for key, timeout in CACHE_TIMEOUTS.items():
        if key in endpoint.lower():
            return timeout
    return 300  # Default 5 minutes
# Performance Cache Documentation

## Overview

The landscape architecture tool includes a performance optimization module (`src/services/performance.py`) that provides caching, query optimization, and performance monitoring capabilities.

## Cache Module Usage

### Importing the Cache

The performance module exposes a global `cache` instance that can be imported directly:

```python
from src.services.performance import cache
```

This import is guaranteed to work and provides access to a `PerformanceCache` instance with Redis primary storage and in-memory fallback.

### Basic Cache Operations

```python
from src.services.performance import cache

# Set a value with default timeout (5 minutes)
cache.set("my_key", {"data": "value"})

# Set a value with custom timeout (timeout is in seconds)
cache.set("my_key", {"data": "value"}, timeout=600)  # timeout in seconds (10 minutes)

# Get a value
result = cache.get("my_key")

# Delete a value
cache.delete("my_key")

# Clear all cache
cache.clear()
```

### Available Functions and Decorators

The module also provides convenient decorators and utilities:

```python
from src.services.performance import (
    cache,                      # Global cache instance
    cached,                     # Generic caching decorator
    cache_api_response,         # API response caching decorator
    cache_dashboard_stats,      # Dashboard-specific caching
    cache_plant_data,          # Plant data caching
    cache_project_data,        # Project data caching
    get_cache_stats,           # Get cache performance stats
    clear_cache_by_pattern,    # Clear cache by pattern
    monitor_db_performance,    # Database performance monitoring
    invalidate_dashboard_cache, # Dashboard cache invalidation
    invalidate_plant_cache,    # Plant cache invalidation
    invalidate_project_cache   # Project cache invalidation
)
```

### Usage in Routes

The cache is commonly used in route handlers:

```python
from src.services.performance import cache, get_cache_stats

@app.route('/api/performance/stats')
def get_performance_stats():
    return jsonify(get_cache_stats())

@app.route('/api/performance/cache/clear', methods=['POST'])
def clear_cache():
    success = cache.clear()
    return jsonify({'success': success})
```

## Cache Backend

The cache system uses a dual-tier approach:

1. **Primary**: Redis cache (if available)
2. **Fallback**: In-memory Python dictionary cache

If Redis is not available (connection fails), the system automatically falls back to memory-only caching without errors.

## Performance Monitoring

The cache system includes built-in performance monitoring:

```python
from src.services.performance import get_cache_stats

stats = get_cache_stats()
# Returns: {
#     'redis_available': bool,
#     'memory_cache_size': int,
#     'cache_backend': str,
#     'redis_used_memory': str,
#     'redis_keyspace_hits': int,
#     'redis_keyspace_misses': int,
#     'cache_hit_rate': float
# }
```

## Module-Level Cache Availability

The `cache` instance is available at the module level and is initialized when the module is imported. This ensures that:

1. `from src.services.performance import cache` always works
2. The same cache instance is shared across all imports
3. No additional initialization is required

## Testing

The cache functionality is thoroughly tested in `tests/services/test_performance_cache.py`, which includes:

- Import validation tests
- Basic functionality tests
- Redis fallback tests
- Module consistency tests
- Performance validation tests

Run the cache tests with:

```bash
pytest tests/services/test_performance_cache.py -v
```

## Development Notes

- The cache is initialized lazily but exposed at module level for guaranteed imports
- Redis connection failures are handled gracefully with automatic fallback
- All cache operations are designed to be non-blocking and fault-tolerant
- Cache keys should be descriptive and use consistent patterns for easy management
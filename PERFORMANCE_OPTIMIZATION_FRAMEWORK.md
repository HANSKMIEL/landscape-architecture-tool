# Performance Optimization Framework

This document describes the comprehensive performance optimization framework implemented for the Landscape Architecture Management Tool.

## Overview

The Performance Optimization Framework provides real-time monitoring, caching, and analytics capabilities to ensure optimal application performance. The framework is designed to be non-intrusive, configurable, and production-ready.

## Features

### 1. Performance Monitoring

#### Request Monitoring
- **Request timing**: Tracks response times for all API endpoints
- **Endpoint statistics**: Aggregated metrics per endpoint (avg, min, max response times)
- **Slow request detection**: Configurable thresholds for identifying slow requests
- **Error rate monitoring**: Tracks HTTP error rates per endpoint

#### Database Monitoring
- **Query performance**: Monitors execution time for all database queries
- **Slow query detection**: Identifies queries exceeding configurable thresholds
- **Query statistics**: Aggregated database performance metrics
- **SQLAlchemy integration**: Automatic monitoring via SQLAlchemy event hooks

#### System Monitoring
- **Memory usage**: Real-time memory consumption tracking
- **Background monitoring**: Non-blocking system metrics collection
- **Resource utilization**: CPU and disk usage monitoring

### 2. Multi-Tier Caching

#### Cache Layers
- **Redis Cache**: Primary cache layer for production environments
- **Memory Cache**: Fallback cache layer for development or when Redis is unavailable
- **Automatic fallback**: Seamless switching between cache layers

#### Caching Strategies
- **Function result caching**: `@cached` decorator for expensive operations
- **API response caching**: `@cache_api_response` decorator for GET endpoints
- **Query result caching**: Specialized caching for database queries
- **Automatic invalidation**: Cache invalidation on data modifications

#### Cache Management
- **Statistics tracking**: Hit rates, miss rates, and operation counts
- **Manual clearing**: API endpoints for cache management
- **Pattern-based clearing**: Clear cache entries by pattern
- **Expiration handling**: Automatic cleanup of expired entries

### 3. Performance Analytics

#### Health Scoring
- **Overall health score**: 0-100 score based on multiple metrics
- **Component scoring**: Individual scores for requests, database, memory, cache
- **Threshold-based evaluation**: Configurable performance thresholds

#### Alert System
- **Severity levels**: Low, Medium, High, Critical alerts
- **Alert types**: Slow requests, slow queries, high memory, high error rates
- **Alert management**: Resolution tracking and history
- **Real-time monitoring**: Continuous alert generation

#### Trend Analysis
- **Performance trends**: Historical performance data analysis
- **Trend detection**: Identification of improving/degrading performance
- **Time-series data**: Support for trend analysis over time periods

## API Endpoints

### Performance Metrics
```
GET /api/performance/metrics
```
Returns current performance metrics including request times, database performance, and memory usage.

**Response Example:**
```json
{
  "timestamp": "2023-07-28T10:30:00Z",
  "period_minutes": 5,
  "requests": {
    "total_requests": 150,
    "avg_response_time": 0.25,
    "max_response_time": 1.2,
    "min_response_time": 0.05,
    "error_rate": 0.02
  },
  "database": {
    "total_queries": 300,
    "avg_query_time": 0.05,
    "max_query_time": 0.15,
    "slow_query_count": 2
  },
  "memory": {
    "current_memory_mb": 185.5,
    "avg_memory_mb": 180.2,
    "max_memory_mb": 195.0
  }
}
```

### Performance Analytics
```
GET /api/performance/analytics?minutes=5
```
Returns detailed performance analytics including health score, alerts, and recommendations.

**Response Example:**
```json
{
  "timestamp": "2023-07-28T10:30:00Z",
  "health_score": 85,
  "alerts": [],
  "recommendations": [
    "Consider enabling response caching for frequently accessed endpoints"
  ],
  "cache_performance": {
    "hit_rate": 0.75,
    "total_operations": 500
  }
}
```

### Performance Summary
```
GET /api/performance/summary
```
Returns a quick performance overview suitable for dashboards.

**Response Example:**
```json
{
  "status": "healthy",
  "health_score": 85,
  "active_alerts": 0,
  "key_metrics": {
    "avg_response_time": 0.25,
    "error_rate": 0.02,
    "cache_hit_rate": 0.75,
    "memory_usage_mb": 185.5
  }
}
```

### Performance Alerts
```
GET /api/performance/alerts?resolved=false
```
Returns performance alerts with optional filtering by resolution status.

```
POST /api/performance/alerts/{alert_id}/resolve
```
Marks a specific alert as resolved.

### Performance Thresholds
```
GET /api/performance/thresholds
```
Returns current performance monitoring thresholds.

```
PUT /api/performance/thresholds
```
Updates performance monitoring thresholds.

**Request Body Example:**
```json
{
  "slow_request_threshold": 1.0,
  "slow_query_threshold": 0.1,
  "high_memory_threshold": 500.0,
  "error_rate_threshold": 0.1
}
```

### Cache Management
```
GET /api/performance/cache/stats
```
Returns cache performance statistics.

```
POST /api/performance/cache/clear
```
Clears cache entries, optionally by pattern.

**Request Body Example:**
```json
{
  "pattern": "dashboard:*"
}
```

## Configuration

### Environment Variables

```bash
# Performance monitoring
PERFORMANCE_MONITORING_ENABLED=true
SLOW_REQUEST_THRESHOLD=1.0          # seconds
SLOW_QUERY_THRESHOLD=0.1            # seconds
MEMORY_MONITORING_ENABLED=true
CACHE_DEFAULT_TIMEOUT=300           # seconds

# Redis configuration (optional)
REDIS_URL=redis://localhost:6379/0
```

### Application Configuration

```python
# config.py
class Config:
    # Performance monitoring
    PERFORMANCE_MONITORING_ENABLED = True
    SLOW_REQUEST_THRESHOLD = 1.0
    SLOW_QUERY_THRESHOLD = 0.1
    MEMORY_MONITORING_ENABLED = True
    CACHE_DEFAULT_TIMEOUT = 300
```

## Usage Examples

### Adding Performance Monitoring to Functions

```python
from src.utils.performance import monitor_db_performance

@monitor_db_performance
def expensive_database_operation():
    # Database operation code
    return result
```

### Adding Caching to Functions

```python
from src.utils.cache import cached

@cached(timeout=600, key_prefix="user_data")
def get_user_data(user_id):
    # Expensive operation
    return data
```

### Adding API Response Caching

```python
from src.utils.cache import cache_api_response

@app.route("/api/data")
@cache_api_response(timeout=300)
def get_data():
    return jsonify(expensive_data_operation())
```

### Cache Invalidation

```python
from src.utils.cache import invalidate_cache_on_change

@invalidate_cache_on_change("users")
def update_user(user_id, data):
    # Update operation that should invalidate user-related cache
    return updated_user
```

## Performance Best Practices

### 1. Caching Strategy
- Cache frequently accessed data with appropriate timeouts
- Use shorter timeouts for data that changes frequently
- Implement cache invalidation for data modifications
- Monitor cache hit rates and adjust strategies accordingly

### 2. Database Optimization
- Monitor slow queries and optimize them
- Use database indexes for frequently queried fields
- Implement pagination for large result sets
- Consider query result caching for expensive operations

### 3. API Performance
- Cache GET endpoint responses when appropriate
- Implement rate limiting to prevent abuse
- Use compression for large responses
- Monitor endpoint performance and optimize slow endpoints

### 4. Memory Management
- Monitor memory usage trends
- Implement memory-efficient data structures
- Clear unnecessary data from memory
- Use appropriate cache sizes to prevent memory exhaustion

## Monitoring and Alerting

### Health Score Calculation

The health score (0-100) is calculated based on:
- **Response Time** (30% weight): Penalty for slow response times
- **Error Rate** (25% weight): Penalty for high error rates
- **Memory Usage** (20% weight): Penalty for high memory consumption
- **Database Performance** (15% weight): Penalty for slow queries
- **Cache Performance** (10% weight): Bonus for high cache hit rates

### Alert Severity Levels

- **Critical**: Performance is severely degraded (>3x threshold)
- **High**: Performance is significantly impacted (>2x threshold)
- **Medium**: Performance is moderately impacted (>1.5x threshold)
- **Low**: Performance is slightly impacted (>1x threshold)

### Recommended Thresholds

#### Development Environment
```
SLOW_REQUEST_THRESHOLD=1.0          # 1 second
SLOW_QUERY_THRESHOLD=0.1            # 100ms
HIGH_MEMORY_THRESHOLD=500.0         # 500MB
ERROR_RATE_THRESHOLD=0.1            # 10%
```

#### Production Environment
```
SLOW_REQUEST_THRESHOLD=0.5          # 500ms
SLOW_QUERY_THRESHOLD=0.05           # 50ms
HIGH_MEMORY_THRESHOLD=200.0         # 200MB
ERROR_RATE_THRESHOLD=0.05           # 5%
```

## Troubleshooting

### Common Issues

#### High Memory Usage
1. Check for memory leaks in application code
2. Review cache sizes and implement cleanup
3. Monitor background processes
4. Consider increasing server memory

#### Slow Response Times
1. Identify slow endpoints using performance metrics
2. Optimize database queries
3. Implement response caching
4. Review and optimize business logic

#### Low Cache Hit Rates
1. Review cache key strategies
2. Adjust cache timeouts
3. Implement better cache warming
4. Monitor cache invalidation patterns

#### Database Performance Issues
1. Identify slow queries from performance logs
2. Add appropriate database indexes
3. Optimize query logic
4. Consider query result caching

### Performance Debugging

```python
# Enable detailed performance logging
import logging
logging.getLogger('src.utils.performance').setLevel(logging.DEBUG)

# Get detailed performance report
from src.services.performance_analytics import get_performance_analytics
analytics = get_performance_analytics()
detailed_report = analytics.get_detailed_performance_report()
```

## Integration with Existing Code

The Performance Optimization Framework is designed to integrate seamlessly with existing code:

1. **Middleware Integration**: Automatic request monitoring without code changes
2. **Decorator-Based**: Add performance monitoring with simple decorators
3. **Service Enhancement**: Existing services are enhanced with minimal changes
4. **Configuration-Driven**: Enable/disable features via configuration
5. **Backward Compatibility**: No breaking changes to existing functionality

This framework provides a solid foundation for maintaining optimal application performance while being flexible enough to adapt to changing requirements.
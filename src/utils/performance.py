#!/usr/bin/env python3
"""
Performance monitoring and optimization utilities
"""

import time
import logging
import psutil
import threading
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Callable
from flask import Flask, request, g, jsonify, current_app
import sqlite3


logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Collects and stores performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_times = deque(maxlen=max_history)
        self.db_query_times = deque(maxlen=max_history)
        self.memory_usage = deque(maxlen=max_history)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'max_time': 0.0,
            'min_time': float('inf')
        })
        self.slow_queries = deque(maxlen=100)
        self.slow_requests = deque(maxlen=100)
        self._lock = threading.Lock()
    
    def add_request_time(self, endpoint: str, method: str, duration: float, status_code: int):
        """Add request timing data"""
        with self._lock:
            timestamp = datetime.now()
            self.request_times.append({
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'timestamp': timestamp
            })
            
            # Update endpoint statistics
            key = f"{method} {endpoint}"
            stats = self.endpoint_stats[key]
            stats['count'] += 1
            stats['total_time'] += duration
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['max_time'] = max(stats['max_time'], duration)
            stats['min_time'] = min(stats['min_time'], duration)
            
            # Track slow requests
            if duration > current_app.config.get('SLOW_REQUEST_THRESHOLD', 1.0):
                self.slow_requests.append({
                    'endpoint': endpoint,
                    'method': method,
                    'duration': duration,
                    'timestamp': timestamp
                })
    
    def add_db_query_time(self, query: str, duration: float, params: Optional[Any] = None):
        """Add database query timing data"""
        with self._lock:
            timestamp = datetime.now()
            self.db_query_times.append({
                'query': query[:200],  # Truncate long queries
                'duration': duration,
                'params': str(params)[:100] if params else None,
                'timestamp': timestamp
            })
            
            # Track slow queries
            if duration > current_app.config.get('SLOW_QUERY_THRESHOLD', 0.1):
                self.slow_queries.append({
                    'query': query[:500],
                    'duration': duration,
                    'params': str(params)[:200] if params else None,
                    'timestamp': timestamp
                })
    
    def add_memory_usage(self):
        """Add current memory usage"""
        with self._lock:
            process = psutil.Process()
            memory_info = process.memory_info()
            self.memory_usage.append({
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent(),
                'timestamp': datetime.now()
            })
    
    def get_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """Get performance summary for the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            # Filter recent data
            recent_requests = [r for r in self.request_times if r['timestamp'] >= cutoff_time]
            recent_queries = [q for q in self.db_query_times if q['timestamp'] >= cutoff_time]
            recent_memory = [m for m in self.memory_usage if m['timestamp'] >= cutoff_time]
            
            # Calculate request statistics
            request_stats = {
                'total_requests': len(recent_requests),
                'avg_response_time': 0.0,
                'max_response_time': 0.0,
                'min_response_time': float('inf'),
                'error_rate': 0.0
            }
            
            if recent_requests:
                durations = [r['duration'] for r in recent_requests]
                request_stats['avg_response_time'] = sum(durations) / len(durations)
                request_stats['max_response_time'] = max(durations)
                request_stats['min_response_time'] = min(durations)
                
                error_count = len([r for r in recent_requests if r['status_code'] >= 400])
                request_stats['error_rate'] = error_count / len(recent_requests)
            
            # Calculate database statistics
            db_stats = {
                'total_queries': len(recent_queries),
                'avg_query_time': 0.0,
                'max_query_time': 0.0,
                'slow_query_count': len([q for q in recent_queries if q['duration'] > 0.1])
            }
            
            if recent_queries:
                durations = [q['duration'] for q in recent_queries]
                db_stats['avg_query_time'] = sum(durations) / len(durations)
                db_stats['max_query_time'] = max(durations)
            
            # Calculate memory statistics
            memory_stats = {
                'current_memory_mb': 0.0,
                'avg_memory_mb': 0.0,
                'max_memory_mb': 0.0
            }
            
            if recent_memory:
                current_rss = recent_memory[-1]['rss'] / 1024 / 1024
                avg_rss = sum(m['rss'] for m in recent_memory) / len(recent_memory) / 1024 / 1024
                max_rss = max(m['rss'] for m in recent_memory) / 1024 / 1024
                
                memory_stats['current_memory_mb'] = current_rss
                memory_stats['avg_memory_mb'] = avg_rss
                memory_stats['max_memory_mb'] = max_rss
            
            return {
                'timestamp': datetime.now().isoformat(),
                'period_minutes': minutes,
                'requests': request_stats,
                'database': db_stats,
                'memory': memory_stats,
                'slow_requests': len(self.slow_requests),
                'slow_queries': len(self.slow_queries)
            }


# Global performance metrics instance
performance_metrics = PerformanceMetrics()


class PerformanceMonitoringMiddleware:
    """Flask middleware for performance monitoring"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Set default configuration
        app.config.setdefault('PERFORMANCE_MONITORING_ENABLED', True)
        app.config.setdefault('SLOW_REQUEST_THRESHOLD', 1.0)  # seconds
        app.config.setdefault('SLOW_QUERY_THRESHOLD', 0.1)   # seconds
        app.config.setdefault('MEMORY_MONITORING_ENABLED', True)
        
        # Start background memory monitoring
        if app.config.get('MEMORY_MONITORING_ENABLED'):
            self._start_memory_monitoring()
    
    def before_request(self):
        """Called before each request"""
        if current_app.config.get('PERFORMANCE_MONITORING_ENABLED'):
            g.start_time = time.time()
    
    def after_request(self, response):
        """Called after each request"""
        if current_app.config.get('PERFORMANCE_MONITORING_ENABLED'):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                performance_metrics.add_request_time(
                    endpoint=request.endpoint or request.path,
                    method=request.method,
                    duration=duration,
                    status_code=response.status_code
                )
        return response
    
    def _start_memory_monitoring(self):
        """Start background thread for memory monitoring"""
        def monitor_memory():
            while True:
                try:
                    performance_metrics.add_memory_usage()
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"Memory monitoring error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=monitor_memory, daemon=True)
        thread.start()


def monitor_db_performance(func: Callable) -> Callable:
    """Decorator to monitor database operation performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_app.config.get('PERFORMANCE_MONITORING_ENABLED'):
            return func(*args, **kwargs)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Try to extract query information
            query_info = str(func.__name__)
            if hasattr(func, '__self__'):
                query_info = f"{func.__self__.__class__.__name__}.{func.__name__}"
            
            performance_metrics.add_db_query_time(
                query=query_info,
                duration=duration,
                params=f"args={len(args)}, kwargs={len(kwargs)}"
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            performance_metrics.add_db_query_time(
                query=f"FAILED: {func.__name__}",
                duration=duration,
                params=str(e)[:100]
            )
            raise
    
    return wrapper


class DatabasePerformanceProfiler:
    """Database query performance profiler for SQLAlchemy"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize database profiler"""
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            
            @event.listens_for(Engine, "before_cursor_execute")
            def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                if app.config.get('PERFORMANCE_MONITORING_ENABLED'):
                    context._query_start_time = time.time()
            
            @event.listens_for(Engine, "after_cursor_execute")
            def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                if app.config.get('PERFORMANCE_MONITORING_ENABLED'):
                    if hasattr(context, '_query_start_time'):
                        duration = time.time() - context._query_start_time
                        performance_metrics.add_db_query_time(
                            query=statement,
                            duration=duration,
                            params=parameters
                        )
        except ImportError:
            logger.warning("SQLAlchemy not available for database profiling")


def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    return performance_metrics.get_summary()


def get_detailed_performance_report() -> Dict[str, Any]:
    """Get detailed performance report"""
    with performance_metrics._lock:
        return {
            'summary_5min': performance_metrics.get_summary(5),
            'summary_60min': performance_metrics.get_summary(60),
            'endpoint_stats': dict(performance_metrics.endpoint_stats),
            'slow_requests': list(performance_metrics.slow_requests)[-10:],
            'slow_queries': list(performance_metrics.slow_queries)[-10:],
            'system_info': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_available': psutil.virtual_memory().available / 1024 / 1024,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }


# Performance optimization decorators
def cache_result(timeout: int = 300):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check if cached result is still valid
            now = time.time()
            if key in cache and now - cache_times[key] < timeout:
                return cache[key]
            
            # Calculate and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = now
            
            # Clean old cache entries
            if len(cache) > 100:  # Prevent unbounded growth
                oldest_key = min(cache_times.keys(), key=cache_times.get)
                del cache[oldest_key]
                del cache_times[oldest_key]
            
            return result
        
        return wrapper
    return decorator


def rate_limit_endpoint(per_minute: int = 60):
    """Decorator to rate limit endpoint calls"""
    request_times = defaultdict(deque)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get client identifier
            client_id = request.remote_addr
            
            # Clean old requests
            now = time.time()
            minute_ago = now - 60
            times = request_times[client_id]
            while times and times[0] < minute_ago:
                times.popleft()
            
            # Check rate limit
            if len(times) >= per_minute:
                from flask import jsonify
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Record this request
            times.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
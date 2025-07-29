#!/usr/bin/env python3
"""
Performance Framework Demo Script

This script demonstrates the performance optimization framework capabilities.
"""

import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.utils.performance import PerformanceMetrics, performance_metrics
    from src.utils.cache import CacheService, cached
    from src.services.performance_analytics import PerformanceAnalyticsService
    
    print("✅ Performance Optimization Framework Demo")
    print("=" * 50)
    
    # Demo 1: Performance Metrics Collection
    print("\n📊 Demo 1: Performance Metrics Collection")
    metrics = PerformanceMetrics()
    
    # Simulate some requests
    metrics.add_request_time("/api/plants", "GET", 0.25, 200)
    metrics.add_request_time("/api/projects", "GET", 0.45, 200)
    metrics.add_request_time("/api/dashboard/stats", "GET", 0.15, 200)
    metrics.add_request_time("/api/plants", "POST", 0.35, 201)
    metrics.add_request_time("/api/error", "GET", 1.2, 500)  # Slow request with error
    
    # Simulate some database queries
    metrics.add_db_query_time("SELECT * FROM plants WHERE category = ?", 0.05, ["trees"])
    metrics.add_db_query_time("SELECT COUNT(*) FROM projects", 0.02)
    metrics.add_db_query_time("SELECT * FROM large_table JOIN other_table", 0.15)  # Slow query
    
    # Add memory usage
    metrics.add_memory_usage()
    
    # Get summary
    summary = metrics.get_summary(5)
    print(f"📈 Total Requests: {summary['requests']['total_requests']}")
    print(f"⏱️  Average Response Time: {summary['requests']['avg_response_time']:.3f}s")
    print(f"🐌 Max Response Time: {summary['requests']['max_response_time']:.3f}s")
    print(f"❌ Error Rate: {summary['requests']['error_rate']:.1%}")
    print(f"🗄️  Total Queries: {summary['database']['total_queries']}")
    print(f"⏲️  Average Query Time: {summary['database']['avg_query_time']:.3f}s")
    print(f"🐌 Slow Queries: {summary['database']['slow_query_count']}")
    print(f"💾 Current Memory: {summary['memory']['current_memory_mb']:.1f}MB")
    
    # Demo 2: Caching System
    print("\n🗄️  Demo 2: Caching System")
    cache = CacheService(default_timeout=2)  # 2 second timeout for demo
    
    # Cache some data
    cache.set("user:123", {"name": "Hans Kmiel", "role": "admin"})
    cache.set("plants:count", 25)
    cache.set("dashboard:stats", {"projects": 10, "clients": 5})
    
    # Retrieve cached data
    user_data = cache.get("user:123")
    plants_count = cache.get("plants:count")
    stats = cache.get("dashboard:stats")
    
    print(f"👤 Cached User: {user_data}")
    print(f"🌱 Plants Count: {plants_count}")
    print(f"📊 Dashboard Stats: {stats}")
    
    # Test cache expiration
    print("\n⏳ Testing cache expiration...")
    time.sleep(2.5)  # Wait for cache to expire
    
    expired_user = cache.get("user:123")
    print(f"👤 Expired User Data: {expired_user}")  # Should be None
    
    # Get cache statistics
    cache_stats = cache.get_stats()
    print(f"📈 Cache Hit Rate: {cache_stats['hit_rate']:.1%}")
    print(f"🎯 Cache Hits: {cache_stats['stats']['hits']}")
    print(f"❌ Cache Misses: {cache_stats['stats']['misses']}")
    
    # Demo 3: Function Caching Decorator
    print("\n🎯 Demo 3: Function Caching Decorator")
    
    @cached(timeout=5, key_prefix="expensive_calc")
    def expensive_calculation(n):
        """Simulate an expensive calculation"""
        print(f"  🔄 Computing expensive calculation for n={n}...")
        time.sleep(0.1)  # Simulate work
        return n * n * n
    
    # First call - should execute function
    print("First call:")
    start_time = time.time()
    result1 = expensive_calculation(10)
    time1 = time.time() - start_time
    print(f"  Result: {result1}, Time: {time1:.3f}s")
    
    # Second call - should use cache
    print("Second call (cached):")
    start_time = time.time()
    result2 = expensive_calculation(10)
    time2 = time.time() - start_time
    print(f"  Result: {result2}, Time: {time2:.3f}s")
    
    print(f"  ⚡ Speed improvement: {time1/time2:.1f}x faster")
    
    # Demo 4: Performance Analytics
    print("\n📊 Demo 4: Performance Analytics")
    analytics = PerformanceAnalyticsService()
    
    # Create mock metrics for analysis
    mock_metrics = {
        'requests': {
            'total_requests': 100,
            'avg_response_time': 0.75,  # Slightly slow
            'max_response_time': 2.5,
            'min_response_time': 0.1,
            'error_rate': 0.05  # 5% error rate
        },
        'database': {
            'total_queries': 200,
            'avg_query_time': 0.08,
            'max_query_time': 0.3,
            'slow_query_count': 3
        },
        'memory': {
            'current_memory_mb': 180.5,
            'avg_memory_mb': 175.0,
            'max_memory_mb': 190.0
        }
    }
    
    mock_cache_stats = {
        'hit_rate': 0.65,  # 65% hit rate
        'total_operations': 150
    }
    
    # Calculate health score
    health_score = analytics._calculate_health_score(mock_metrics, mock_cache_stats)
    print(f"💪 Overall Health Score: {health_score}/100")
    
    # Check for alerts
    alerts = analytics._check_performance_alerts(mock_metrics)
    if alerts:
        print("🚨 Performance Alerts:")
        for alert in alerts:
            print(f"  {alert['severity'].upper()}: {alert['message']}")
    else:
        print("✅ No performance alerts")
    
    # Generate recommendations
    recommendations = analytics._generate_recommendations(mock_metrics, mock_cache_stats)
    if recommendations:
        print("💡 Performance Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 50)
    print("✅ Performance Framework Demo Complete!")
    print("\n🚀 Framework Features Demonstrated:")
    print("  ✓ Real-time performance metrics collection")
    print("  ✓ Multi-tier caching system")
    print("  ✓ Function result caching with decorators")
    print("  ✓ Performance analytics and health scoring")
    print("  ✓ Alert generation and recommendations")
    
    print("\n📖 Next Steps:")
    print("  1. Start the Flask application to see live monitoring")
    print("  2. Visit /api/performance/metrics for real-time data")
    print("  3. Check /api/performance/summary for health overview")
    print("  4. Use /api/performance/cache/stats for cache metrics")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip install flask psutil")
except Exception as e:
    print(f"❌ Error running demo: {e}")
    print("Check that all modules are properly installed and configured.")
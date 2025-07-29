#!/usr/bin/env python3
"""
Performance analytics and monitoring service
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from src.utils.performance import performance_metrics, get_performance_metrics
from src.utils.cache import cache_service, query_cache

logger = logging.getLogger(__name__)


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    id: str
    type: str  # 'slow_request', 'slow_query', 'high_memory', 'high_error_rate'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    endpoint: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    resolved: bool = False


class PerformanceAnalyticsService:
    """Service for analyzing and monitoring application performance"""
    
    def __init__(self):
        self.alerts = []
        self.alert_history = []
        self.thresholds = {
            'slow_request_threshold': 2.0,      # seconds
            'slow_query_threshold': 0.5,        # seconds
            'high_memory_threshold': 500.0,     # MB
            'error_rate_threshold': 0.1,        # 10%
            'cpu_threshold': 80.0,              # percentage
            'cache_hit_rate_threshold': 0.7     # 70%
        }
        self.monitoring_enabled = True
    
    def analyze_performance(self, minutes: int = 5) -> Dict[str, Any]:
        """Analyze performance over the specified time period"""
        try:
            metrics = get_performance_metrics()
            cache_stats = cache_service.get_stats()
            query_stats = query_cache.get_stats()
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'period_minutes': minutes,
                'metrics': metrics,
                'cache_performance': cache_stats,
                'query_performance': query_stats,
                'alerts': self._check_performance_alerts(metrics),
                'recommendations': self._generate_recommendations(metrics, cache_stats),
                'health_score': self._calculate_health_score(metrics, cache_stats)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'health_score': 0
            }
    
    def _check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance issues and generate alerts"""
        alerts = []
        current_time = datetime.now()
        
        # Check slow requests
        if metrics['requests']['avg_response_time'] > self.thresholds['slow_request_threshold']:
            alert = PerformanceAlert(
                id=f"slow_request_{int(time.time())}",
                type='slow_request',
                severity=self._determine_severity(
                    metrics['requests']['avg_response_time'],
                    self.thresholds['slow_request_threshold']
                ),
                message=f"Average response time is {metrics['requests']['avg_response_time']:.2f}s",
                timestamp=current_time,
                value=metrics['requests']['avg_response_time'],
                threshold=self.thresholds['slow_request_threshold']
            )
            alerts.append(asdict(alert))
        
        # Check slow queries
        if metrics['database']['avg_query_time'] > self.thresholds['slow_query_threshold']:
            alert = PerformanceAlert(
                id=f"slow_query_{int(time.time())}",
                type='slow_query',
                severity=self._determine_severity(
                    metrics['database']['avg_query_time'],
                    self.thresholds['slow_query_threshold']
                ),
                message=f"Average query time is {metrics['database']['avg_query_time']:.3f}s",
                timestamp=current_time,
                value=metrics['database']['avg_query_time'],
                threshold=self.thresholds['slow_query_threshold']
            )
            alerts.append(asdict(alert))
        
        # Check high memory usage
        if metrics['memory']['current_memory_mb'] > self.thresholds['high_memory_threshold']:
            alert = PerformanceAlert(
                id=f"high_memory_{int(time.time())}",
                type='high_memory',
                severity=self._determine_severity(
                    metrics['memory']['current_memory_mb'],
                    self.thresholds['high_memory_threshold']
                ),
                message=f"Memory usage is {metrics['memory']['current_memory_mb']:.1f}MB",
                timestamp=current_time,
                value=metrics['memory']['current_memory_mb'],
                threshold=self.thresholds['high_memory_threshold']
            )
            alerts.append(asdict(alert))
        
        # Check error rate
        if metrics['requests']['error_rate'] > self.thresholds['error_rate_threshold']:
            alert = PerformanceAlert(
                id=f"high_error_rate_{int(time.time())}",
                type='high_error_rate',
                severity=self._determine_severity(
                    metrics['requests']['error_rate'],
                    self.thresholds['error_rate_threshold']
                ),
                message=f"Error rate is {metrics['requests']['error_rate']:.1%}",
                timestamp=current_time,
                value=metrics['requests']['error_rate'],
                threshold=self.thresholds['error_rate_threshold']
            )
            alerts.append(asdict(alert))
        
        # Store alerts
        self.alerts.extend(alerts)
        self.alert_history.extend(alerts)
        
        # Keep only recent alerts
        cutoff_time = current_time - timedelta(hours=1)
        self.alerts = [
            alert for alert in self.alerts 
            if datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        
        return alerts
    
    def _determine_severity(self, value: float, threshold: float) -> str:
        """Determine alert severity based on how much the value exceeds threshold"""
        ratio = value / threshold
        
        if ratio > 3.0:
            return 'critical'
        elif ratio > 2.0:
            return 'high'
        elif ratio > 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, metrics: Dict[str, Any], cache_stats: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Slow response times
        if metrics['requests']['avg_response_time'] > 1.0:
            recommendations.append(
                "Consider enabling response caching for frequently accessed endpoints"
            )
            recommendations.append(
                "Review and optimize slow database queries"
            )
        
        # Low cache hit rate
        if cache_stats.get('hit_rate', 0) < self.thresholds['cache_hit_rate_threshold']:
            recommendations.append(
                f"Cache hit rate is {cache_stats.get('hit_rate', 0):.1%}. "
                "Consider increasing cache timeouts or improving cache key strategy"
            )
        
        # High database query count
        if metrics['database']['total_queries'] > metrics['requests']['total_requests'] * 2:
            recommendations.append(
                "High query-to-request ratio detected. Consider implementing query optimization or batch operations"
            )
        
        # Memory usage
        if metrics['memory']['current_memory_mb'] > 200:
            recommendations.append(
                "Memory usage is high. Consider implementing memory optimization strategies"
            )
        
        # Error rates
        if metrics['requests']['error_rate'] > 0.05:
            recommendations.append(
                "Error rate is elevated. Review application logs for common error patterns"
            )
        
        # Slow queries
        if metrics.get('slow_queries', 0) > 0:
            recommendations.append(
                f"Found {metrics.get('slow_queries', 0)} slow queries. "
                "Consider adding database indexes or optimizing query logic"
            )
        
        return recommendations
    
    def _calculate_health_score(self, metrics: Dict[str, Any], cache_stats: Dict[str, Any]) -> int:
        """Calculate overall application health score (0-100)"""
        score = 100
        
        # Response time penalty
        avg_response = metrics['requests']['avg_response_time']
        if avg_response > 2.0:
            score -= 30
        elif avg_response > 1.0:
            score -= 15
        elif avg_response > 0.5:
            score -= 5
        
        # Error rate penalty
        error_rate = metrics['requests']['error_rate']
        if error_rate > 0.1:
            score -= 25
        elif error_rate > 0.05:
            score -= 15
        elif error_rate > 0.01:
            score -= 5
        
        # Memory usage penalty
        memory_mb = metrics['memory']['current_memory_mb']
        if memory_mb > 500:
            score -= 20
        elif memory_mb > 300:
            score -= 10
        elif memory_mb > 200:
            score -= 5
        
        # Cache performance bonus/penalty
        hit_rate = cache_stats.get('hit_rate', 0)
        if hit_rate > 0.8:
            score += 5
        elif hit_rate < 0.5:
            score -= 10
        
        # Database performance penalty
        avg_query_time = metrics['database']['avg_query_time']
        if avg_query_time > 0.5:
            score -= 15
        elif avg_query_time > 0.1:
            score -= 5
        
        return max(0, min(100, score))
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        # This would typically read from a time-series database
        # For now, return current metrics as a trend point
        current_analysis = self.analyze_performance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'trend_data': [current_analysis],  # Would be multiple points in real implementation
            'trend_analysis': {
                'response_time_trend': 'stable',  # 'improving', 'degrading', 'stable'
                'error_rate_trend': 'stable',
                'memory_trend': 'stable',
                'cache_performance_trend': 'stable'
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summarized performance information"""
        current_metrics = get_performance_metrics()
        cache_stats = cache_service.get_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'status': self._get_overall_status(current_metrics),
            'health_score': self._calculate_health_score(current_metrics, cache_stats),
            'active_alerts': len([a for a in self.alerts if not a.get('resolved', False)]),
            'key_metrics': {
                'avg_response_time': current_metrics['requests']['avg_response_time'],
                'error_rate': current_metrics['requests']['error_rate'],
                'cache_hit_rate': cache_stats.get('hit_rate', 0),
                'memory_usage_mb': current_metrics['memory']['current_memory_mb']
            },
            'recommendations_count': len(self._generate_recommendations(current_metrics, cache_stats))
        }
    
    def _get_overall_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall application status"""
        if metrics['requests']['error_rate'] > 0.2:
            return 'critical'
        elif (metrics['requests']['avg_response_time'] > 3.0 or 
              metrics['requests']['error_rate'] > 0.1):
            return 'warning'
        elif (metrics['requests']['avg_response_time'] > 1.0 or 
              metrics['requests']['error_rate'] > 0.05):
            return 'degraded'
        else:
            return 'healthy'
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> bool:
        """Update performance monitoring thresholds"""
        try:
            for key, value in new_thresholds.items():
                if key in self.thresholds and isinstance(value, (int, float)):
                    self.thresholds[key] = float(value)
            
            logger.info(f"Updated performance thresholds: {new_thresholds}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating thresholds: {e}")
            return False
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        if resolved is None:
            return self.alerts
        
        return [
            alert for alert in self.alerts 
            if alert.get('resolved', False) == resolved
        ]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                logger.info(f"Resolved alert: {alert_id}")
                return True
        
        return False


# Global performance analytics service
performance_analytics = PerformanceAnalyticsService()


def get_performance_analytics() -> PerformanceAnalyticsService:
    """Get the global performance analytics service"""
    return performance_analytics


def monitor_endpoint_performance(endpoint_name: str = None):
    """Decorator to monitor specific endpoint performance"""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance for analysis
                logger.info(f"Endpoint {endpoint} executed in {duration:.3f}s")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.warning(f"Endpoint {endpoint} failed after {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator
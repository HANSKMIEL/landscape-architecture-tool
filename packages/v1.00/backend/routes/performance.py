"""
Performance monitoring and optimization routes.
Provides endpoints for monitoring cache performance and system health.
"""

from flask import Blueprint, current_app, jsonify, request

from src.routes.user import data_access_required, login_required
from src.services.performance import (
    cache,
    get_cache_stats,
    invalidate_dashboard_cache,
    invalidate_plant_cache,
    invalidate_project_cache,
)

performance_bp = Blueprint("performance", __name__, url_prefix="/api/performance")


@performance_bp.route("/stats", methods=["GET"])
@login_required
def get_performance_stats():
    """Get comprehensive performance statistics."""
    try:
        stats = {"cache": get_cache_stats(), "status": "healthy"}
        return jsonify(stats)
    except Exception:
        current_app.logger.exception("Failed to get performance stats")
        return jsonify({"error": "Failed to get performance stats"}), 500


@performance_bp.route("/cache/stats", methods=["GET"])
def get_cache_statistics():
    """Get detailed cache statistics."""
    try:
        return jsonify(get_cache_stats())
    except Exception:
        current_app.logger.exception("Failed to get cache stats")
        return jsonify({"error": "Failed to get cache stats"}), 500


@performance_bp.route("/cache/clear", methods=["POST"])
@data_access_required
def clear_cache():
    """Clear all cache entries."""
    try:
        success = cache.clear()
        if success:
            return jsonify({"message": "Cache cleared successfully", "success": True})
        return jsonify({"error": "Failed to clear cache", "success": False}), 500
    except Exception:
        current_app.logger.exception("Failed to clear cache")
        return jsonify({"error": "Failed to clear cache"}), 500


@performance_bp.route("/cache/invalidate", methods=["POST"])
@data_access_required
def invalidate_cache():
    """Invalidate specific cache patterns."""
    try:
        # Handle both JSON and form data requests
        data = request.get_json() or {} if request.is_json else request.form.to_dict() or {}
        cache_type = data.get("type", "all")

        if cache_type == "dashboard":
            invalidate_dashboard_cache()
            message = "Dashboard cache invalidated"
        elif cache_type == "plants":
            invalidate_plant_cache()
            message = "Plant cache invalidated"
        elif cache_type == "projects":
            invalidate_project_cache()
            message = "Project cache invalidated"
        elif cache_type == "all":
            invalidate_dashboard_cache()
            invalidate_plant_cache()
            invalidate_project_cache()
            message = "All cache invalidated"
        else:
            return (
                jsonify({"error": ("Invalid cache type. Use: dashboard, plants, " "projects, or all")}),
                400,
            )

        return jsonify({"message": message, "success": True})
    except Exception:
        current_app.logger.exception("Failed to invalidate cache")
        return jsonify({"error": "Failed to invalidate cache"}), 500


@performance_bp.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    try:
        cache_stats = get_cache_stats()
        health_score = 100  # Start with perfect score

        # Reduce score based on cache availability
        if not cache_stats.get("redis_available"):
            health_score -= 20

        # Calculate health based on cache hit rate if available
        hit_rate = cache_stats.get("cache_hit_rate", 0)
        if hit_rate < 50:
            health_score -= 30
        elif hit_rate < 70:
            health_score -= 15

        status = "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy"

        return jsonify(
            {
                "status": status,
                "health_score": health_score,
                "cache_stats": cache_stats,
                "timestamp": cache_stats.get("timestamp", "unknown"),
            }
        )
    except Exception:
        current_app.logger.exception("Health check failed")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "health_score": 0,
                    "error": "Internal server error",
                }
            ),
            500,
        )


@performance_bp.route("/metrics", methods=["GET"])
def get_performance_metrics():
    """Get detailed performance metrics."""
    try:
        cache_stats = get_cache_stats()

        metrics = {
            "cache": {
                "backend": cache_stats.get("cache_backend", "Unknown"),
                "redis_available": cache_stats.get("redis_available", False),
                "memory_cache_size": cache_stats.get("memory_cache_size", 0),
                "hit_rate": cache_stats.get("cache_hit_rate", 0),
                "redis_memory": cache_stats.get("redis_used_memory", "Unknown"),
            },
            "recommendations": [],
        }

        # Add performance recommendations
        if not cache_stats.get("redis_available"):
            metrics["recommendations"].append(
                {
                    "type": "warning",
                    "message": "Redis cache not available, using memory fallback",
                    "impact": "Performance may be reduced in production",
                }
            )

        hit_rate = cache_stats.get("cache_hit_rate", 0)
        if hit_rate < 50:
            metrics["recommendations"].append(
                {
                    "type": "critical",
                    "message": f"Low cache hit rate: {hit_rate}%",
                    "impact": "Consider adjusting cache timeouts or warming cache",
                }
            )
        elif hit_rate > 90:
            metrics["recommendations"].append(
                {
                    "type": "success",
                    "message": f"Excellent cache hit rate: {hit_rate}%",
                    "impact": "Cache is performing optimally",
                }
            )

        return jsonify(metrics)
    except Exception:
        current_app.logger.exception("Failed to get performance metrics")
        return jsonify({"error": "Failed to get performance metrics"}), 500

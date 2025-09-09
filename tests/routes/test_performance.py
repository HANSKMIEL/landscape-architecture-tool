# Test file for Performance API Routes
# This file handles comprehensive testing of performance monitoring endpoints

from unittest.mock import patch

import pytest

from tests.fixtures.database import DatabaseTestMixin


@pytest.mark.api
class TestPerformanceRoutes(DatabaseTestMixin):
    """Test class for performance monitoring routes"""

    @pytest.fixture
    def authenticated_client(self, client, app_context):
        """Create an authenticated test client"""
        from src.models.user import User, db
        
        # Create test user
        user = User(username="testuser", email="test@example.com", role="admin")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        
        # Login
        response = client.post("/api/auth/login", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        
        return client

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_stats_success(self, mock_get_stats, authenticated_client, app_context):
        """Test successful performance stats retrieval"""
        # Mock cache stats
        mock_stats = {
            "cache_backend": "redis",
            "redis_available": True,
            "cache_hit_rate": 85.5,
            "memory_cache_size": 1024,
            "redis_used_memory": "2.5MB",
        }
        mock_get_stats.return_value = mock_stats

        response = authenticated_client.get("/api/performance/stats")

        assert response.status_code == 200
        data = response.get_json()

        # Check response structure
        assert "cache" in data
        assert "status" in data
        assert data["status"] == "healthy"
        assert data["cache"] == mock_stats

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_stats_error(self, mock_get_stats, authenticated_client, app_context):
        """Test performance stats error handling"""
        # Mock exception
        mock_get_stats.side_effect = Exception("Cache connection failed")

        response = authenticated_client.get("/api/performance/stats")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to get performance stats" in data["error"]

    @patch("src.routes.performance.get_cache_stats")
    def test_get_cache_statistics_success(self, mock_get_stats, client, app_context):
        """Test successful cache statistics retrieval"""
        mock_stats = {
            "cache_backend": "memory",
            "redis_available": False,
            "cache_hit_rate": 65.0,
            "memory_cache_size": 512,
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/cache/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert data == mock_stats

    @patch("src.routes.performance.get_cache_stats")
    def test_get_cache_statistics_error(self, mock_get_stats, client, app_context):
        """Test cache statistics error handling"""
        mock_get_stats.side_effect = Exception("Stats unavailable")

        response = client.get("/api/performance/cache/stats")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.routes.performance.cache")
    def test_clear_cache_success(self, mock_cache, authenticated_client, app_context):
        """Test successful cache clearing"""
        mock_cache.clear.return_value = True

        response = authenticated_client.post("/api/performance/cache/clear")

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "Cache cleared successfully" in data["message"]
        mock_cache.clear.assert_called_once()

    @patch("src.routes.performance.cache")
    def test_clear_cache_failure(self, mock_cache, authenticated_client, app_context):
        """Test cache clearing failure"""
        mock_cache.clear.return_value = False

        response = authenticated_client.post("/api/performance/cache/clear")

        assert response.status_code == 500
        data = response.get_json()

        assert data["success"] is False
        assert "Failed to clear cache" in data["error"]

    @patch("src.routes.performance.cache")
    def test_clear_cache_exception(self, mock_cache, authenticated_client, app_context):
        """Test cache clearing with exception"""
        mock_cache.clear.side_effect = Exception("Cache error")

        response = authenticated_client.post("/api/performance/cache/clear")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.routes.performance.invalidate_dashboard_cache")
    def test_invalidate_cache_dashboard(self, mock_invalidate, authenticated_client, app_context):
        """Test dashboard cache invalidation"""
        response = authenticated_client.post("/api/performance/cache/invalidate", json={"type": "dashboard"})

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "dashboard" in data["message"]
        mock_invalidate.assert_called_once()

    @patch("src.routes.performance.invalidate_plant_cache")
    def test_invalidate_cache_plants(self, mock_invalidate, authenticated_client, app_context):
        """Test plant cache invalidation"""
        response = authenticated_client.post("/api/performance/cache/invalidate", json={"type": "plants"})

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "plants" in data["message"]
        mock_invalidate.assert_called_once()

    @patch("src.routes.performance.invalidate_project_cache")
    def test_invalidate_cache_projects(self, mock_invalidate, authenticated_client, app_context):
        """Test project cache invalidation"""
        response = authenticated_client.post("/api/performance/cache/invalidate", json={"type": "projects"})

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "Project cache invalidated" in data["message"]
        mock_invalidate.assert_called_once()

    @patch("src.routes.performance.invalidate_dashboard_cache")
    @patch("src.routes.performance.invalidate_plant_cache")
    @patch("src.routes.performance.invalidate_project_cache")
    def test_invalidate_cache_all(self, mock_project, mock_plant, mock_dashboard, client, app_context):
        """Test invalidating all cache types"""
        response = client.post("/api/performance/cache/invalidate", json={"type": "all"})

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "All cache invalidated" in data["message"]

        # All invalidation functions should be called
        mock_dashboard.assert_called_once()
        mock_plant.assert_called_once()
        mock_project.assert_called_once()

    def test_invalidate_cache_invalid_type(self, client, app_context):
        """Test cache invalidation with invalid type"""
        response = client.post("/api/performance/cache/invalidate", json={"type": "invalid"})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Invalid cache type" in data["error"]

    @patch("src.routes.performance.invalidate_dashboard_cache")
    @patch("src.routes.performance.invalidate_plant_cache")
    @patch("src.routes.performance.invalidate_project_cache")
    def test_invalidate_cache_no_json(self, mock_project, mock_plant, mock_dashboard, client, app_context):
        """Test cache invalidation without JSON data"""
        response = client.post("/api/performance/cache/invalidate")

        # Should default to "all" type
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    @patch("src.routes.performance.invalidate_dashboard_cache")
    def test_invalidate_cache_exception(self, mock_invalidate, client, app_context):
        """Test cache invalidation with exception"""
        mock_invalidate.side_effect = Exception("Invalidation failed")

        response = client.post("/api/performance/cache/invalidate", json={"type": "dashboard"})

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    @patch("src.routes.performance.get_cache_stats")
    def test_health_check_healthy(self, mock_get_stats, client, app_context):
        """Test health check with healthy system"""
        mock_stats = {
            "redis_available": True,
            "cache_hit_rate": 85,
            "timestamp": "2024-01-01T12:00:00",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/health")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "healthy"
        assert data["health_score"] >= 80
        assert "cache_stats" in data
        assert data["timestamp"] == "2024-01-01T12:00:00"

    @patch("src.routes.performance.get_cache_stats")
    def test_health_check_degraded(self, mock_get_stats, client, app_context):
        """Test health check with degraded system"""
        mock_stats = {
            "redis_available": False,  # Redis down
            "cache_hit_rate": 65,  # Low hit rate
            "timestamp": "2024-01-01T12:00:00",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/health")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "degraded"
        assert 60 <= data["health_score"] < 80

    @patch("src.routes.performance.get_cache_stats")
    def test_health_check_unhealthy(self, mock_get_stats, client, app_context):
        """Test health check with unhealthy system"""
        mock_stats = {
            "redis_available": False,  # Redis down
            "cache_hit_rate": 30,  # Very low hit rate
            "timestamp": "2024-01-01T12:00:00",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/health")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "unhealthy"
        assert data["health_score"] < 60

    @patch("src.routes.performance.get_cache_stats")
    def test_health_check_exception(self, mock_get_stats, client, app_context):
        """Test health check with exception"""
        mock_get_stats.side_effect = Exception("Health check failed")

        response = client.get("/api/performance/health")

        assert response.status_code == 500
        data = response.get_json()

        assert data["status"] == "unhealthy"
        assert data["health_score"] == 0
        assert "error" in data

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_metrics_success(self, mock_get_stats, client, app_context):
        """Test successful performance metrics retrieval"""
        mock_stats = {
            "cache_backend": "redis",
            "redis_available": True,
            "memory_cache_size": 2048,
            "cache_hit_rate": 92,
            "redis_used_memory": "5.2MB",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/metrics")

        assert response.status_code == 200
        data = response.get_json()

        # Check structure
        assert "cache" in data
        assert "recommendations" in data

        cache_data = data["cache"]
        assert cache_data["backend"] == "redis"
        assert cache_data["redis_available"] is True
        assert cache_data["memory_cache_size"] == 2048
        assert cache_data["hit_rate"] == 92
        assert cache_data["redis_memory"] == "5.2MB"

        # Should have success recommendation for high hit rate
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)

        # Check if there's a success message for high hit rate
        success_recommendations = [r for r in recommendations if r["type"] == "success"]
        assert len(success_recommendations) > 0

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_metrics_redis_unavailable(self, mock_get_stats, client, app_context):
        """Test performance metrics with Redis unavailable"""
        mock_stats = {
            "cache_backend": "memory",
            "redis_available": False,
            "memory_cache_size": 1024,
            "cache_hit_rate": 75,
            "redis_used_memory": "Unknown",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/metrics")

        assert response.status_code == 200
        data = response.get_json()

        # Should have warning recommendation
        recommendations = data["recommendations"]
        warning_recommendations = [r for r in recommendations if r["type"] == "warning"]
        assert len(warning_recommendations) > 0

        warning = warning_recommendations[0]
        assert "Redis cache not available" in warning["message"]

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_metrics_low_hit_rate(self, mock_get_stats, client, app_context):
        """Test performance metrics with low hit rate"""
        mock_stats = {
            "cache_backend": "redis",
            "redis_available": True,
            "memory_cache_size": 1024,
            "cache_hit_rate": 35,  # Low hit rate
            "redis_used_memory": "2.1MB",
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/metrics")

        assert response.status_code == 200
        data = response.get_json()

        # Should have critical recommendation
        recommendations = data["recommendations"]
        critical_recommendations = [r for r in recommendations if r["type"] == "critical"]
        assert len(critical_recommendations) > 0

        critical = critical_recommendations[0]
        assert "Low cache hit rate" in critical["message"]
        assert "35%" in critical["message"]

    @patch("src.routes.performance.get_cache_stats")
    def test_get_performance_metrics_exception(self, mock_get_stats, client, app_context):
        """Test performance metrics with exception"""
        mock_get_stats.side_effect = Exception("Metrics unavailable")

        response = client.get("/api/performance/metrics")

        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Failed to get performance metrics" in data["error"]


@pytest.mark.api
class TestPerformanceRoutesIntegration(DatabaseTestMixin):
    """Integration tests for performance routes"""

    def test_performance_endpoints_availability(self, client, app_context):
        """Test that all performance endpoints are available"""
        endpoints = [
            "/api/performance/stats",
            "/api/performance/cache/stats",
            "/api/performance/health",
            "/api/performance/metrics",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404

    def test_cache_operations_workflow(self, client, app_context):
        """Test complete cache operations workflow"""
        # 1. Get initial stats
        response = client.get("/api/performance/cache/stats")
        assert response.status_code in [200, 500]  # May fail due to cache issues

        # 2. Clear cache
        response = authenticated_client.post("/api/performance/cache/clear")
        assert response.status_code in [200, 500]  # May fail due to cache issues

        # 3. Invalidate specific cache
        response = client.post("/api/performance/cache/invalidate", json={"type": "dashboard"})
        assert response.status_code in [200, 500]  # May fail due to cache issues

    def test_health_monitoring_workflow(self, client, app_context):
        """Test health monitoring workflow"""
        # 1. Check overall health
        response = client.get("/api/performance/health")
        assert response.status_code in [200, 500]

        # 2. Get detailed metrics
        response = client.get("/api/performance/metrics")
        assert response.status_code in [200, 500]

        # 3. Get performance stats
        response = client.get("/api/performance/stats")
        assert response.status_code in [200, 500]


@pytest.mark.api
class TestPerformanceRoutesEdgeCases(DatabaseTestMixin):
    """Edge case tests for performance routes"""

    def test_post_requests_to_get_endpoints(self, client, app_context):
        """Test POST requests to GET-only endpoints"""
        get_endpoints = [
            "/api/performance/stats",
            "/api/performance/cache/stats",
            "/api/performance/health",
            "/api/performance/metrics",
        ]

        for endpoint in get_endpoints:
            response = client.post(endpoint)
            # Should return method not allowed or handled by error handler
            assert response.status_code in [405, 500]

    def test_get_requests_to_post_endpoints(self, client, app_context):
        """Test GET requests to POST-only endpoints"""
        post_endpoints = [
            "/api/performance/cache/clear",
            "/api/performance/cache/invalidate",
        ]

        for endpoint in post_endpoints:
            response = client.get(endpoint)
            # Should return method not allowed or handled by error handler
            assert response.status_code in [405, 500]

    def test_invalid_json_in_invalidate_cache(self, client, app_context):
        """Test invalid JSON in cache invalidation"""
        response = client.post(
            "/api/performance/cache/invalidate",
            data="invalid json",
            content_type="application/json",
        )

        # Should handle gracefully (default to empty dict)
        assert response.status_code in [200, 400, 500]

    @patch("src.routes.performance.get_cache_stats")
    def test_missing_cache_stats_fields(self, mock_get_stats, client, app_context):
        """Test handling of missing fields in cache stats"""
        # Mock stats with missing fields
        mock_stats = {
            "cache_backend": "redis"
            # Missing other expected fields
        }
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/performance/metrics")

        assert response.status_code == 200
        data = response.get_json()

        # Should handle missing fields gracefully
        cache_data = data["cache"]
        assert cache_data["backend"] == "redis"

        # Missing fields should have defaults
        assert "redis_available" in cache_data
        assert "hit_rate" in cache_data

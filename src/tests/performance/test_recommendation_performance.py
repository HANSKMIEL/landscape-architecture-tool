import pytest
import time
import statistics
from src.services.recommendation_service import RecommendationService
from src.tests.database.factories import create_test_plant

class TestRecommendationPerformance:
    
    @pytest.fixture
    def large_plant_dataset(self, db_session):
        """Create large dataset for performance testing"""
        plants = []
        plant_types = ['tree', 'shrub', 'perennial', 'annual']
        sun_requirements = ['full_sun', 'partial_shade', 'full_shade']
        soil_types = ['well_drained', 'moist', 'wet', 'dry']
        
        for i in range(1000):
            plant = create_test_plant(
                name=f'Plant {i}',
                plant_type=plant_types[i % len(plant_types)],
                sun_requirements=sun_requirements[i % len(sun_requirements)],
                soil_type=soil_types[i % len(soil_types)]
            )
            plants.append(plant)
            db_session.add(plant)
        
        db_session.commit()
        return plants
    
    def test_recommendation_speed_benchmark(self, large_plant_dataset):
        """Benchmark recommendation generation speed"""
        service = RecommendationService()
        criteria = {
            'sun_requirements': 'full_sun',
            'plant_type': 'shrub',
            'height_range': [50, 200]
        }
        
        # Warm up
        service.get_recommendations(criteria)
        
        # Benchmark multiple runs
        times = []
        for _ in range(10):
            start_time = time.time()
            recommendations = service.get_recommendations(criteria)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Performance assertions
        assert avg_time < 1.0, f"Average recommendation time {avg_time:.3f}s exceeds 1s"
        assert max_time < 2.0, f"Maximum recommendation time {max_time:.3f}s exceeds 2s"
        assert len(recommendations) > 0, "No recommendations returned"
    
    def test_memory_usage_stability(self, large_plant_dataset):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os
        
        service = RecommendationService()
        criteria = {
            'sun_requirements': 'full_sun',
            'plant_type': 'shrub'
        }
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run many recommendation requests
        for _ in range(50):
            service.get_recommendations(criteria)
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 50MB)
        assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.1f}MB"
    
    def test_concurrent_recommendation_requests(self, large_plant_dataset):
        """Test handling of concurrent recommendation requests"""
        # Note: Testing true concurrent database access is complex with Flask's app context
        # This test verifies that multiple sequential calls work correctly
        
        service = RecommendationService()
        criteria = {
            'sun_requirements': 'full_sun',
            'plant_type': 'shrub'
        }
        
        results = []
        
        # Make multiple sequential calls to simulate concurrent-like behavior
        for _ in range(10):
            start_time = time.time()
            recommendations = service.get_recommendations(criteria)
            end_time = time.time()
            results.append({
                'time': end_time - start_time,
                'count': len(recommendations)
            })
        
        # All requests should succeed
        assert len(results) == 10, "Not all requests completed"
        
        # Check performance consistency
        times = [result['time'] for result in results]
        avg_time = statistics.mean(times)
        assert avg_time < 2.0, f"Average request time {avg_time:.3f}s too high"
        
        # All requests should return the same number of results
        counts = [result['count'] for result in results]
        assert all(count == counts[0] for count in counts), "Inconsistent result counts"
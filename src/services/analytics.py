"""
Analytics and Reporting Service

Provides comprehensive analytics for projects, plants, clients,
and business intelligence reporting.
"""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import func

from src.models.landscape import (
    Client,
    Plant,
    PlantRecommendationRequest,
    Project,
    ProjectPlant,
)
from src.models.user import db


class AnalyticsService:
    """Service for generating analytics and reports"""

    def get_plant_usage_analytics(self, date_range: Optional[tuple] = None) -> Dict:
        """Get plant usage statistics and trends"""
        try:
            # Build date filter
            date_filter = []
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                if start_date:
                    date_filter.append(
                        Project.created_at >= datetime.fromisoformat(start_date)
                    )
                if end_date:
                    date_filter.append(
                        Project.created_at <= datetime.fromisoformat(end_date)
                    )

            # Most used plants by project count
            plant_usage = (
                db.session.query(
                    Plant.id,
                    Plant.name,
                    Plant.common_name,
                    Plant.category,
                    func.count(ProjectPlant.project_id.distinct()).label(
                        "project_count"
                    ),
                    func.sum(ProjectPlant.quantity).label("total_quantity"),
                    func.avg(ProjectPlant.unit_cost).label("avg_cost"),
                )
                .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
                .join(Project, ProjectPlant.project_id == Project.id)
                .filter(*date_filter)
                .group_by(Plant.id, Plant.name, Plant.common_name, Plant.category)
                .order_by(func.count(ProjectPlant.project_id.distinct()).desc())
                .limit(20)
                .all()
            )

            most_used_plants = [
                {
                    "id": plant_id,
                    "name": name,
                    "common_name": common_name,
                    "category": category,
                    "project_count": project_count,
                    "total_quantity": int(total_quantity) if total_quantity else 0,
                    "avg_cost": float(avg_cost) if avg_cost else 0,
                }
                for (
                    plant_id,
                    name,
                    common_name,
                    category,
                    project_count,
                    total_quantity,
                    avg_cost,
                ) in plant_usage
            ]

            # Category distribution
            category_stats = (
                db.session.query(
                    Plant.category,
                    func.count(ProjectPlant.project_id.distinct()).label(
                        "project_count"
                    ),
                    func.sum(ProjectPlant.quantity).label("total_quantity"),
                )
                .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
                .join(Project, ProjectPlant.project_id == Project.id)
                .filter(*date_filter)
                .filter(Plant.category.isnot(None))
                .group_by(Plant.category)
                .order_by(func.count(ProjectPlant.project_id.distinct()).desc())
                .all()
            )

            category_distribution = [
                {
                    "category": category,
                    "project_count": project_count,
                    "total_quantity": int(total_quantity) if total_quantity else 0,
                }
                for category, project_count, total_quantity in category_stats
            ]

            # Usage trends over time
            usage_trends = (
                db.session.query(
                    func.strftime("%Y-%m", Project.created_at).label("month"),
                    func.count(ProjectPlant.id.distinct()).label("plant_selections"),
                    func.sum(ProjectPlant.quantity).label("total_quantity"),
                )
                .join(ProjectPlant, Project.id == ProjectPlant.project_id)
                .filter(*date_filter)
                .group_by(func.strftime("%Y-%m", Project.created_at))
                .order_by(func.strftime("%Y-%m", Project.created_at))
                .all()
            )

            trends = [
                {
                    "month": month if month else "",
                    "plant_selections": plant_selections,
                    "total_quantity": int(total_quantity) if total_quantity else 0,
                }
                for month, plant_selections, total_quantity in usage_trends
            ]

            # Total statistics
            total_plants_used = db.session.query(func.sum(ProjectPlant.quantity)).filter(*date_filter).scalar() or 0
            total_projects_with_plants = db.session.query(func.count(func.distinct(ProjectPlant.project_id))).filter(*date_filter).scalar() or 0

            return {
                "most_used_plants": most_used_plants,
                "category_distribution": category_distribution,
                "usage_trends": trends,
                "total_unique_plants": len(most_used_plants),
                "total_plants_used": int(total_plants_used),
                "total_projects_with_plants": int(total_projects_with_plants),
                "analysis_period": date_range,
            }

        except Exception as e:
            return {
                "error": str(e),
                "most_used_plants": [],
                "category_distribution": [],
                "usage_trends": [],
                "total_unique_plants": 0,
                "total_plants_used": 0,
                "total_projects_with_plants": 0,
            }

    def get_project_performance_metrics(self, project_id: Optional[int] = None) -> Dict:
        """Get project performance and timeline analytics"""
        try:
            query = db.session.query(Project)
            if project_id:
                query = query.filter(Project.id == project_id)

            projects = query.all()

            # Status distribution
            status_stats = (
                db.session.query(Project.status, func.count(Project.id).label("count"))
                .group_by(Project.status)
                .all()
            )

            status_distribution = {status: count for status, count in status_stats}

            # Budget analysis
            budget_stats = (
                db.session.query(
                    func.sum(Project.budget).label("total_budget"),
                    func.avg(Project.budget).label("avg_budget"),
                    func.min(Project.budget).label("min_budget"),
                    func.max(Project.budget).label("max_budget"),
                    func.count(Project.id).label("project_count"),
                )
                .filter(Project.budget.isnot(None))
                .first()
            )

            # Project timeline analysis
            timeline_stats = []
            for project in projects:
                start_date_val = project.start_date
                end_date_val = project.end_date or project.actual_completion_date
                
                if start_date_val and end_date_val:
                    try:
                        # Handle different date formats
                        if isinstance(start_date_val, str):
                            start = datetime.fromisoformat(start_date_val)
                        else:
                            start = start_date_val
                            
                        if isinstance(end_date_val, str):
                            end = datetime.fromisoformat(end_date_val)
                        else:
                            end = end_date_val
                            
                        # Convert to dates if they're datetimes
                        if hasattr(start, 'date'):
                            start = start.date() if hasattr(start, 'date') else start
                        if hasattr(end, 'date'):
                            end = end.date() if hasattr(end, 'date') else end
                            
                        duration = (end - start).days

                        timeline_stats.append(
                            {
                                "id": project.id,
                                "name": project.name,
                                "duration_days": duration,
                                "status": project.status,
                                "budget": (
                                    float(project.budget) if project.budget else 0
                                ),
                            }
                        )
                    except (ValueError, TypeError, AttributeError):
                        continue

            # Performance by project type
            type_performance = (
                db.session.query(
                    Project.project_type,
                    func.count(Project.id).label("count"),
                    func.avg(Project.budget).label("avg_budget"),
                )
                .filter(Project.project_type.isnot(None))
                .group_by(Project.project_type)
                .all()
            )

            type_stats = [
                {
                    "type": project_type,
                    "count": count,
                    "avg_budget": float(avg_budget) if avg_budget else 0,
                }
                for project_type, count, avg_budget in type_performance
            ]

            return {
                "status_distribution": status_distribution,
                "budget_analysis": {
                    "total_budget": (
                        float(budget_stats.total_budget)
                        if budget_stats.total_budget
                        else 0
                    ),
                    "avg_budget": (
                        float(budget_stats.avg_budget) if budget_stats.avg_budget else 0
                    ),
                    "min_budget": (
                        float(budget_stats.min_budget) if budget_stats.min_budget else 0
                    ),
                    "max_budget": (
                        float(budget_stats.max_budget) if budget_stats.max_budget else 0
                    ),
                    "project_count": (
                        budget_stats.project_count if budget_stats.project_count else 0
                    ),
                },
                "timeline_analysis": timeline_stats,
                "type_performance": type_stats,
            }

        except Exception as e:
            return {"error": str(e)}

    def get_client_relationship_insights(self) -> Dict:
        """Get client relationship and business analytics"""
        try:
            # Top clients by project count and value
            top_clients = (
                db.session.query(
                    Client.id,
                    Client.name,
                    Client.client_type,
                    func.count(Project.id).label("project_count"),
                    func.sum(Project.budget).label("total_value"),
                    func.avg(Project.budget).label("avg_project_value"),
                    func.max(Project.created_at).label("last_project_date"),
                )
                .outerjoin(Project)
                .group_by(Client.id, Client.name, Client.client_type)
                .order_by(func.count(Project.id).desc())
                .limit(20)
                .all()
            )

            client_analytics = [
                {
                    "id": client_id,
                    "name": name,
                    "client_type": client_type,
                    "project_count": project_count,
                    "total_value": float(total_value) if total_value else 0,
                    "avg_project_value": (
                        float(avg_project_value) if avg_project_value else 0
                    ),
                    "last_project_date": (
                        last_project_date.isoformat() if last_project_date else None
                    ),
                }
                for (
                    client_id,
                    name,
                    client_type,
                    project_count,
                    total_value,
                    avg_project_value,
                    last_project_date,
                ) in top_clients
            ]

            # Client type distribution
            type_distribution = (
                db.session.query(
                    Client.client_type, func.count(Client.id).label("count")
                )
                .filter(Client.client_type.isnot(None))
                .group_by(Client.client_type)
                .all()
            )

            client_type_stats = {
                client_type: count for client_type, count in type_distribution
            }

            # Geographic distribution
            geographic_distribution = (
                db.session.query(Client.city, func.count(Client.id).label("count"))
                .filter(Client.city.isnot(None))
                .group_by(Client.city)
                .order_by(func.count(Client.id).desc())
                .limit(10)
                .all()
            )

            geographic_stats = [
                {"city": city, "client_count": count}
                for city, count in geographic_distribution
            ]

            return {
                "top_clients": client_analytics,
                "client_type_distribution": client_type_stats,
                "geographic_distribution": geographic_stats,
                "total_clients": len(client_analytics),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_financial_reporting(self, date_range: tuple) -> Dict:
        """Get financial performance and budget analytics"""
        try:
            start_date, end_date = date_range

            # Build date filter
            date_filter = []
            if start_date:
                date_filter.append(
                    Project.created_at >= datetime.fromisoformat(start_date)
                )
            if end_date:
                date_filter.append(
                    Project.created_at <= datetime.fromisoformat(end_date)
                )

            # Revenue analytics
            revenue_stats = (
                db.session.query(
                    func.sum(Project.budget).label("total_revenue"),
                    func.count(Project.id).label("project_count"),
                    func.avg(Project.budget).label("avg_project_value"),
                )
                .filter(Project.budget.isnot(None))
                .filter(*date_filter)
                .first()
            )

            # Revenue by month
            monthly_revenue = (
                db.session.query(
                    func.strftime("%Y-%m", Project.created_at).label("month"),
                    func.sum(Project.budget).label("revenue"),
                    func.count(Project.id).label("project_count"),
                )
                .filter(Project.budget.isnot(None))
                .filter(*date_filter)
                .group_by(func.strftime("%Y-%m", Project.created_at))
                .order_by(func.strftime("%Y-%m", Project.created_at))
                .all()
            )

            revenue_trends = [
                {
                    "month": month if month else "",
                    "revenue": float(revenue) if revenue else 0,
                    "project_count": project_count,
                }
                for month, revenue, project_count in monthly_revenue
            ]

            # Cost analysis (from project plants)
            cost_analysis = (
                db.session.query(
                    func.sum(ProjectPlant.quantity * ProjectPlant.unit_cost).label(
                        "total_plant_costs"
                    )
                )
                .join(Project)
                .filter(*date_filter)
                .filter(ProjectPlant.unit_cost.isnot(None))
                .first()
            )

            # Profitability by project type
            profitability_by_type = (
                db.session.query(
                    Project.project_type,
                    func.sum(Project.budget).label("revenue"),
                    func.count(Project.id).label("project_count"),
                )
                .filter(Project.budget.isnot(None))
                .filter(Project.project_type.isnot(None))
                .filter(*date_filter)
                .group_by(Project.project_type)
                .all()
            )

            profitability_stats = [
                {
                    "project_type": project_type,
                    "revenue": float(revenue) if revenue else 0,
                    "project_count": project_count,
                    "avg_revenue": (
                        float(revenue / project_count)
                        if revenue and project_count > 0
                        else 0
                    ),
                }
                for project_type, revenue, project_count in profitability_by_type
            ]

            return {
                "revenue_summary": {
                    "total_revenue": (
                        float(revenue_stats.total_revenue)
                        if revenue_stats.total_revenue
                        else 0
                    ),
                    "project_count": (
                        revenue_stats.project_count
                        if revenue_stats.project_count
                        else 0
                    ),
                    "avg_project_value": (
                        float(revenue_stats.avg_project_value)
                        if revenue_stats.avg_project_value
                        else 0
                    ),
                },
                "revenue_trends": revenue_trends,
                "cost_analysis": {
                    "total_plant_costs": (
                        float(cost_analysis.total_plant_costs)
                        if cost_analysis.total_plant_costs
                        else 0
                    )
                },
                "profitability_by_type": profitability_stats,
                "analysis_period": {"start": start_date, "end": end_date},
            }

        except Exception as e:
            return {"error": str(e)}

    def get_recommendation_effectiveness(self) -> Dict:
        """Get plant recommendation system effectiveness metrics"""
        try:
            # Total recommendation requests
            total_requests = PlantRecommendationRequest.query.count()

            # Requests with feedback
            requests_with_feedback = PlantRecommendationRequest.query.filter(
                PlantRecommendationRequest.feedback_rating.isnot(None)
            ).count()

            # Average rating
            avg_rating = (
                db.session.query(func.avg(PlantRecommendationRequest.feedback_rating))
                .filter(PlantRecommendationRequest.feedback_rating.isnot(None))
                .scalar()
            )

            # Rating distribution
            rating_distribution = (
                db.session.query(
                    PlantRecommendationRequest.feedback_rating,
                    func.count(PlantRecommendationRequest.id).label("count"),
                )
                .filter(PlantRecommendationRequest.feedback_rating.isnot(None))
                .group_by(PlantRecommendationRequest.feedback_rating)
                .all()
            )

            rating_stats = {rating: count for rating, count in rating_distribution}

            # Popular criteria
            popular_criteria = (
                db.session.query(
                    PlantRecommendationRequest.project_type,
                    func.count(PlantRecommendationRequest.id).label("count"),
                )
                .filter(PlantRecommendationRequest.project_type.isnot(None))
                .group_by(PlantRecommendationRequest.project_type)
                .order_by(func.count(PlantRecommendationRequest.id).desc())
                .limit(10)
                .all()
            )

            criteria_stats = [
                {"project_type": project_type, "request_count": count}
                for project_type, count in popular_criteria
            ]

            # Usage trends
            usage_trends = (
                db.session.query(
                    func.strftime("%Y-%m", PlantRecommendationRequest.created_at).label(
                        "month"
                    ),
                    func.count(PlantRecommendationRequest.id).label("request_count"),
                )
                .group_by(func.strftime("%Y-%m", PlantRecommendationRequest.created_at))
                .order_by(func.strftime("%Y-%m", PlantRecommendationRequest.created_at))
                .all()
            )

            trends = [
                {"month": month if month else "", "request_count": request_count}
                for month, request_count in usage_trends
            ]

            return {
                "total_requests": total_requests,
                "requests_with_feedback": requests_with_feedback,
                "feedback_rate": (
                    (requests_with_feedback / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
                "average_rating": float(avg_rating) if avg_rating else 0,
                "rating_distribution": rating_stats,
                "popular_criteria": criteria_stats,
                "usage_trends": trends,
            }

        except Exception as e:
            return {"error": str(e)}

    def get_project_performance_analytics(self, project_id: Optional[int] = None) -> Dict:
        """Get project performance analytics (alias for compatibility)"""
        result = self.get_project_performance_metrics(project_id)
        
        # Adapt the result to match test expectations
        if "error" in result:
            return {
                "total_projects": 0,
                "completion_rate": 0,
                "average_duration": 0,
                "projects_by_status": {},
                "error": result["error"]
            }
        
        status_dist = result.get("status_distribution", {})
        timeline_analysis = result.get("timeline_analysis", [])
        
        # Calculate completion rate
        total_projects = sum(status_dist.values())
        completed_projects = status_dist.get("completed", 0)
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        
        # Calculate average duration from timeline analysis
        durations = [p["duration_days"] for p in timeline_analysis if p.get("duration_days", 0) > 0]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_projects": total_projects,
            "completion_rate": completion_rate,
            "average_duration": average_duration,
            "projects_by_status": status_dist,
            "timeline_analysis": timeline_analysis,
            "total_budget": result.get("budget_analysis", {}).get("total_budget", 0),
            "average_budget": result.get("budget_analysis", {}).get("avg_budget", 0)
        }

    def get_client_analytics(self) -> Dict:
        """Get client analytics"""
        try:
            insights = self.get_client_relationship_insights()
            
            if "error" in insights:
                return {
                    "total_clients": 0,
                    "top_clients_by_projects": [],
                    "top_clients_by_budget": [],
                    "client_distribution": {},
                    "error": insights["error"]
                }
            
            top_clients = insights.get("top_clients", [])
            
            # Sort by project count for top_clients_by_projects
            top_by_projects = sorted(top_clients, key=lambda x: x["project_count"], reverse=True)[:10]
            
            # Sort by total value for top_clients_by_budget  
            top_by_budget = sorted(top_clients, key=lambda x: x["total_value"], reverse=True)[:10]
            
            return {
                "total_clients": insights.get("total_clients", 0),
                "top_clients_by_projects": top_by_projects,
                "top_clients_by_budget": top_by_budget,
                "client_distribution": insights.get("client_type_distribution", {}),
                "geographic_distribution": insights.get("geographic_distribution", [])
            }
            
        except Exception as e:
            return {
                "total_clients": 0,
                "top_clients_by_projects": [],
                "top_clients_by_budget": [],
                "client_distribution": {},
                "error": str(e)
            }

    def get_recommendation_analytics(self) -> Dict:
        """Get recommendation analytics (alias for compatibility)"""
        try:
            result = self.get_recommendation_effectiveness()
            
            if "error" in result:
                return {
                    "total_requests": 0,
                    "feedback_rate": 0,
                    "average_satisfaction": 0,
                    "popular_criteria": [],
                    "error": result["error"]
                }
                
            return {
                "total_requests": result.get("total_requests", 0),
                "feedback_rate": result.get("feedback_rate", 0),
                "average_satisfaction": result.get("average_rating", 0),
                "popular_criteria": result.get("popular_criteria", []),
                "usage_trends": result.get("usage_trends", []),
                "rating_distribution": result.get("rating_distribution", {})
            }
            
        except Exception as e:
            return {
                "total_requests": 0,
                "feedback_rate": 0,
                "average_satisfaction": 0,
                "popular_criteria": [],
                "error": str(e)
            }

    def get_seasonal_analytics(self) -> Dict:
        """Get seasonal analytics"""
        try:
            # Projects by month
            projects_by_month = (
                db.session.query(
                    func.strftime("%Y-%m", Project.created_at).label("month"),
                    func.count(Project.id).label("project_count")
                )
                .group_by(func.strftime("%Y-%m", Project.created_at))
                .order_by(func.strftime("%Y-%m", Project.created_at))
                .all()
            )
            
            monthly_data = [
                {"month": month if month else "", "project_count": project_count}
                for month, project_count in projects_by_month
            ]
            
            # Plant usage by season (based on bloom_time)
            seasonal_usage = (
                db.session.query(
                    Plant.bloom_time,
                    func.count(ProjectPlant.id).label("usage_count"),
                    func.sum(ProjectPlant.quantity).label("total_quantity")
                )
                .join(ProjectPlant, Plant.id == ProjectPlant.plant_id)
                .filter(Plant.bloom_time.isnot(None))
                .group_by(Plant.bloom_time)
                .all()
            )
            
            plant_usage_by_season = {
                bloom_time: {
                    "usage_count": usage_count,
                    "total_quantity": int(total_quantity) if total_quantity else 0
                }
                for bloom_time, usage_count, total_quantity in seasonal_usage
            }
            
            # Identify peak seasons (months with most projects)
            peak_seasons = sorted(monthly_data, key=lambda x: x["project_count"], reverse=True)[:3]
            
            return {
                "projects_by_month": monthly_data,
                "plant_usage_by_season": plant_usage_by_season,
                "peak_seasons": [season["month"] for season in peak_seasons]
            }
            
        except Exception as e:
            return {
                "projects_by_month": [],
                "plant_usage_by_season": {},
                "peak_seasons": [],
                "error": str(e)
            }

    def get_geographic_analytics(self) -> Dict:
        """Get geographic analytics"""
        try:
            # Projects by location
            projects_by_location = (
                db.session.query(
                    Project.location,
                    func.count(Project.id).label("project_count"),
                    func.sum(Project.budget).label("total_budget")
                )
                .filter(Project.location.isnot(None))
                .group_by(Project.location)
                .order_by(func.count(Project.id).desc())
                .limit(20)
                .all()
            )
            
            location_data = [
                {
                    "location": location,
                    "project_count": project_count,
                    "total_budget": float(total_budget) if total_budget else 0
                }
                for location, project_count, total_budget in projects_by_location
            ]
            
            # Regional plant preferences (by client city)
            regional_preferences = (
                db.session.query(
                    Client.city,
                    Plant.category,
                    func.count(ProjectPlant.id).label("usage_count")
                )
                .join(Project, Client.id == Project.client_id)
                .join(ProjectPlant, Project.id == ProjectPlant.project_id)
                .join(Plant, ProjectPlant.plant_id == Plant.id)
                .filter(Client.city.isnot(None))
                .filter(Plant.category.isnot(None))
                .group_by(Client.city, Plant.category)
                .all()
            )
            
            regional_plant_preferences = {}
            for city, category, usage_count in regional_preferences:
                if city not in regional_plant_preferences:
                    regional_plant_preferences[city] = {}
                regional_plant_preferences[city][category] = usage_count
            
            # Coverage areas (unique cities with projects)
            coverage_areas = (
                db.session.query(Client.city)
                .join(Project)
                .filter(Client.city.isnot(None))
                .distinct()
                .all()
            )
            
            coverage_list = [city[0] for city in coverage_areas]
            
            return {
                "projects_by_location": location_data,
                "regional_plant_preferences": regional_plant_preferences,
                "coverage_areas": coverage_list
            }
            
        except Exception as e:
            return {
                "projects_by_location": [],
                "regional_plant_preferences": {},
                "coverage_areas": [],
                "error": str(e)
            }

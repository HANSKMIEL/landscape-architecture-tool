"""
Analytics and Reporting Service

Provides comprehensive analytics for projects, plants, clients,
and business intelligence reporting.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, text
from src.models.landscape import Project, Plant, Client, PlantRecommendationRequest, Product, project_plants, project_products, db


class AnalyticsService:
    """Service for generating analytics and reports"""
    
    def _get_month_format(self, date_column):
        """Get database-compatible month formatting"""
        # For SQLite, use strftime; for PostgreSQL, use date_trunc
        return func.strftime('%Y-%m', date_column)
    
    def get_plant_usage_analytics(self, date_range: Optional[tuple] = None) -> Dict:
        """Get plant usage statistics and trends"""
        try:
            # Build date filter
            date_filter = []
            if date_range and date_range[0]:
                date_filter.append(Project.created_at >= datetime.fromisoformat(date_range[0]))
            if date_range and date_range[1]:
                date_filter.append(Project.created_at <= datetime.fromisoformat(date_range[1]))

            # Most popular plants by project count
            popular_plants = (
                db.session.query(
                    Plant.name,
                    Plant.common_name,
                    Plant.category,
                    func.count(Project.id.distinct()).label('project_count'),
                    func.sum(func.coalesce(project_plants.c.quantity, 1)).label('total_quantity')
                )
                .join(project_plants, Plant.id == project_plants.c.plant_id)
                .join(Project, Project.id == project_plants.c.project_id)
                .filter(*date_filter)
                .group_by(Plant.id, Plant.name, Plant.common_name, Plant.category)
                .order_by(func.count(Project.id.distinct()).desc())
                .limit(10)
                .all()
            )

            # Plant category distribution
            category_distribution = (
                db.session.query(
                    Plant.category,
                    func.count(Project.id.distinct()).label('project_count'),
                    func.sum(func.coalesce(project_plants.c.quantity, 1)).label('total_quantity')
                )
                .join(project_plants, Plant.id == project_plants.c.plant_id)
                .join(Project, Project.id == project_plants.c.project_id)
                .filter(*date_filter)
                .filter(Plant.category.isnot(None))
                .group_by(Plant.category)
                .order_by(func.count(Project.id.distinct()).desc())
                .all()
            )

            # Plant usage trends over time (monthly)
            usage_trends = (
                db.session.query(
                    self._get_month_format(Project.created_at).label('month'),
                    func.count(Project.id.distinct()).label('projects_with_plants'),
                    func.sum(func.coalesce(project_plants.c.quantity, 1)).label('total_plants_used')
                )
                .join(project_plants, Project.id == project_plants.c.project_id)
                .filter(*date_filter)
                .group_by(self._get_month_format(Project.created_at))
                .order_by(self._get_month_format(Project.created_at))
                .all()
            )

            # Native vs non-native usage
            native_usage = (
                db.session.query(
                    Plant.native,
                    func.count(Project.id.distinct()).label('project_count'),
                    func.sum(func.coalesce(project_plants.c.quantity, 1)).label('total_quantity')
                )
                .join(project_plants, Plant.id == project_plants.c.plant_id)
                .join(Project, Project.id == project_plants.c.project_id)
                .filter(*date_filter)
                .group_by(Plant.native)
                .all()
            )

            return {
                'popular_plants': [
                    {
                        'name': name,
                        'common_name': common_name,
                        'category': category,
                        'project_count': project_count,
                        'total_quantity': total_quantity or 0
                    }
                    for name, common_name, category, project_count, total_quantity in popular_plants
                ],
                'category_distribution': [
                    {
                        'category': category,
                        'project_count': project_count,
                        'total_quantity': total_quantity or 0
                    }
                    for category, project_count, total_quantity in category_distribution
                ],
                'usage_trends': [
                    {
                        'month': month if month else '',
                        'projects_with_plants': projects_with_plants,
                        'total_plants_used': total_plants_used or 0
                    }
                    for month, projects_with_plants, total_plants_used in usage_trends
                ],
                'native_vs_non_native': [
                    {
                        'type': 'Native' if native else 'Non-native',
                        'project_count': project_count,
                        'total_quantity': total_quantity or 0
                    }
                    for native, project_count, total_quantity in native_usage
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_project_performance_metrics(self, project_id: Optional[int] = None) -> Dict:
        """Get project performance and timeline analytics"""
        try:
            # Build query
            query = Project.query
            if project_id:
                query = query.filter(Project.id == project_id)

            projects = query.all()

            # Project status distribution
            status_distribution = (
                db.session.query(
                    Project.status,
                    func.count(Project.id).label('count')
                )
                .group_by(Project.status)
                .all()
            )

            # Average project duration (for completed projects) - simplified for SQLite
            completed_projects = (
                db.session.query(Project)
                .filter(
                    and_(
                        Project.start_date.isnot(None),
                        Project.end_date.isnot(None),
                        Project.status == 'Afgerond'
                    )
                )
                .all()
            )
            
            avg_duration = 0
            if completed_projects:
                total_days = 0
                count = 0
                for project in completed_projects:
                    try:
                        start = datetime.fromisoformat(project.start_date)
                        end = datetime.fromisoformat(project.end_date)
                        days = (end - start).days
                        total_days += days
                        count += 1
                    except:
                        continue
                avg_duration = total_days / count if count > 0 else 0

            # Budget performance
            budget_performance = (
                db.session.query(
                    func.count(Project.id).label('total_projects'),
                    func.sum(Project.budget).label('total_budget'),
                    func.avg(Project.budget).label('avg_budget'),
                    func.avg(Project.area_size).label('avg_area_size')
                )
                .filter(Project.budget.isnot(None))
                .first()
            )

            # Project type distribution
            type_distribution = (
                db.session.query(
                    Project.project_type,
                    func.count(Project.id).label('count'),
                    func.avg(Project.budget).label('avg_budget')
                )
                .filter(Project.project_type.isnot(None))
                .group_by(Project.project_type)
                .all()
            )

            # Monthly project creation trends
            creation_trends = (
                db.session.query(
                    self._get_month_format(Project.created_at).label('month'),
                    func.count(Project.id).label('projects_created')
                )
                .group_by(self._get_month_format(Project.created_at))
                .order_by(self._get_month_format(Project.created_at))
                .all()
            )

            return {
                'status_distribution': [
                    {'status': status, 'count': count}
                    for status, count in status_distribution
                ],
                'avg_duration_days': float(avg_duration) if avg_duration else 0,
                'budget_performance': {
                    'total_projects': budget_performance.total_projects if budget_performance else 0,
                    'total_budget': float(budget_performance.total_budget) if budget_performance and budget_performance.total_budget else 0,
                    'avg_budget': float(budget_performance.avg_budget) if budget_performance and budget_performance.avg_budget else 0,
                    'avg_area_size': float(budget_performance.avg_area_size) if budget_performance and budget_performance.avg_area_size else 0
                },
                'type_distribution': [
                    {
                        'project_type': project_type,
                        'count': count,
                        'avg_budget': float(avg_budget) if avg_budget else 0
                    }
                    for project_type, count, avg_budget in type_distribution
                ],
                'creation_trends': [
                    {
                        'month': month if month else '',
                        'projects_created': projects_created
                    }
                    for month, projects_created in creation_trends
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_client_relationship_insights(self) -> Dict:
        """Get client relationship and business analytics"""
        try:
            # Top clients by project count
            top_clients_by_projects = (
                db.session.query(
                    Client.name,
                    Client.client_type,
                    func.count(Project.id).label('project_count'),
                    func.sum(Project.budget).label('total_budget'),
                    func.avg(Project.budget).label('avg_budget')
                )
                .join(Project)
                .group_by(Client.id, Client.name, Client.client_type)
                .order_by(func.count(Project.id).desc())
                .limit(10)
                .all()
            )

            # Client type distribution
            client_type_distribution = (
                db.session.query(
                    Client.client_type,
                    func.count(Client.id).label('client_count'),
                    func.count(Project.id).label('project_count'),
                    func.sum(Project.budget).label('total_budget')
                )
                .outerjoin(Project)
                .filter(Client.client_type.isnot(None))
                .group_by(Client.client_type)
                .all()
            )

            # Client acquisition trends
            acquisition_trends = (
                db.session.query(
                    self._get_month_format(Client.created_at).label('month'),
                    func.count(Client.id).label('new_clients')
                )
                .group_by(self._get_month_format(Client.created_at))
                .order_by(self._get_month_format(Client.created_at))
                .all()
            )

            # Client retention (clients with multiple projects) - simplified
            all_clients = db.session.query(Client.id).all()
            total_clients = len(all_clients)
            
            repeat_clients = 0
            for client_id, in all_clients:
                project_count = db.session.query(Project).filter(Project.client_id == client_id).count()
                if project_count > 1:
                    repeat_clients += 1

            retention_rate = (repeat_clients / total_clients * 100) if total_clients > 0 else 0

            return {
                'top_clients': [
                    {
                        'name': name,
                        'client_type': client_type,
                        'project_count': project_count,
                        'total_budget': float(total_budget) if total_budget else 0,
                        'avg_budget': float(avg_budget) if avg_budget else 0
                    }
                    for name, client_type, project_count, total_budget, avg_budget in top_clients_by_projects
                ],
                'client_type_distribution': [
                    {
                        'client_type': client_type,
                        'client_count': client_count,
                        'project_count': project_count,
                        'total_budget': float(total_budget) if total_budget else 0
                    }
                    for client_type, client_count, project_count, total_budget in client_type_distribution
                ],
                'acquisition_trends': [
                    {
                        'month': month if month else '',
                        'new_clients': new_clients
                    }
                    for month, new_clients in acquisition_trends
                ],
                'retention_metrics': {
                    'total_clients': total_clients,
                    'repeat_clients': repeat_clients,
                    'retention_rate': retention_rate
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_financial_reporting(self, date_range: tuple) -> Dict:
        """Get financial performance and budget analytics"""
        try:
            # Build date filter
            date_filter = []
            if date_range and date_range[0]:
                date_filter.append(Project.created_at >= datetime.fromisoformat(date_range[0]))
            if date_range and date_range[1]:
                date_filter.append(Project.created_at <= datetime.fromisoformat(date_range[1]))

            # Overall financial metrics
            financial_summary = (
                db.session.query(
                    func.count(Project.id).label('total_projects'),
                    func.sum(Project.budget).label('total_budget'),
                    func.avg(Project.budget).label('avg_budget'),
                    func.min(Project.budget).label('min_budget'),
                    func.max(Project.budget).label('max_budget')
                )
                .filter(*date_filter)
                .filter(Project.budget.isnot(None))
                .first()
            )

            # Revenue by month
            monthly_revenue = (
                db.session.query(
                    self._get_month_format(Project.created_at).label('month'),
                    func.sum(Project.budget).label('revenue'),
                    func.count(Project.id).label('project_count')
                )
                .filter(*date_filter)
                .filter(Project.budget.isnot(None))
                .group_by(self._get_month_format(Project.created_at))
                .order_by(self._get_month_format(Project.created_at))
                .all()
            )

            # Revenue by project type
            revenue_by_type = (
                db.session.query(
                    Project.project_type,
                    func.sum(Project.budget).label('revenue'),
                    func.count(Project.id).label('project_count'),
                    func.avg(Project.budget).label('avg_budget')
                )
                .filter(*date_filter)
                .filter(Project.budget.isnot(None))
                .filter(Project.project_type.isnot(None))
                .group_by(Project.project_type)
                .order_by(func.sum(Project.budget).desc())
                .all()
            )

            # Budget range distribution
            budget_ranges = [
                ('€0 - €25k', 0, 25000),
                ('€25k - €50k', 25000, 50000),
                ('€50k - €100k', 50000, 100000),
                ('€100k+', 100000, float('inf'))
            ]

            budget_distribution = []
            for range_name, min_budget, max_budget in budget_ranges:
                if max_budget == float('inf'):
                    count = (
                        db.session.query(func.count(Project.id))
                        .filter(*date_filter)
                        .filter(Project.budget >= min_budget)
                        .scalar()
                    )
                else:
                    count = (
                        db.session.query(func.count(Project.id))
                        .filter(*date_filter)
                        .filter(and_(Project.budget >= min_budget, Project.budget < max_budget))
                        .scalar()
                    )
                budget_distribution.append({
                    'range': range_name,
                    'count': count or 0
                })

            return {
                'financial_summary': {
                    'total_projects': financial_summary.total_projects if financial_summary else 0,
                    'total_budget': float(financial_summary.total_budget) if financial_summary and financial_summary.total_budget else 0,
                    'avg_budget': float(financial_summary.avg_budget) if financial_summary and financial_summary.avg_budget else 0,
                    'min_budget': float(financial_summary.min_budget) if financial_summary and financial_summary.min_budget else 0,
                    'max_budget': float(financial_summary.max_budget) if financial_summary and financial_summary.max_budget else 0
                },
                'monthly_revenue': [
                    {
                        'month': month if month else '',
                        'revenue': float(revenue) if revenue else 0,
                        'project_count': project_count
                    }
                    for month, revenue, project_count in monthly_revenue
                ],
                'revenue_by_type': [
                    {
                        'project_type': project_type,
                        'revenue': float(revenue) if revenue else 0,
                        'project_count': project_count,
                        'avg_budget': float(avg_budget) if avg_budget else 0
                    }
                    for project_type, revenue, project_count, avg_budget in revenue_by_type
                ],
                'budget_distribution': budget_distribution
            }
        except Exception as e:
            return {'error': str(e)}
    
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
                    func.count(PlantRecommendationRequest.id).label('count')
                )
                .filter(PlantRecommendationRequest.feedback_rating.isnot(None))
                .group_by(PlantRecommendationRequest.feedback_rating)
                .order_by(PlantRecommendationRequest.feedback_rating)
                .all()
            )

            # Most requested criteria
            project_type_requests = (
                db.session.query(
                    PlantRecommendationRequest.project_type,
                    func.count(PlantRecommendationRequest.id).label('count')
                )
                .filter(PlantRecommendationRequest.project_type.isnot(None))
                .group_by(PlantRecommendationRequest.project_type)
                .order_by(func.count(PlantRecommendationRequest.id).desc())
                .limit(10)
                .all()
            )

            # Requests over time
            request_trends = (
                db.session.query(
                    self._get_month_format(PlantRecommendationRequest.created_at).label('month'),
                    func.count(PlantRecommendationRequest.id).label('requests')
                )
                .group_by(self._get_month_format(PlantRecommendationRequest.created_at))
                .order_by(self._get_month_format(PlantRecommendationRequest.created_at))
                .all()
            )

            # Special requirements frequency - simplified for SQLite
            special_requirements = {
                'native_preference': 0,
                'wildlife_friendly': 0,
                'deer_resistant': 0,
                'pollinator_friendly': 0
            }
            
            # Count special requirements manually for SQLite compatibility
            all_requests = PlantRecommendationRequest.query.all()
            for req in all_requests:
                if req.native_preference:
                    special_requirements['native_preference'] += 1
                if req.wildlife_friendly:
                    special_requirements['wildlife_friendly'] += 1
                if req.deer_resistant_required:
                    special_requirements['deer_resistant'] += 1
                if req.pollinator_friendly_required:
                    special_requirements['pollinator_friendly'] += 1

            return {
                'total_requests': total_requests,
                'requests_with_feedback': requests_with_feedback,
                'feedback_rate': (requests_with_feedback / total_requests * 100) if total_requests > 0 else 0,
                'avg_rating': float(avg_rating) if avg_rating else 0,
                'rating_distribution': [
                    {'rating': rating, 'count': count}
                    for rating, count in rating_distribution
                ],
                'popular_project_types': [
                    {'project_type': project_type, 'count': count}
                    for project_type, count in project_type_requests
                ],
                'request_trends': [
                    {
                        'month': month if month else '',
                        'requests': requests
                    }
                    for month, requests in request_trends
                ],
                'special_requirements': special_requirements
            }
        except Exception as e:
            return {'error': str(e)}
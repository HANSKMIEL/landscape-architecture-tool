"""Add database indexes for query optimization

Revision ID: optimization_indexes
Revises: 
Create Date: 2024-07-29 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'optimization_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for frequently queried columns"""
    
    # Plants table indexes
    op.create_index('idx_plants_name', 'plants', ['name'])
    op.create_index('idx_plants_category', 'plants', ['category'])
    op.create_index('idx_plants_sun_requirements', 'plants', ['sun_requirements'])
    op.create_index('idx_plants_water_needs', 'plants', ['water_needs'])
    op.create_index('idx_plants_hardiness_zone', 'plants', ['hardiness_zone'])
    op.create_index('idx_plants_native', 'plants', ['native'])
    op.create_index('idx_plants_supplier_id', 'plants', ['supplier_id'])
    op.create_index('idx_plants_price', 'plants', ['price'])
    
    # Composite indexes for common query patterns
    op.create_index('idx_plants_category_sun', 'plants', ['category', 'sun_requirements'])
    op.create_index('idx_plants_native_category', 'plants', ['native', 'category'])
    
    # Projects table indexes
    op.create_index('idx_projects_client_id', 'projects', ['client_id'])
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_project_type', 'projects', ['project_type'])
    op.create_index('idx_projects_start_date', 'projects', ['start_date'])
    op.create_index('idx_projects_budget', 'projects', ['budget'])
    
    # Composite index for project filtering
    op.create_index('idx_projects_client_status', 'projects', ['client_id', 'status'])
    
    # Suppliers table indexes
    op.create_index('idx_suppliers_name', 'suppliers', ['name'])
    op.create_index('idx_suppliers_city', 'suppliers', ['city'])
    op.create_index('idx_suppliers_specialization', 'suppliers', ['specialization'])
    
    # Products table indexes
    op.create_index('idx_products_supplier_id', 'products', ['supplier_id'])
    op.create_index('idx_products_category', 'products', ['category'])
    op.create_index('idx_products_price', 'products', ['price'])
    op.create_index('idx_products_name', 'products', ['name'])
    
    # Clients table indexes
    op.create_index('idx_clients_name', 'clients', ['name'])
    op.create_index('idx_clients_city', 'clients', ['city'])
    op.create_index('idx_clients_client_type', 'clients', ['client_type'])
    
    # Project plants association table indexes
    op.create_index('idx_project_plants_project_id', 'project_plants', ['project_id'])
    op.create_index('idx_project_plants_plant_id', 'project_plants', ['plant_id'])
    op.create_index('idx_project_plants_status', 'project_plants', ['status'])
    
    # Plant recommendation requests indexes
    op.create_index('idx_plant_rec_hardiness_zone', 'plant_recommendation_requests', ['hardiness_zone'])
    op.create_index('idx_plant_rec_sun_exposure', 'plant_recommendation_requests', ['sun_exposure'])
    op.create_index('idx_plant_rec_project_type', 'plant_recommendation_requests', ['project_type'])
    op.create_index('idx_plant_rec_created_at', 'plant_recommendation_requests', ['created_at'])


def downgrade():
    """Remove the indexes"""
    
    # Plants table indexes
    op.drop_index('idx_plants_name')
    op.drop_index('idx_plants_category')
    op.drop_index('idx_plants_sun_requirements')
    op.drop_index('idx_plants_water_needs')
    op.drop_index('idx_plants_hardiness_zone')
    op.drop_index('idx_plants_native')
    op.drop_index('idx_plants_supplier_id')
    op.drop_index('idx_plants_price')
    op.drop_index('idx_plants_category_sun')
    op.drop_index('idx_plants_native_category')
    
    # Projects table indexes
    op.drop_index('idx_projects_client_id')
    op.drop_index('idx_projects_status')
    op.drop_index('idx_projects_project_type')
    op.drop_index('idx_projects_start_date')
    op.drop_index('idx_projects_budget')
    op.drop_index('idx_projects_client_status')
    
    # Suppliers table indexes
    op.drop_index('idx_suppliers_name')
    op.drop_index('idx_suppliers_city')
    op.drop_index('idx_suppliers_specialization')
    
    # Products table indexes
    op.drop_index('idx_products_supplier_id')
    op.drop_index('idx_products_category')
    op.drop_index('idx_products_price')
    op.drop_index('idx_products_name')
    
    # Clients table indexes
    op.drop_index('idx_clients_name')
    op.drop_index('idx_clients_city')
    op.drop_index('idx_clients_client_type')
    
    # Project plants association table indexes
    op.drop_index('idx_project_plants_project_id')
    op.drop_index('idx_project_plants_plant_id')
    op.drop_index('idx_project_plants_status')
    
    # Plant recommendation requests indexes
    op.drop_index('idx_plant_rec_hardiness_zone')
    op.drop_index('idx_plant_rec_sun_exposure')
    op.drop_index('idx_plant_rec_project_type')
    op.drop_index('idx_plant_rec_created_at')
"""
Project-Plant Relationship Management Service

Handles the relationship between projects and plants including
quantities, costs, status tracking, and project plant lists.
"""

import logging
from typing import Dict, List

from sqlalchemy.exc import IntegrityError

from src.models.landscape import Plant, Project, ProjectPlant
from src.models.user import db

logger = logging.getLogger(__name__)


class ProjectPlantService:
    """Service for managing project-plant relationships"""

    def add_plant_to_project(
        self,
        project_id: int,
        plant_id: int,
        quantity: int,
        unit_cost: float = None,
        notes: str = None,
    ) -> ProjectPlant:
        """Add a plant to a project with quantity and cost"""
        try:
            # Validate project and plant exist
            project = Project.query.get(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            plant = Plant.query.get(plant_id)
            if not plant:
                raise ValueError(f"Plant with ID {plant_id} not found")

            # Check if the plant is already in the project
            existing = ProjectPlant.query.filter_by(
                project_id=project_id, plant_id=plant_id
            ).first()

            if existing:
                # Update existing entry instead of creating duplicate
                existing.quantity += quantity
                if unit_cost is not None:
                    existing.unit_cost = unit_cost
                if notes:
                    existing.notes = notes
                db.session.commit()
                logger.info(
                    f"Updated plant {plant_id} quantity in project {project_id}"
                )
                return existing

            # Use plant's price as default unit cost if not provided
            if unit_cost is None and plant.price:
                unit_cost = plant.price

            # Create new project-plant relationship
            project_plant = ProjectPlant(
                project_id=project_id,
                plant_id=plant_id,
                quantity=quantity,
                unit_cost=unit_cost,
                notes=notes,
            )

            db.session.add(project_plant)
            db.session.commit()

            logger.info(
                f"Added plant {plant_id} to project {project_id} with quantity {quantity}"
            )
            return project_plant

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error: {e}")
            raise ValueError("Database constraint violation")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding plant to project: {e}")
            raise

    def update_plant_quantity(
        self, project_id: int, plant_id: int, new_quantity: int
    ) -> ProjectPlant:
        """Update plant quantity in project"""
        try:
            project_plant = ProjectPlant.query.filter_by(
                project_id=project_id, plant_id=plant_id
            ).first()

            if not project_plant:
                raise ValueError(f"Plant {plant_id} not found in project {project_id}")

            if new_quantity <= 0:
                raise ValueError("Quantity must be greater than 0")

            project_plant.quantity = new_quantity
            db.session.commit()

            logger.info(
                f"Updated plant {plant_id} quantity to {new_quantity} in project {project_id}"
            )
            return project_plant

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating plant quantity: {e}")
            raise

    def update_plant_status(
        self, project_id: int, plant_id: int, status: str
    ) -> ProjectPlant:
        """Update plant status (planned, ordered, planted, etc.)"""
        try:
            valid_statuses = ["planned", "ordered", "planted", "completed"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

            project_plant = ProjectPlant.query.filter_by(
                project_id=project_id, plant_id=plant_id
            ).first()

            if not project_plant:
                raise ValueError(f"Plant {plant_id} not found in project {project_id}")

            project_plant.status = status
            db.session.commit()

            logger.info(
                f"Updated plant {plant_id} status to {status} in project {project_id}"
            )
            return project_plant

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating plant status: {e}")
            raise

    def get_project_plant_list(self, project_id: int) -> List[Dict]:
        """Get complete plant list for a project"""
        try:
            project = Project.query.get(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            project_plants = ProjectPlant.query.filter_by(project_id=project_id).all()

            return [pp.to_dict() for pp in project_plants]

        except Exception as e:
            logger.error(f"Error getting project plant list: {e}")
            raise

    def calculate_project_cost(self, project_id: int) -> Dict:
        """Calculate total project cost breakdown"""
        try:
            project = Project.query.get(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            project_plants = ProjectPlant.query.filter_by(project_id=project_id).all()

            total_cost = 0
            plants_with_cost = 0
            plants_without_cost = 0
            cost_breakdown = []

            for pp in project_plants:
                if pp.unit_cost is not None:
                    plant_total = pp.unit_cost * pp.quantity
                    total_cost += plant_total
                    plants_with_cost += 1

                    cost_breakdown.append(
                        {
                            "plant_id": pp.plant_id,
                            "plant_name": pp.plant.name if pp.plant else "Unknown",
                            "quantity": pp.quantity,
                            "unit_cost": pp.unit_cost,
                            "total_cost": plant_total,
                            "status": pp.status,
                        }
                    )
                else:
                    plants_without_cost += 1
                    cost_breakdown.append(
                        {
                            "plant_id": pp.plant_id,
                            "plant_name": pp.plant.name if pp.plant else "Unknown",
                            "quantity": pp.quantity,
                            "unit_cost": None,
                            "total_cost": None,
                            "status": pp.status,
                        }
                    )

            return {
                "project_id": project_id,
                "project_name": project.name,
                "total_cost": total_cost,
                "plants_with_cost": plants_with_cost,
                "plants_without_cost": plants_without_cost,
                "total_plants": len(project_plants),
                "cost_breakdown": cost_breakdown,
                "budget": project.budget,
                "budget_remaining": (
                    (project.budget - total_cost) if project.budget else None
                ),
            }

        except Exception as e:
            logger.error(f"Error calculating project cost: {e}")
            raise

    def generate_plant_order_list(self, project_id: int) -> List[Dict]:
        """Generate plant order list for suppliers"""
        try:
            project = Project.query.get(project_id)
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            # Get plants that are planned or ordered
            project_plants = ProjectPlant.query.filter(
                ProjectPlant.project_id == project_id,
                ProjectPlant.status.in_(["planned", "ordered"]),
            ).all()

            # Group by supplier
            supplier_orders = {}

            for pp in project_plants:
                plant = pp.plant
                if not plant:
                    continue

                supplier_name = (
                    plant.supplier.name if plant.supplier else "Unknown Supplier"
                )
                supplier_id = plant.supplier_id if plant.supplier_id else 0

                if supplier_id not in supplier_orders:
                    supplier_orders[supplier_id] = {
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_name,
                        "contact_info": {
                            "email": plant.supplier.email if plant.supplier else None,
                            "phone": plant.supplier.phone if plant.supplier else None,
                        },
                        "plants": [],
                        "total_cost": 0,
                    }

                plant_cost = (pp.unit_cost * pp.quantity) if pp.unit_cost else 0
                supplier_orders[supplier_id]["plants"].append(
                    {
                        "plant_id": pp.plant_id,
                        "plant_name": plant.name,
                        "common_name": plant.common_name,
                        "quantity": pp.quantity,
                        "unit_cost": pp.unit_cost,
                        "total_cost": plant_cost,
                        "status": pp.status,
                        "notes": pp.notes,
                    }
                )
                supplier_orders[supplier_id]["total_cost"] += plant_cost

            return list(supplier_orders.values())

        except Exception as e:
            logger.error(f"Error generating plant order list: {e}")
            raise

    def remove_plant_from_project(self, project_id: int, plant_id: int) -> bool:
        """Remove a plant from a project"""
        try:
            project_plant = ProjectPlant.query.filter_by(
                project_id=project_id, plant_id=plant_id
            ).first()

            if not project_plant:
                raise ValueError(f"Plant {plant_id} not found in project {project_id}")

            db.session.delete(project_plant)
            db.session.commit()

            logger.info(f"Removed plant {plant_id} from project {project_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing plant from project: {e}")
            raise

    def update_plant_cost(
        self, project_id: int, plant_id: int, unit_cost: float
    ) -> ProjectPlant:
        """Update plant unit cost in project"""
        try:
            project_plant = ProjectPlant.query.filter_by(
                project_id=project_id, plant_id=plant_id
            ).first()

            if not project_plant:
                raise ValueError(f"Plant {plant_id} not found in project {project_id}")

            if unit_cost < 0:
                raise ValueError("Unit cost cannot be negative")

            project_plant.unit_cost = unit_cost
            db.session.commit()

            logger.info(
                f"Updated plant {plant_id} unit cost to {unit_cost} in project {project_id}"
            )
            return project_plant

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating plant cost: {e}")
            raise

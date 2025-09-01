"""
Project-Plant Relationship API Routes

Provides REST API endpoints for managing project-plant relationships
including adding plants, updating quantities, and generating reports.
"""

import logging

from flask import Blueprint, jsonify, request

from src.schemas import ProjectPlantCreateSchema, ProjectPlantUpdateSchema
from src.services.project_plant import ProjectPlantService
from src.utils.error_handlers import handle_errors

logger = logging.getLogger(__name__)

project_plants_bp = Blueprint("project_plants", __name__)
service = ProjectPlantService()


@project_plants_bp.route("/api/projects/<int:project_id>/plants", methods=["POST"])
@handle_errors
def add_plant_to_project(project_id):
    """Add a plant to a project"""
    try:
        data = request.get_json()

        # Validate input
        schema = ProjectPlantCreateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        project_plant = service.add_plant_to_project(
            project_id=project_id,
            plant_id=validated_data["plant_id"],
            quantity=validated_data["quantity"],
            unit_cost=validated_data.get("unit_cost"),
            notes=validated_data.get("notes"),
        )

        return jsonify(project_plant.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding plant to project: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/plants/<int:plant_id>", methods=["PUT"])
@handle_errors
def update_project_plant(project_id, plant_id):
    """Update plant details in project"""
    try:
        data = request.get_json()

        # Validate input
        schema = ProjectPlantUpdateSchema(**data)
        validated_data = schema.model_dump(exclude_unset=True)

        # Handle different update operations
        if "quantity" in validated_data:
            project_plant = service.update_plant_quantity(project_id, plant_id, validated_data["quantity"])
        elif "status" in validated_data:
            project_plant = service.update_plant_status(project_id, plant_id, validated_data["status"])
        elif "unit_cost" in validated_data:
            project_plant = service.update_plant_cost(project_id, plant_id, validated_data["unit_cost"])
        else:
            return jsonify({"error": "No valid update fields provided"}), 400

        return jsonify(project_plant.to_dict())

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating project plant: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/plants/<int:plant_id>", methods=["DELETE"])
@handle_errors
def remove_plant_from_project(project_id, plant_id):
    """Remove a plant from a project"""
    try:
        success = service.remove_plant_from_project(project_id, plant_id)
        if success:
            return jsonify({"message": "Plant removed from project successfully"})
        else:
            return jsonify({"error": "Failed to remove plant from project"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error removing plant from project: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/plants", methods=["GET"])
@handle_errors
def get_project_plants(project_id):
    """Get all plants for a project"""
    try:
        plants = service.get_project_plant_list(project_id)
        return jsonify(plants)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting project plants: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/cost-analysis", methods=["GET"])
@handle_errors
def get_project_cost_analysis(project_id):
    """Get project cost breakdown"""
    try:
        cost_analysis = service.calculate_project_cost(project_id)
        return jsonify(cost_analysis)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting project cost analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/plant-order-list", methods=["GET"])
@handle_errors
def get_plant_order_list(project_id):
    """Generate plant order list for suppliers"""
    try:
        order_list = service.generate_plant_order_list(project_id)
        return jsonify(order_list)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating plant order list: {e}")
        return jsonify({"error": "Internal server error"}), 500


@project_plants_bp.route("/api/projects/<int:project_id>/plants/batch", methods=["POST"])
@handle_errors
def add_multiple_plants_to_project(project_id):
    """Add multiple plants to a project at once"""
    try:
        data = request.get_json()
        plants_data = data.get("plants", [])

        if not plants_data:
            return jsonify({"error": "No plants data provided"}), 400

        results = []
        errors = []

        for plant_data in plants_data:
            try:
                # Validate each plant entry
                schema = ProjectPlantCreateSchema(**plant_data)
                validated_data = schema.model_dump(exclude_unset=True)

                project_plant = service.add_plant_to_project(
                    project_id=project_id,
                    plant_id=validated_data["plant_id"],
                    quantity=validated_data["quantity"],
                    unit_cost=validated_data.get("unit_cost"),
                    notes=validated_data.get("notes"),
                )

                results.append(project_plant.to_dict())

            except Exception as e:
                errors.append({"plant_data": plant_data, "error": str(e)})

        response = {
            "added_plants": results,
            "errors": errors,
            "total_added": len(results),
            "total_errors": len(errors),
        }

        if errors:
            return jsonify(response), 207  # Multi-status
        else:
            return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error adding multiple plants to project: {e}")
        return jsonify({"error": "Internal server error"}), 500

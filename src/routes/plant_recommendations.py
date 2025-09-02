"""
Plant Recommendation API Routes

Provides REST API endpoints for plant recommendation functionality
including recommendations, feedback, history, and data import/export.
"""

import csv
import io
import logging
import uuid
from typing import Any

from flask import Blueprint, Response, jsonify, request, session

from src.models.landscape import Plant, PlantRecommendationRequest
from src.models.user import db
from src.services.plant_recommendation import (
    PlantRecommendationEngine,
    RecommendationCriteria,
)

# Create blueprint
plant_recommendations_bp = Blueprint("plant_recommendations", __name__)

# Initialize recommendation engine
recommendation_engine = PlantRecommendationEngine()


@plant_recommendations_bp.route("/api/plant-recommendations", methods=["POST"])
def get_plant_recommendations():
    """
    Get plant recommendations based on criteria

    Request body should contain recommendation criteria:
    {
        "hardiness_zone": "6a",
        "sun_exposure": "full_sun",
        "soil_type": "loam",
        "desired_height_min": 1.0,
        "desired_height_max": 3.0,
        "maintenance_level": "low",
        "native_preference": true,
        ...
    }

    Returns:
    {
        "recommendations": [
            {
                "plant": {...plant data...},
                "score": 0.85,
                "criteria_scores": {...},
                "match_reasons": [...],
                "warnings": [...]
            }
        ],
        "request_id": "uuid",
        "criteria_summary": {...}
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Parse criteria from request
        criteria = RecommendationCriteria(
            hardiness_zone=data.get("hardiness_zone"),
            sun_exposure=data.get("sun_exposure"),
            soil_type=data.get("soil_type"),
            soil_ph=data.get("soil_ph"),
            moisture_level=data.get("moisture_level"),
            desired_height_min=data.get("desired_height_min"),
            desired_height_max=data.get("desired_height_max"),
            desired_width_min=data.get("desired_width_min"),
            desired_width_max=data.get("desired_width_max"),
            color_preferences=data.get("color_preferences", []),
            bloom_season=data.get("bloom_season"),
            maintenance_level=data.get("maintenance_level"),
            budget_range=data.get("budget_range"),
            native_preference=data.get("native_preference", False),
            wildlife_friendly=data.get("wildlife_friendly", False),
            deer_resistant_required=data.get("deer_resistant_required", False),
            pollinator_friendly_required=data.get("pollinator_friendly_required", False),
            container_planting=data.get("container_planting", False),
            screening_purpose=data.get("screening_purpose", False),
            hedging_purpose=data.get("hedging_purpose", False),
            groundcover_purpose=data.get("groundcover_purpose", False),
            slope_planting=data.get("slope_planting", False),
            weights=data.get("weights"),  # Allow custom weights
        )

        # Get recommendation parameters
        max_results = data.get("max_results", 10)
        min_score = data.get("min_score", 0.3)

        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(criteria, max_results, min_score)

        # Generate session ID if not exists
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())

        # Log recommendation request
        try:
            logged_request = recommendation_engine.log_recommendation_request(
                criteria=criteria,
                results=recommendations,
                user_id=data.get("user_id"),
                session_id=session["session_id"],
                ip_address=request.remote_addr,
            )
            request_id = logged_request.id
        except Exception:
            # Continue even if logging fails
            request_id = None

        # Format response
        response = {
            "recommendations": [
                {
                    "plant": rec.plant.to_dict(),
                    "score": round(rec.total_score, 3),
                    "criteria_scores": {k: round(v, 3) for k, v in rec.criteria_scores.items()},
                    "match_reasons": rec.match_reasons,
                    "warnings": rec.warnings,
                }
                for rec in recommendations
            ],
            "request_id": request_id,
            "criteria_summary": _format_criteria_summary(criteria),
            "total_plants_evaluated": Plant.query.count(),
            "recommendations_count": len(recommendations),
        }

        return jsonify(response)

    except Exception:
        logging.exception("Failed to get recommendations")
        return (
            jsonify({"error": "Failed to get recommendations due to an internal error."}),
            500,
        )


@plant_recommendations_bp.route("/api/plant-recommendations/criteria-options", methods=["GET"])
def get_criteria_options():
    """
    Get available options for recommendation criteria

    Returns:
    {
        "hardiness_zones": [...],
        "sun_exposures": [...],
        "soil_types": [...],
        "maintenance_levels": [...],
        ...
    }
    """
    try:
        # Query database for available options
        plants = Plant.query.all()

        options = {
            "hardiness_zones": sorted(set(filter(None, [p.hardiness_zone for p in plants]))),
            "sun_exposures": ["Full Sun", "Partial Sun", "Partial Shade", "Full Shade"],
            "soil_types": sorted(set(filter(None, [p.soil_type for p in plants]))),
            "maintenance_levels": ["Low", "Medium", "High"],
            "moisture_levels": ["Low", "Medium", "High"],
            "budget_ranges": ["Low", "Medium", "High", "Premium"],
            "plant_categories": sorted(set(filter(None, [p.category for p in plants]))),
            "bloom_colors": sorted(set(filter(None, [p.bloom_color for p in plants]))),
            "foliage_colors": sorted(set(filter(None, [p.foliage_color for p in plants]))),
            "bloom_seasons": sorted(set(filter(None, [p.bloom_time for p in plants]))),
            "project_types": [
                "Garden",
                "Landscape",
                "Commercial",
                "Residential",
                "Public Space",
            ],
        }

        return jsonify(options)

    except Exception as e:
        return jsonify({"error": f"Failed to get criteria options: {e!s}"}), 500


@plant_recommendations_bp.route("/api/plant-recommendations/feedback", methods=["POST"])
def submit_feedback():
    """
    Submit user feedback for a recommendation

    Request body:
    {
        "request_id": 123,
        "feedback": {
            "helpful": true,
            "selected_plants": [1, 5, 8],
            "comments": "Great suggestions!",
            "improvements": "More native options"
        },
        "rating": 4
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        request_id = data.get("request_id")
        feedback = data.get("feedback", {})
        rating = data.get("rating")

        if not request_id:
            return jsonify({"error": "request_id is required"}), 400

        # Save feedback
        success = recommendation_engine.save_user_feedback(request_id=request_id, feedback=feedback, rating=rating)

        if success:
            return jsonify({"message": "Feedback saved successfully"})
        return jsonify({"error": "Failed to save feedback"}), 404

    except Exception as e:
        return jsonify({"error": "An internal error has occurred."}), 500


@plant_recommendations_bp.route("/api/plant-recommendations/history", methods=["GET"])
def get_recommendation_history():
    """
    Get recommendation history (optionally filtered by user/session)

    Query parameters:
    - user_id: Filter by user ID
    - session_id: Filter by session ID
    - limit: Maximum number of records (default 50)
    - offset: Pagination offset (default 0)
    """
    try:
        user_id = request.args.get("user_id")
        session_id = request.args.get("session_id", session.get("session_id"))

        # Handle invalid parameters gracefully
        try:
            limit = min(int(request.args.get("limit", 50)), 100)  # Max 100 records
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid limit parameter"}), 400

        try:
            offset = int(request.args.get("offset", 0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid offset parameter"}), 400

        query = PlantRecommendationRequest.query

        if user_id:
            query = query.filter(PlantRecommendationRequest.user_id == user_id)
        elif session_id:
            query = query.filter(PlantRecommendationRequest.session_id == session_id)

        requests = query.order_by(PlantRecommendationRequest.created_at.desc()).offset(offset).limit(limit).all()

        history = []
        for req in requests:
            history.append(
                {
                    "id": req.id,
                    "created_at": (req.created_at.isoformat() if req.created_at else None),
                    "criteria_summary": _format_request_criteria(req),
                    "recommendations_count": (len(req.recommended_plants) if req.recommended_plants else 0),
                    "feedback_rating": req.feedback_rating,
                    "has_feedback": bool(req.user_feedback),
                }
            )

        return jsonify(
            {
                "history": history,
                "limit": limit,
                "offset": offset,
                "has_more": len(requests) == limit,
            }
        )

    except Exception as e:
        logging.exception("Failed to get history")  # Log full stack trace for investigation
        return jsonify({"error": "An internal error has occurred."}), 500


@plant_recommendations_bp.route("/api/plant-recommendations/export", methods=["POST"])
def export_recommendations():
    """
    Export recommendation results to CSV format

    Request body:
    {
        "request_id": 123,
        "format": "csv"  // Currently only CSV supported
    }

    Returns CSV file with plant recommendations
    """
    try:
        data = request.get_json()
        request_id = data.get("request_id")
        export_format = data.get("format", "csv").lower()

        if not request_id:
            return jsonify({"error": "request_id is required"}), 400

        if export_format != "csv":
            return jsonify({"error": "Only CSV format is currently supported"}), 400

        # Get recommendation request
        req = db.session.get(PlantRecommendationRequest, request_id)
        if not req or not req.recommended_plants:
            return (
                jsonify({"error": "Recommendation request not found or has no results"}),
                404,
            )

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "Plant ID",
                "Plant Name",
                "Common Name",
                "Category",
                "Score",
                "Height (min-max)",
                "Width (min-max)",
                "Sun Requirements",
                "Water Needs",
                "Maintenance",
                "Native",
                "Price",
                "Match Reasons",
                "Warnings",
            ]
        )

        # Write recommendation data
        for rec_data in req.recommended_plants:
            plant_id = rec_data.get("plant_id")
            plant = db.session.get(Plant, plant_id)

            if plant:
                height_range = f"{plant.height_min or 'N/A'}-{plant.height_max or 'N/A'}"
                width_range = f"{plant.width_min or 'N/A'}-{plant.width_max or 'N/A'}"
                match_reasons = "; ".join(rec_data.get("match_reasons", []))
                warnings = "; ".join(rec_data.get("warnings", []))

                writer.writerow(
                    [
                        plant.id,
                        plant.name,
                        plant.common_name or "N/A",
                        plant.category or "N/A",
                        rec_data.get("total_score", 0),
                        height_range,
                        width_range,
                        plant.sun_requirements or "N/A",
                        plant.water_needs or "N/A",
                        plant.maintenance or "N/A",
                        "Yes" if plant.native else "No",
                        plant.price or "N/A",
                        match_reasons,
                        warnings,
                    ]
                )

        # Create response
        csv_content = output.getvalue()
        output.close()

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": (f"attachment; filename=plant_recommendations_{request_id}.csv")},
        )

    except Exception as e:
        return jsonify({"error": f"Failed to export recommendations: {e!s}"}), 500


@plant_recommendations_bp.route("/api/plant-recommendations/import", methods=["POST"])
def import_plant_data():
    """
    Import plant data from CSV file

    Expects multipart/form-data with 'file' field containing CSV
    CSV should have headers matching Plant model attributes
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith(".csv"):
            return jsonify({"error": "Only CSV files are supported"}), 400

        # Read and parse CSV
        csv_content = file.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        imported_plants = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (after header)
            try:
                # Create plant from CSV row
                plant = Plant(
                    name=row.get("name", "").strip(),
                    common_name=row.get("common_name", "").strip() or None,
                    category=row.get("category", "").strip() or None,
                    height_min=_parse_float(row.get("height_min")),
                    height_max=_parse_float(row.get("height_max")),
                    width_min=_parse_float(row.get("width_min")),
                    width_max=_parse_float(row.get("width_max")),
                    sun_requirements=row.get("sun_requirements", "").strip() or None,
                    soil_type=row.get("soil_type", "").strip() or None,
                    water_needs=row.get("water_needs", "").strip() or None,
                    hardiness_zone=row.get("hardiness_zone", "").strip() or None,
                    bloom_time=row.get("bloom_time", "").strip() or None,
                    bloom_color=row.get("bloom_color", "").strip() or None,
                    foliage_color=row.get("foliage_color", "").strip() or None,
                    native=_parse_bool(row.get("native", "")),
                    maintenance=row.get("maintenance", "").strip() or None,
                    price=_parse_float(row.get("price")),
                    # Extended attributes
                    temperature_min=_parse_float(row.get("temperature_min")),
                    temperature_max=_parse_float(row.get("temperature_max")),
                    humidity_preference=row.get("humidity_preference", "").strip() or None,
                    wind_tolerance=row.get("wind_tolerance", "").strip() or None,
                    soil_ph_min=_parse_float(row.get("soil_ph_min")),
                    soil_ph_max=_parse_float(row.get("soil_ph_max")),
                    soil_drainage=row.get("soil_drainage", "").strip() or None,
                    soil_fertility=row.get("soil_fertility", "").strip() or None,
                    pruning_needs=row.get("pruning_needs", "").strip() or None,
                    fertilizer_needs=row.get("fertilizer_needs", "").strip() or None,
                    pest_resistance=row.get("pest_resistance", "").strip() or None,
                    disease_resistance=row.get("disease_resistance", "").strip() or None,
                    plant_form=row.get("plant_form", "").strip() or None,
                    foliage_texture=row.get("foliage_texture", "").strip() or None,
                    seasonal_interest=row.get("seasonal_interest", "").strip() or None,
                    fragrance=_parse_bool(row.get("fragrance", "")),
                    growth_rate=row.get("growth_rate", "").strip() or None,
                    mature_spread=_parse_float(row.get("mature_spread")),
                    root_system=row.get("root_system", "").strip() or None,
                    wildlife_value=row.get("wildlife_value", "").strip() or None,
                    pollinator_friendly=_parse_bool(row.get("pollinator_friendly", "")),
                    deer_resistant=_parse_bool(row.get("deer_resistant", "")),
                    invasive_potential=row.get("invasive_potential", "").strip() or None,
                    suitable_for_containers=_parse_bool(row.get("suitable_for_containers", "")),
                    suitable_for_hedging=_parse_bool(row.get("suitable_for_hedging", "")),
                    suitable_for_screening=_parse_bool(row.get("suitable_for_screening", "")),
                    suitable_for_groundcover=_parse_bool(row.get("suitable_for_groundcover", "")),
                    suitable_for_slopes=_parse_bool(row.get("suitable_for_slopes", "")),
                )

                if not plant.name:
                    errors.append(f"Row {row_num}: Plant name is required")
                    continue

                db.session.add(plant)
                imported_plants.append(plant.name)

            except Exception as e:
                logging.exception(f"Error processing row {row_num}: {e!s}")
                errors.append(f"Row {row_num}: An error occurred while processing this row")

        # Commit if no errors
        if not errors:
            db.session.commit()
            return jsonify(
                {
                    "message": f"Successfully imported {len(imported_plants)} plants",
                    "imported_plants": imported_plants,
                }
            )
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Import failed due to errors",
                    "errors": errors[:10],  # Limit error messages
                    "total_errors": len(errors),
                }
            ),
            400,
        )

    except Exception as e:
        logging.exception(f"Failed to import plant data: {e!s}")
        return (
            jsonify({"error": "An internal error occurred while importing plant data"}),
            500,
        )


# Helper functions
def _format_criteria_summary(criteria: RecommendationCriteria) -> dict[str, Any]:
    """Format criteria for summary display"""
    summary = {}

    if criteria.hardiness_zone:
        summary["Hardiness Zone"] = criteria.hardiness_zone
    if criteria.sun_exposure:
        summary["Sun Exposure"] = criteria.sun_exposure
    if criteria.soil_type:
        summary["Soil Type"] = criteria.soil_type
    if criteria.desired_height_min or criteria.desired_height_max:
        height_range = f"{criteria.desired_height_min or 'Any'}-" f"{criteria.desired_height_max or 'Any'}m"
        summary["Desired Height"] = height_range
    if criteria.maintenance_level:
        summary["Maintenance Level"] = criteria.maintenance_level
    if criteria.native_preference:
        summary["Native Preference"] = "Yes"
    if criteria.wildlife_friendly:
        summary["Wildlife Friendly"] = "Yes"

    return summary


def _format_request_criteria(req: PlantRecommendationRequest) -> dict[str, Any]:
    """Format stored request criteria for display"""
    summary = {}

    if req.hardiness_zone:
        summary["Hardiness Zone"] = req.hardiness_zone
    if req.sun_exposure:
        summary["Sun Exposure"] = req.sun_exposure
    if req.soil_type:
        summary["Soil Type"] = req.soil_type
    if req.desired_height_min or req.desired_height_max:
        height_range = f"{req.desired_height_min or 'Any'}-{req.desired_height_max or 'Any'}m"
        summary["Desired Height"] = height_range
    if req.maintenance_level:
        summary["Maintenance Level"] = req.maintenance_level
    if req.native_preference:
        summary["Native Preference"] = "Yes"

    return summary


def _parse_float(value: str) -> float:
    """Safely parse float from string"""
    if not value or value.strip() == "":
        return None
    try:
        return float(value.strip())
    except (ValueError, TypeError):
        return None


def _parse_bool(value: str) -> bool:
    """Safely parse boolean from string"""
    if not value:
        return False
    value = value.strip().lower()
    return value in ["true", "1", "yes", "y", "on"]

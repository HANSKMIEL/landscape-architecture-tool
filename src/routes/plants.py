import openai
from flask import Blueprint, jsonify, request

from src.models.landscape import Plant
from src.models.user import db
from src.routes.user import data_access_required, login_required

plants_bp = Blueprint("plants", __name__)


@plants_bp.route("/", methods=["GET"])
@login_required
def get_plants():
    """Get all plants with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get("search", "")
        category = request.args.get("category", "")
        sun_requirements = request.args.get("sun_requirements", "")
        water_requirements = request.args.get("water_requirements", "")
        native_only = request.args.get("native_only", "").lower() == "true"
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        query = Plant.query

        # Apply filters
        if search:
            query = query.filter(
                Plant.name.contains(search)
                | Plant.scientific_name.contains(search)
                | Plant.common_name.contains(search)
            )

        if category:
            query = query.filter(Plant.category == category)

        if sun_requirements:
            query = query.filter(Plant.sun_requirements == sun_requirements)

        if water_requirements:
            query = query.filter(Plant.water_requirements == water_requirements)

        if native_only:
            query = query.filter(Plant.native_to_netherlands.is_(True))

        plants = query.order_by(Plant.name).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "plants": [plant.to_dict() for plant in plants.items],
                "total": plants.total,
                "pages": plants.pages,
                "current_page": page,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plants_bp.route("/recommendations", methods=["POST"])
@data_access_required
def get_plant_recommendations():
    """Get AI-powered plant recommendations"""
    try:
        data = request.get_json()

        # Extract criteria from request
        site_conditions = data.get("site_conditions", {})
        project_type = data.get("project_type", "Residential Garden")
        preferences = data.get("preferences", {})

        # Build context for AI
        context = f"""
        Project Type: {project_type}
        Site Conditions:
        - Sun Exposure: {site_conditions.get('sun_exposure', 'Unknown')}
        - Soil Type: {site_conditions.get('soil_type', 'Unknown')}
        - Water Availability: {site_conditions.get('water_availability', 'Medium')}
        - Climate Zone: Netherlands (Hardiness Zone 8-9)

        Preferences:
        - Maintenance Level: {preferences.get('maintenance_level', 'Medium')}
        - Native Plants Preferred: {preferences.get('native_preferred', False)}
        - Attracts Pollinators: {preferences.get('pollinators', False)}
        - Deer Resistant: {preferences.get('deer_resistant', False)}
        """

        # Get available plants from database
        available_plants = Plant.query.all()
        plant_list = []
        for plant in available_plants[:20]:  # Limit for AI processing
            plant_info = (
                f"{plant.name} ({plant.scientific_name}) - "
                f"{plant.category}, {plant.sun_requirements}, "
                f"{plant.water_requirements}"
            )
            plant_list.append(plant_info)

        # Create AI prompt
        prompt_parts = [
            "As a landscape architecture expert, recommend the best plants " "for this project:",
            "",
            context,
            "",
            "Available plants in our database:",
            chr(10).join(plant_list),
            "",
            "Please recommend 5-8 plants that would work best for these conditions.",
            "For each plant, provide:",
            "1. Plant name",
            "2. Why it's suitable for these conditions",
            "3. Design considerations",
            "4. Maintenance requirements",
            "",
            "Focus on plants that are suitable for Dutch climate and the " "specified conditions.",
        ]
        prompt = "\n".join(prompt_parts)

        try:
            # Call OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert landscape architect specializing in "
                            "Dutch gardens and sustainable plant selection."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            ai_recommendations = response.choices[0].message.content

            # Get matching plants from database
            recommended_plants = []
            for plant in available_plants:
                # Simple matching logic - in production, this would be more
                # sophisticated
                if any(
                    keyword in plant.name.lower() or keyword in plant.scientific_name.lower()
                    for keyword in ai_recommendations.lower().split()
                ):
                    recommended_plants.append(plant.to_dict())

            return jsonify(
                {
                    "recommendations": ai_recommendations,
                    "matching_plants": recommended_plants[:8],
                    "criteria_used": {
                        "site_conditions": site_conditions,
                        "project_type": project_type,
                        "preferences": preferences,
                    },
                }
            )

        except Exception:
            # Fallback to rule-based recommendations if AI fails
            fallback_plants = []
            query = Plant.query

            # Apply basic filtering based on conditions
            if site_conditions.get("sun_exposure") == "Full Sun":
                query = query.filter(Plant.sun_requirements.in_(["Full Sun", "Partial Sun"]))
            elif site_conditions.get("sun_exposure") == "Shade":
                query = query.filter(Plant.sun_requirements.in_(["Shade", "Partial Sun"]))

            if preferences.get("native_preferred"):
                query = query.filter(Plant.native_to_netherlands.is_(True))

            fallback_plants = query.limit(8).all()

            return jsonify(
                {
                    "recommendations": (
                        "AI recommendations temporarily unavailable. Here are plants "
                        "matching your basic criteria."
                    ),
                    "matching_plants": [plant.to_dict() for plant in fallback_plants],
                    "criteria_used": {
                        "site_conditions": site_conditions,
                        "project_type": project_type,
                        "preferences": preferences,
                    },
                    "fallback_mode": True,
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plants_bp.route("/", methods=["POST"])
@data_access_required
def create_plant():
    """Create a new plant"""
    try:
        data = request.get_json()

        plant = Plant(
            name=data.get("name"),
            scientific_name=data.get("scientific_name"),
            common_name=data.get("common_name"),
            category=data.get("category"),
            sun_requirements=data.get("sun_requirements"),
            water_requirements=data.get("water_requirements"),
            soil_type=data.get("soil_type"),
            hardiness_zone=data.get("hardiness_zone"),
            mature_height=data.get("mature_height"),
            mature_width=data.get("mature_width"),
            bloom_time=data.get("bloom_time"),
            bloom_color=data.get("bloom_color"),
            foliage_color=data.get("foliage_color"),
            maintenance_level=data.get("maintenance_level"),
            native_to_netherlands=data.get("native_to_netherlands", False),
            deer_resistant=data.get("deer_resistant", False),
            drought_tolerant=data.get("drought_tolerant", False),
            attracts_pollinators=data.get("attracts_pollinators", False),
            price=data.get("price"),
            supplier_id=data.get("supplier_id"),
            notes=data.get("notes"),
        )

        db.session.add(plant)
        db.session.commit()

        return jsonify(plant.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    """Get a specific plant"""
    try:
        plant = Plant.query.get_or_404(plant_id)
        return jsonify(plant.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plants_bp.route("/categories", methods=["GET"])
def get_plant_categories():
    """Get all plant categories"""
    try:
        categories = db.session.query(Plant.category).distinct().all()
        return jsonify([cat[0] for cat in categories if cat[0]])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

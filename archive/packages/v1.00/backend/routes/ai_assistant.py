# File location: src/routes/ai_assistant.py
# This file handles AI assistant operations using OpenAI API

import logging
import os
from datetime import UTC, datetime

import openai
from flask import Blueprint, jsonify, request

from src.models.landscape import Client, Plant, Product, Project, Supplier, db
from src.routes.user import login_required

ai_assistant_bp = Blueprint("ai_assistant", __name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py

@ai_assistant_bp.route("/api/ai/chat", methods=["POST"])
@login_required
def ai_chat():
    """Handle AI chat requests with landscape architecture context"""
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        language = data.get("language", "en")
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
        context = data.get("context", "landscape_architecture")
        
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        if not user_message.strip():
            return jsonify({"error": "Message is required"}), 400

        # Get current data for context
        stats = get_landscape_stats()

        # Build system prompt based on language
        if language == "nl":
            system_prompt = f"""Je bent een AI-assistent gespecialiseerd in landschapsarchitectuur. 
            Je helpt gebruikers met plantaanbevelingen, projectbeheer, en tuinontwerp.
            
            Huidige database statistieken:
            - Projecten: {stats['projects']}
            - Klanten: {stats['clients']}
            - Planten: {stats['plants']}
            - Producten: {stats['products']}
            - Leveranciers: {stats['suppliers']}
            
            Geef praktische, professionele adviezen in het Nederlands. 
            Focus op duurzaamheid, inheemse planten, en kosteneffectiviteit."""
        else:
            system_prompt = f"""You are an AI assistant specialized in landscape architecture. 
            You help users with plant recommendations, project management, and garden design.
            
            Current database statistics:
            - Projects: {stats['projects']}
            - Clients: {stats['clients']}
            - Plants: {stats['plants']}
            - Products: {stats['products']}
            - Suppliers: {stats['suppliers']}
            
            Provide practical, professional advice in English. 
            Focus on sustainability, native plants, and cost-effectiveness."""

        # Call OpenAI API
        try:
            from openai import OpenAI

            client = OpenAI(api_key=openai.api_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                max_tokens=500,
                temperature=0.7,
            )

            ai_response = response.choices[0].message.content.strip()

        except Exception as openai_error:
            logging.error(f"OpenAI API error: {openai_error!s}")
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
            
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            # Fallback responses
            fallback_responses = {
                "nl": {
                    "plant_recommendation": "Voor plantaanbevelingen raad ik aan om inheemse soorten te kiezen die geschikt zijn voor uw klimaat en bodemtype. Overweeg ook de onderhoudsvereisten en seizoensgebonden aspecten.",
                    "project_management": "Voor effectief projectbeheer is het belangrijk om duidelijke doelen te stellen, regelmatig te communiceren met klanten, en een gedetailleerde planning te maken.",
                    "design_tips": "Bij tuinontwerp is het belangrijk om rekening te houden met de bestaande omgeving, de wensen van de klant, en duurzame praktijken.",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "default": "Ik kan je helpen met plantaanbevelingen, projectbeheer, en tuinontwerp. Stel gerust specifieke vragen!"
                },
                "en": {
                    "plant_recommendation": "For plant recommendations, I suggest choosing native species suitable for your climate and soil type. Also consider maintenance requirements and seasonal aspects.",
                    "project_management": "For effective project management, it's important to set clear goals, communicate regularly with clients, and create detailed planning.",
                    "design_tips": "In garden design, it's important to consider the existing environment, client preferences, and sustainable practices.",
                    "default": "I can help you with plant recommendations, project management, and garden design. Feel free to ask specific questions!"
                }
=======
                    "default": "Ik kan je helpen met plantaanbevelingen, projectbeheer, en tuinontwerp. Stel gerust specifieke vragen!",
                },
                "en": {
                    "plant_recommendation": "For plant recommendations, I suggest choosing native species suitable for your climate and soil type. Also consider maintenance requirements and seasonal aspects.",
                    "project_management": "For effective project management, it's important to set clear goals, communicate regularly with clients, and create detailed planning.",
                    "design_tips": "In garden design, it's important to consider the existing environment, client preferences, and sustainable practices.",
                    "default": "I can help you with plant recommendations, project management, and garden design. Feel free to ask specific questions!",
                },
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            }

            # Determine response type based on keywords
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["plant", "flower", "tree", "shrub", "native"]):
                response_type = "plant_recommendation"
            elif any(word in message_lower for word in ["project", "manage", "plan", "schedule"]):
                response_type = "project_management"
            elif any(word in message_lower for word in ["design", "layout", "garden", "landscape"]):
                response_type = "design_tips"
            else:
                response_type = "default"
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
            
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            ai_response = fallback_responses[language][response_type]

        return jsonify({"response": ai_response, "timestamp": datetime.now(UTC).isoformat(), "language": language})

    except Exception as e:
        logging.error(f"AI chat error: {e!s}")
        return jsonify({"error": "AI service temporarily unavailable"}), 500


@ai_assistant_bp.route("/api/ai/plant-recommendations", methods=["POST"])
@login_required
def ai_plant_recommendations():
    """Generate AI-powered plant recommendations based on criteria"""
    try:
        data = request.get_json()
        criteria = data.get("criteria", {})
        language = data.get("language", "en")
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
        
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        # Get available plants
        plants = Plant.query.all()

        # Filter plants based on criteria
        filtered_plants = []
        for plant in plants:
            matches = True
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
            
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            if criteria.get("sun_requirements") and plant.sun_requirements != criteria["sun_requirements"]:
                matches = False
            if criteria.get("water_needs") and plant.water_needs != criteria["water_needs"]:
                matches = False
            if criteria.get("native_only") and not plant.native:
                matches = False
            if criteria.get("category") and plant.category != criteria["category"]:
                matches = False

            if matches:
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                filtered_plants.append({
                    "id": plant.id,
                    "name": plant.name,
                    "common_name": plant.common_name,
                    "category": plant.category,
                    "native": plant.native,
                    "sun_requirements": plant.sun_requirements,
                    "water_needs": plant.water_needs,
                    "height_min": plant.height_min,
                    "height_max": plant.height_max
                })
        
=======
                filtered_plants.append(
                    {
                        "id": plant.id,
                        "name": plant.name,
                        "common_name": plant.common_name,
                        "category": plant.category,
                        "native": plant.native,
                        "sun_requirements": plant.sun_requirements,
                        "water_needs": plant.water_needs,
                        "height_min": plant.height_min,
                        "height_max": plant.height_max,
                    }
                )

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        # Generate AI explanation
        if language == "nl":
            explanation = f"Gebaseerd op uw criteria heb ik {len(filtered_plants)} geschikte planten gevonden. Deze selectie houdt rekening met uw specifieke vereisten voor zonlicht, water, en andere factoren."
        else:
            explanation = f"Based on your criteria, I found {len(filtered_plants)} suitable plants. This selection considers your specific requirements for sunlight, water, and other factors."

        return jsonify(
            {
                "recommendations": filtered_plants[:10],  # Limit to top 10
                "explanation": explanation,
                "total_matches": len(filtered_plants),
                "criteria_used": criteria,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    except Exception as e:
        logging.error(f"Plant recommendations error: {e!s}")
        return jsonify({"error": "Failed to generate plant recommendations"}), 500


@ai_assistant_bp.route("/api/ai/project-insights", methods=["GET"])
@login_required
def ai_project_insights():
    """Generate AI-powered insights about projects"""
    try:
        language = request.args.get("language", "en")
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
        
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        # Get project statistics
        total_projects = Project.query.count()
        active_projects = Project.query.filter(Project.status == "active").count()
        completed_projects = Project.query.filter(Project.status == "completed").count()
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
        
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        # Get budget statistics
        budget_stats = (
            db.session.query(db.func.sum(Project.budget), db.func.avg(Project.budget))
            .filter(Project.budget.isnot(None))
            .first()
        )

        total_budget = float(budget_stats[0]) if budget_stats[0] else 0
        avg_budget = float(budget_stats[1]) if budget_stats[1] else 0

        # Generate insights
        insights = []
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
        
=======

>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
        if language == "nl":
            insights = [
                {
                    "type": "performance",
                    "title": "Project Prestaties",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "content": f"Je hebt {completed_projects} van de {total_projects} projecten voltooid. Dit is een voltooiingspercentage van {(completed_projects/total_projects*100):.1f}%." if total_projects > 0 else "Je hebt nog geen projecten voltooid.",
                    "recommendation": "Focus op het voltooien van actieve projecten om je voltooiingspercentage te verbeteren." if active_projects > completed_projects else "Uitstekende voltooiingsratio! Overweeg om meer projecten aan te nemen."
=======
                    "content": (
                        f"Je hebt {completed_projects} van de {total_projects} projecten voltooid. Dit is een voltooiingspercentage van {(completed_projects/total_projects*100):.1f}%."
                        if total_projects > 0
                        else "Je hebt nog geen projecten voltooid."
                    ),
                    "recommendation": (
                        "Focus op het voltooien van actieve projecten om je voltooiingspercentage te verbeteren."
                        if active_projects > completed_projects
                        else "Uitstekende voltooiingsratio! Overweeg om meer projecten aan te nemen."
                    ),
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
                },
                {
                    "type": "financial",
                    "title": "Financiële Analyse",
                    "content": f"Je totale projectbudget is €{total_budget:,.2f} met een gemiddelde van €{avg_budget:,.2f} per project.",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "recommendation": "Overweeg om projecten met hogere marges te targeten om de winstgevendheid te verbeteren." if avg_budget < 10000 else "Je gemiddelde projectwaarde is goed. Focus op het behouden van deze standaard."
=======
                    "recommendation": (
                        "Overweeg om projecten met hogere marges te targeten om de winstgevendheid te verbeteren."
                        if avg_budget < 10000
                        else "Je gemiddelde projectwaarde is goed. Focus op het behouden van deze standaard."
                    ),
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
                },
                {
                    "type": "growth",
                    "title": "Groei Mogelijkheden",
                    "content": f"Met {active_projects} actieve projecten heb je een goede werkvoorraad.",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "recommendation": "Overweeg om je team uit te breiden om meer projecten tegelijk aan te kunnen." if active_projects > 5 else "Je hebt capaciteit voor meer projecten. Focus op marketing en acquisitie."
                }
=======
                    "recommendation": (
                        "Overweeg om je team uit te breiden om meer projecten tegelijk aan te kunnen."
                        if active_projects > 5
                        else "Je hebt capaciteit voor meer projecten. Focus op marketing en acquisitie."
                    ),
                },
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            ]
        else:
            insights = [
                {
                    "type": "performance",
                    "title": "Project Performance",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "content": f"You have completed {completed_projects} out of {total_projects} projects. This is a completion rate of {(completed_projects/total_projects*100):.1f}%." if total_projects > 0 else "You haven't completed any projects yet.",
                    "recommendation": "Focus on completing active projects to improve your completion rate." if active_projects > completed_projects else "Excellent completion ratio! Consider taking on more projects."
=======
                    "content": (
                        f"You have completed {completed_projects} out of {total_projects} projects. This is a completion rate of {(completed_projects/total_projects*100):.1f}%."
                        if total_projects > 0
                        else "You haven't completed any projects yet."
                    ),
                    "recommendation": (
                        "Focus on completing active projects to improve your completion rate."
                        if active_projects > completed_projects
                        else "Excellent completion ratio! Consider taking on more projects."
                    ),
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
                },
                {
                    "type": "financial",
                    "title": "Financial Analysis",
                    "content": f"Your total project budget is €{total_budget:,.2f} with an average of €{avg_budget:,.2f} per project.",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "recommendation": "Consider targeting higher-margin projects to improve profitability." if avg_budget < 10000 else "Your average project value is good. Focus on maintaining this standard."
=======
                    "recommendation": (
                        "Consider targeting higher-margin projects to improve profitability."
                        if avg_budget < 10000
                        else "Your average project value is good. Focus on maintaining this standard."
                    ),
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
                },
                {
                    "type": "growth",
                    "title": "Growth Opportunities",
                    "content": f"With {active_projects} active projects, you have a good pipeline.",
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
                    "recommendation": "Consider expanding your team to handle more concurrent projects." if active_projects > 5 else "You have capacity for more projects. Focus on marketing and acquisition."
                }
=======
                    "recommendation": (
                        "Consider expanding your team to handle more concurrent projects."
                        if active_projects > 5
                        else "You have capacity for more projects. Focus on marketing and acquisition."
                    ),
                },
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py
            ]

        return jsonify(
            {
                "insights": insights,
                "statistics": {
                    "total_projects": total_projects,
                    "active_projects": active_projects,
                    "completed_projects": completed_projects,
                    "total_budget": total_budget,
                    "average_budget": avg_budget,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    except Exception as e:
        logging.error(f"Project insights error: {e!s}")
        return jsonify({"error": "Failed to generate project insights"}), 500


def get_landscape_stats():
    """Get current landscape architecture statistics"""
    try:
        return {
            "projects": Project.query.count(),
            "clients": Client.query.count(),
            "plants": Plant.query.count(),
            "products": Product.query.count(),
<<<<<<< HEAD:archive/packages/v1.00/backend/routes/ai_assistant.py
            "suppliers": Supplier.query.count()
        }
    except Exception as e:
        logging.error(f"Error getting landscape stats: {e!s}")
        return {
            "projects": 0,
            "clients": 0,
            "plants": 0,
            "products": 0,
            "suppliers": 0
        }
=======
            "suppliers": Supplier.query.count(),
        }
    except Exception as e:
        logging.error(f"Error getting landscape stats: {e!s}")
        return {"projects": 0, "clients": 0, "plants": 0, "products": 0, "suppliers": 0}
>>>>>>> origin/main:packages/v1.00/backend/routes/ai_assistant.py

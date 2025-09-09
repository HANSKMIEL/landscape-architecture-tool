"""
Enhanced Client Presentation System
Provides dynamic, editable presentations for landscape architecture projects.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import io
from pathlib import Path

logger = logging.getLogger(__name__)

# Plant classification constants for maintainable and extensible classification
TREE_CLASSIFICATION_KEYWORDS = ["boom", "tree"]
SHRUB_CLASSIFICATION_KEYWORDS = ["struik", "shrub"]

@dataclass
class PresentationConfig:
    """Configuration for client presentations"""
    theme: str = "modern"
    primary_color: str = "#2563eb"
    secondary_color: str = "#10b981"
    font_family: str = "Inter"
    logo_url: Optional[str] = None
    company_name: str = ""
    language: str = "nl"

@dataclass
class PlantPresentationData:
    """Plant data for presentation"""
    id: int
    name: str
    scientific_name: str
    description: str
    image_url: Optional[str]
    characteristics: Dict[str, str]
    care_instructions: str
    price: float
    quantity: int
    placement_notes: str

@dataclass
class ProjectPresentationData:
    """Project data for presentation"""
    id: int
    name: str
    client_name: str
    description: str
    location: str
    area_size: float
    budget: float
    timeline: str
    design_style: str
    special_requirements: List[str]

@dataclass
class PresentationSlide:
    """Individual presentation slide"""
    id: str
    title: str
    content_type: str  # text, image, plant_grid, timeline, budget
    content: Dict[str, Any]
    editable_fields: List[str]
    order: int

class ClientPresentationGenerator:
    """Generate dynamic client presentations"""
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.templates = self._load_presentation_templates()
        
        # Define contact information constants (configurable)
        self.DEFAULT_CONTACT_INFO = self._get_contact_info_config()
    
    def _get_contact_info_config(self) -> Dict[str, str]:
        """Get contact information from configuration or environment variables"""
        import os
        return {
            "phone": os.getenv('COMPANY_PHONE', "+31 (0)20 123 4567"),
            "email": os.getenv('COMPANY_EMAIL', "info@landscapearchitect.nl"),
            "website": os.getenv('COMPANY_WEBSITE', "www.landscapearchitect.nl")
        }
    
    def _load_presentation_templates(self) -> Dict[str, Dict]:
        """Load presentation templates"""
        return {
            "modern": {
                "name": "Modern Landscape",
                "description": "Clean, contemporary design presentation",
                "slides": [
                    "welcome", "project_overview", "design_concept", 
                    "plant_selection", "timeline", "budget", "next_steps"
                ],
                "colors": {
                    "primary": "#2563eb",
                    "secondary": "#10b981",
                    "accent": "#f59e0b",
                    "background": "#ffffff",
                    "text": "#1f2937"
                }
            },
            "natural": {
                "name": "Natural Garden",
                "description": "Organic, nature-inspired presentation",
                "slides": [
                    "welcome", "site_analysis", "design_philosophy", 
                    "plant_communities", "seasonal_interest", "maintenance", "investment"
                ],
                "colors": {
                    "primary": "#059669",
                    "secondary": "#92400e",
                    "accent": "#dc2626",
                    "background": "#f9fafb",
                    "text": "#374151"
                }
            },
            "formal": {
                "name": "Formal Garden",
                "description": "Classic, structured garden presentation",
                "slides": [
                    "introduction", "design_principles", "hardscape_elements",
                    "formal_plantings", "maintenance_program", "phased_implementation", "conclusion"
                ],
                "colors": {
                    "primary": "#1e40af",
                    "secondary": "#7c2d12",
                    "accent": "#b91c1c",
                    "background": "#ffffff",
                    "text": "#111827"
                }
            }
        }
    
    def _is_plant_type(self, plant: PlantPresentationData, keywords: List[str]) -> bool:
        """Helper method to classify plants by type using keywords"""
        plant_name_lower = plant.name.lower()
        plant_type_lower = plant.characteristics.get("type", "").lower()
        
        return any(keyword in plant_name_lower or keyword in plant_type_lower for keyword in keywords)
    
    def create_presentation(self, project_id: int, template: str = "modern", 
                          config: Optional[PresentationConfig] = None) -> Dict:
        """Create a new client presentation"""
        try:
            # Get project data
            project_data = self._get_project_data(project_id)
            if not project_data:
                raise ValueError(f"Project {project_id} not found")
            
            # Get plant data
            plant_data = self._get_project_plants(project_id)
            
            # Use provided config or create default
            if not config:
                config = PresentationConfig(theme=template)
            
            # Generate slides
            slides = self._generate_slides(project_data, plant_data, template, config)
            
            # Create presentation metadata
            presentation = {
                "id": f"pres_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "project_id": project_id,
                "template": template,
                "config": asdict(config),
                "created_at": datetime.now().isoformat(),
                "slides": slides,
                "editable": True,
                "version": "1.0"
            }
            
            # Save to database
            self._save_presentation(presentation)
            
            return presentation
            
        except Exception as e:
            logger.error(f"Error creating presentation: {e}")
            raise
    
    def _get_project_data(self, project_id: int) -> Optional[ProjectPresentationData]:
        """Get project data from database"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT p.*, c.name as client_name, c.contact_info
                FROM projects p
                LEFT JOIN clients c ON p.client_id = c.id
                WHERE p.id = %s
            """, (project_id,))
            
            result = cursor.fetchone()
            if result:
                return ProjectPresentationData(
                    id=result[0],
                    name=result[1],
                    client_name=result[-2] or "Client",
                    description=result[2] or "",
                    location=result[3] or "",
                    area_size=result[4] or 0,
                    budget=result[5] or 0,
                    timeline=result[6] or "",
                    design_style=result[7] or "Modern",
                    special_requirements=json.loads(result[8] or "[]")
                )
        except Exception as e:
            logger.error(f"Error getting project data: {e}")
        return None
    
    def _get_project_plants(self, project_id: int) -> List[PlantPresentationData]:
        """Get plant data for project"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT p.*, pp.quantity, pp.placement_notes, pp.price_override
                FROM plants p
                JOIN project_plants pp ON p.id = pp.plant_id
                WHERE pp.project_id = %s
                ORDER BY pp.placement_order
            """, (project_id,))
            
            plants = []
            for row in cursor.fetchall():
                plants.append(PlantPresentationData(
                    id=row[0],
                    name=row[1],
                    scientific_name=row[2] or "",
                    description=row[3] or "",
                    image_url=row[4],
                    characteristics=json.loads(row[5] or "{}"),
                    care_instructions=row[6] or "",
                    price=row[-1] or row[7] or 0,
                    quantity=row[-3] or 1,
                    placement_notes=row[-2] or ""
                ))
            return plants
        except Exception as e:
            logger.error(f"Error getting project plants: {e}")
            return []
    
    def _generate_slides(self, project: ProjectPresentationData, 
                        plants: List[PlantPresentationData],
                        template: str, config: PresentationConfig) -> List[PresentationSlide]:
        """Generate presentation slides"""
        template_config = self.templates.get(template, self.templates["modern"])
        slides = []
        
        slide_generators = {
            "welcome": self._generate_welcome_slide,
            "introduction": self._generate_welcome_slide,
            "project_overview": self._generate_project_overview_slide,
            "site_analysis": self._generate_site_analysis_slide,
            "design_concept": self._generate_design_concept_slide,
            "design_philosophy": self._generate_design_philosophy_slide,
            "design_principles": self._generate_design_principles_slide,
            "plant_selection": self._generate_plant_selection_slide,
            "plant_communities": self._generate_plant_communities_slide,
            "formal_plantings": self._generate_formal_plantings_slide,
            "hardscape_elements": self._generate_hardscape_slide,
            "seasonal_interest": self._generate_seasonal_slide,
            "timeline": self._generate_timeline_slide,
            "phased_implementation": self._generate_timeline_slide,
            "budget": self._generate_budget_slide,
            "investment": self._generate_budget_slide,
            "maintenance": self._generate_maintenance_slide,
            "maintenance_program": self._generate_maintenance_slide,
            "next_steps": self._generate_next_steps_slide,
            "conclusion": self._generate_next_steps_slide
        }
        
        for i, slide_type in enumerate(template_config["slides"]):
            generator = slide_generators.get(slide_type)
            if generator:
                slide = generator(project, plants, config, i)
                slides.append(slide)
        
        return slides
    
    def _generate_welcome_slide(self, project: ProjectPresentationData, 
                               plants: List[PlantPresentationData],
                               config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate welcome slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Welkom" if config.language == "nl" else "Welcome",
            content_type="welcome",
            content={
                "project_name": project.name,
                "client_name": project.client_name,
                "company_name": config.company_name,
                "date": datetime.now().strftime("%d %B %Y"),
                "logo_url": config.logo_url,
                "subtitle": f"Landschapsontwerp voor {project.location}" if config.language == "nl" 
                           else f"Landscape Design for {project.location}"
            },
            editable_fields=["project_name", "client_name", "subtitle"],
            order=order
        )
    
    def _generate_project_overview_slide(self, project: ProjectPresentationData,
                                       plants: List[PlantPresentationData],
                                       config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate project overview slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Project Overzicht" if config.language == "nl" else "Project Overview",
            content_type="project_overview",
            content={
                "description": project.description,
                "location": project.location,
                "area_size": project.area_size,
                "design_style": project.design_style,
                "special_requirements": project.special_requirements,
                "timeline": project.timeline,
                "key_features": [
                    "Duurzame plantkeuze" if config.language == "nl" else "Sustainable plant selection",
                    "Seizoensinteresse" if config.language == "nl" else "Year-round interest",
                    "Onderhoudsarm ontwerp" if config.language == "nl" else "Low-maintenance design"
                ]
            },
            editable_fields=["description", "key_features", "special_requirements"],
            order=order
        )
    
    def _generate_site_analysis_slide(self, project: ProjectPresentationData,
                                    plants: List[PlantPresentationData],
                                    config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate site analysis slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Locatie Analyse" if config.language == "nl" else "Site Analysis",
            content_type="site_analysis",
            content={
                "soil_conditions": "Leemgrond, goed gedraineerd" if config.language == "nl" 
                                 else "Loamy soil, well-drained",
                "sun_exposure": "Gedeeltelijk zon/schaduw" if config.language == "nl" 
                              else "Partial sun/shade",
                "existing_features": [
                    "Bestaande eikenboom" if config.language == "nl" else "Existing oak tree",
                    "Natuurstenen muur" if config.language == "nl" else "Natural stone wall"
                ],
                "challenges": [
                    "Beperkte toegang" if config.language == "nl" else "Limited access",
                    "Hellend terrein" if config.language == "nl" else "Sloping terrain"
                ],
                "opportunities": [
                    "Mooi uitzicht" if config.language == "nl" else "Beautiful views",
                    "Beschutte ligging" if config.language == "nl" else "Sheltered location"
                ]
            },
            editable_fields=["soil_conditions", "sun_exposure", "existing_features", "challenges", "opportunities"],
            order=order
        )
    
    def _generate_design_concept_slide(self, project: ProjectPresentationData,
                                     plants: List[PlantPresentationData],
                                     config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate design concept slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Ontwerp Concept" if config.language == "nl" else "Design Concept",
            content_type="design_concept",
            content={
                "concept_description": project.description,
                "design_principles": [
                    "Harmonie met bestaande architectuur" if config.language == "nl" 
                    else "Harmony with existing architecture",
                    "Duurzame materialen en planten" if config.language == "nl" 
                    else "Sustainable materials and plants",
                    "Functionele en esthetische waarde" if config.language == "nl" 
                    else "Functional and aesthetic value"
                ],
                "inspiration": project.design_style,
                "mood_images": []  # Would be populated with actual images
            },
            editable_fields=["concept_description", "design_principles", "inspiration"],
            order=order
        )
    
    def _generate_design_philosophy_slide(self, project: ProjectPresentationData,
                                        plants: List[PlantPresentationData],
                                        config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate design philosophy slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Ontwerp Filosofie" if config.language == "nl" else "Design Philosophy",
            content_type="design_philosophy",
            content={
                "philosophy": "Werken met de natuur, niet ertegen" if config.language == "nl" 
                            else "Working with nature, not against it",
                "approach": [
                    "Inheemse plantensoorten" if config.language == "nl" else "Native plant species",
                    "Natuurlijke groeipatronen" if config.language == "nl" else "Natural growth patterns",
                    "Ecologische verbindingen" if config.language == "nl" else "Ecological connections"
                ],
                "sustainability": [
                    "Regenwater opvang" if config.language == "nl" else "Rainwater harvesting",
                    "Biodiversiteit bevordering" if config.language == "nl" else "Biodiversity enhancement",
                    "Minimaal onderhoud" if config.language == "nl" else "Minimal maintenance"
                ]
            },
            editable_fields=["philosophy", "approach", "sustainability"],
            order=order
        )
    
    def _generate_design_principles_slide(self, project: ProjectPresentationData,
                                        plants: List[PlantPresentationData],
                                        config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate design principles slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Ontwerp Principes" if config.language == "nl" else "Design Principles",
            content_type="design_principles",
            content={
                "principles": [
                    {
                        "title": "Symmetrie" if config.language == "nl" else "Symmetry",
                        "description": "Formele balans en structuur" if config.language == "nl" 
                                     else "Formal balance and structure"
                    },
                    {
                        "title": "Hiërarchie" if config.language == "nl" else "Hierarchy",
                        "description": "Duidelijke ruimtelijke ordening" if config.language == "nl" 
                                     else "Clear spatial organization"
                    },
                    {
                        "title": "Materiaal Keuze" if config.language == "nl" else "Material Selection",
                        "description": "Tijdloze en duurzame materialen" if config.language == "nl" 
                                     else "Timeless and sustainable materials"
                    }
                ]
            },
            editable_fields=["principles"],
            order=order
        )
    
    def _generate_plant_selection_slide(self, project: ProjectPresentationData,
                                      plants: List[PlantPresentationData],
                                      config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate plant selection slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Plantenselectie" if config.language == "nl" else "Plant Selection",
            content_type="plant_grid",
            content={
                "plants": [asdict(plant) for plant in plants[:6]],  # Show top 6 plants
                "selection_criteria": [
                    "Klimaatbestendigheid" if config.language == "nl" else "Climate resilience",
                    "Seizoensinteresse" if config.language == "nl" else "Seasonal interest",
                    "Onderhoudsgemak" if config.language == "nl" else "Ease of maintenance",
                    "Ecologische waarde" if config.language == "nl" else "Ecological value"
                ],
                "total_species": len(plants)
            },
            editable_fields=["plants", "selection_criteria"],
            order=order
        )
    
    def _generate_plant_communities_slide(self, project: ProjectPresentationData,
                                        plants: List[PlantPresentationData],
                                        config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate plant communities slide"""
        # Use global constants directly for plant classification
        
        # Group plants by type/layer using robust classification
        trees = [p for p in plants if self._is_plant_type(p, TREE_CLASSIFICATION_KEYWORDS)]
        shrubs = [p for p in plants if self._is_plant_type(p, SHRUB_CLASSIFICATION_KEYWORDS)]
        perennials = [p for p in plants if p not in trees and p not in shrubs]
        
        return PresentationSlide(
            id=f"slide_{order}",
            title="Plantengemeenschappen" if config.language == "nl" else "Plant Communities",
            content_type="plant_communities",
            content={
                "communities": [
                    {
                        "name": "Boomlaag" if config.language == "nl" else "Canopy Layer",
                        "plants": [asdict(p) for p in trees],
                        "function": "Structuur en schaduw" if config.language == "nl" else "Structure and shade"
                    },
                    {
                        "name": "Struiklaag" if config.language == "nl" else "Shrub Layer",
                        "plants": [asdict(p) for p in shrubs],
                        "function": "Privacy en habitat" if config.language == "nl" else "Privacy and habitat"
                    },
                    {
                        "name": "Kruidlaag" if config.language == "nl" else "Herbaceous Layer",
                        "plants": [asdict(p) for p in perennials],
                        "function": "Kleur en textuur" if config.language == "nl" else "Color and texture"
                    }
                ]
            },
            editable_fields=["communities"],
            order=order
        )
    
    def _generate_formal_plantings_slide(self, project: ProjectPresentationData,
                                       plants: List[PlantPresentationData],
                                       config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate formal plantings slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Formele Beplanting" if config.language == "nl" else "Formal Plantings",
            content_type="formal_plantings",
            content={
                "hedge_plants": [p for p in plants if "heg" in p.placement_notes.lower() or "hedge" in p.placement_notes.lower()],
                "specimen_plants": [p for p in plants if "solitair" in p.placement_notes.lower() or "specimen" in p.placement_notes.lower()],
                "topiary_options": [
                    "Buxus bollen" if config.language == "nl" else "Boxwood spheres",
                    "Taxus piramides" if config.language == "nl" else "Yew pyramids"
                ],
                "maintenance_schedule": "Tweemaal per jaar snoeien" if config.language == "nl" else "Pruning twice yearly"
            },
            editable_fields=["hedge_plants", "specimen_plants", "topiary_options", "maintenance_schedule"],
            order=order
        )
    
    def _generate_hardscape_slide(self, project: ProjectPresentationData,
                                plants: List[PlantPresentationData],
                                config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate hardscape elements slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Verharding & Structuren" if config.language == "nl" else "Hardscape Elements",
            content_type="hardscape",
            content={
                "materials": [
                    "Natuursteen bestrating" if config.language == "nl" else "Natural stone paving",
                    "Cortenstaal randen" if config.language == "nl" else "Corten steel edging",
                    "Houten pergola" if config.language == "nl" else "Timber pergola"
                ],
                "features": [
                    "Waterpartij" if config.language == "nl" else "Water feature",
                    "Zitgelegenheid" if config.language == "nl" else "Seating areas",
                    "Verlichting" if config.language == "nl" else "Lighting"
                ],
                "sustainability": [
                    "Doorlatende verharding" if config.language == "nl" else "Permeable paving",
                    "Gerecyclede materialen" if config.language == "nl" else "Recycled materials",
                    "LED verlichting" if config.language == "nl" else "LED lighting"
                ]
            },
            editable_fields=["materials", "features", "sustainability"],
            order=order
        )
    
    def _generate_seasonal_slide(self, project: ProjectPresentationData,
                               plants: List[PlantPresentationData],
                               config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate seasonal interest slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Seizoensinteresse" if config.language == "nl" else "Seasonal Interest",
            content_type="seasonal",
            content={
                "seasons": [
                    {
                        "name": "Lente" if config.language == "nl" else "Spring",
                        "highlights": [
                            "Bloeiende bollen" if config.language == "nl" else "Flowering bulbs",
                            "Verse uitloop" if config.language == "nl" else "Fresh growth"
                        ],
                        "plants": [p.name for p in plants if "lente" in p.characteristics.get("blooming_season", "").lower()][:3]
                    },
                    {
                        "name": "Zomer" if config.language == "nl" else "Summer",
                        "highlights": [
                            "Kleurrijke bloei" if config.language == "nl" else "Colorful blooms",
                            "Weelderige groei" if config.language == "nl" else "Lush growth"
                        ],
                        "plants": [p.name for p in plants if "zomer" in p.characteristics.get("blooming_season", "").lower()][:3]
                    },
                    {
                        "name": "Herfst" if config.language == "nl" else "Autumn",
                        "highlights": [
                            "Herfstkleuren" if config.language == "nl" else "Fall colors",
                            "Zaaddozen" if config.language == "nl" else "Seed heads"
                        ],
                        "plants": [p.name for p in plants if "herfst" in p.characteristics.get("blooming_season", "").lower()][:3]
                    },
                    {
                        "name": "Winter" if config.language == "nl" else "Winter",
                        "highlights": [
                            "Structuur" if config.language == "nl" else "Structure",
                            "Wintergroen" if config.language == "nl" else "Evergreen foliage"
                        ],
                        "plants": [p.name for p in plants if "winter" in p.characteristics.get("blooming_season", "").lower()][:3]
                    }
                ]
            },
            editable_fields=["seasons"],
            order=order
        )
    
    def _generate_timeline_slide(self, project: ProjectPresentationData,
                               plants: List[PlantPresentationData],
                               config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate timeline slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Tijdlijn" if config.language == "nl" else "Timeline",
            content_type="timeline",
            content={
                "phases": [
                    {
                        "name": "Fase 1: Voorbereiding" if config.language == "nl" else "Phase 1: Preparation",
                        "duration": "2 weken" if config.language == "nl" else "2 weeks",
                        "tasks": [
                            "Grondvoorbereiding" if config.language == "nl" else "Soil preparation",
                            "Verharding aanleggen" if config.language == "nl" else "Install hardscape"
                        ]
                    },
                    {
                        "name": "Fase 2: Beplanting" if config.language == "nl" else "Phase 2: Planting",
                        "duration": "1 week" if config.language == "nl" else "1 week",
                        "tasks": [
                            "Bomen planten" if config.language == "nl" else "Plant trees",
                            "Struiken en vaste planten" if config.language == "nl" else "Shrubs and perennials"
                        ]
                    },
                    {
                        "name": "Fase 3: Afwerking" if config.language == "nl" else "Phase 3: Finishing",
                        "duration": "1 week" if config.language == "nl" else "1 week",
                        "tasks": [
                            "Mulchen" if config.language == "nl" else "Mulching",
                            "Irrigatie installeren" if config.language == "nl" else "Install irrigation"
                        ]
                    }
                ],
                "total_duration": project.timeline or "4 weken",
                "best_planting_time": "Maart-Mei, September-November" if config.language == "nl" 
                                    else "March-May, September-November"
            },
            editable_fields=["phases", "total_duration", "best_planting_time"],
            order=order
        )
    
    def _generate_budget_slide(self, project: ProjectPresentationData,
                             plants: List[PlantPresentationData],
                             config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate budget slide"""
        plant_cost = sum(p.price * p.quantity for p in plants)
        hardscape_cost = project.budget * 0.4  # Estimate 40% for hardscape
        labor_cost = project.budget * 0.3      # Estimate 30% for labor
        other_cost = project.budget * 0.1      # Estimate 10% for other
        
        return PresentationSlide(
            id=f"slide_{order}",
            title="Budget" if config.language == "nl" else "Investment",
            content_type="budget",
            content={
                "categories": [
                    {
                        "name": "Planten" if config.language == "nl" else "Plants",
                        "amount": plant_cost,
                        "percentage": (plant_cost / project.budget * 100) if project.budget > 0 else 20
                    },
                    {
                        "name": "Verharding" if config.language == "nl" else "Hardscape",
                        "amount": hardscape_cost,
                        "percentage": 40
                    },
                    {
                        "name": "Arbeid" if config.language == "nl" else "Labor",
                        "amount": labor_cost,
                        "percentage": 30
                    },
                    {
                        "name": "Overig" if config.language == "nl" else "Other",
                        "amount": other_cost,
                        "percentage": 10
                    }
                ],
                "total_budget": project.budget,
                "payment_schedule": [
                    "30% bij opdracht" if config.language == "nl" else "30% on contract",
                    "40% bij start werkzaamheden" if config.language == "nl" else "40% on commencement",
                    "30% bij oplevering" if config.language == "nl" else "30% on completion"
                ],
                "warranty": "2 jaar garantie op planten" if config.language == "nl" else "2 year plant warranty"
            },
            editable_fields=["categories", "payment_schedule", "warranty"],
            order=order
        )
    
    def _generate_maintenance_slide(self, project: ProjectPresentationData,
                                  plants: List[PlantPresentationData],
                                  config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate maintenance slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Onderhoud" if config.language == "nl" else "Maintenance",
            content_type="maintenance",
            content={
                "maintenance_level": "Laag tot gemiddeld" if config.language == "nl" else "Low to moderate",
                "seasonal_tasks": [
                    {
                        "season": "Lente" if config.language == "nl" else "Spring",
                        "tasks": [
                            "Snoeien" if config.language == "nl" else "Pruning",
                            "Bemesten" if config.language == "nl" else "Fertilizing",
                            "Mulchen" if config.language == "nl" else "Mulching"
                        ]
                    },
                    {
                        "season": "Zomer" if config.language == "nl" else "Summer",
                        "tasks": [
                            "Begieten" if config.language == "nl" else "Watering",
                            "Onkruid wieden" if config.language == "nl" else "Weeding",
                            "Uitgebloeide bloemen verwijderen" if config.language == "nl" else "Deadheading"
                        ]
                    },
                    {
                        "season": "Herfst" if config.language == "nl" else "Autumn",
                        "tasks": [
                            "Bladeren opruimen" if config.language == "nl" else "Leaf cleanup",
                            "Planten terugsnoeien" if config.language == "nl" else "Cut back perennials",
                            "Winterbescherming" if config.language == "nl" else "Winter protection"
                        ]
                    },
                    {
                        "season": "Winter" if config.language == "nl" else "Winter",
                        "tasks": [
                            "Plannen voor volgend jaar" if config.language == "nl" else "Plan for next year",
                            "Gereedschap onderhouden" if config.language == "nl" else "Tool maintenance"
                        ]
                    }
                ],
                "annual_cost": project.budget * 0.05,  # Estimate 5% of project cost annually
                "maintenance_service": "Optioneel onderhoudscontract beschikbaar" if config.language == "nl" 
                                     else "Optional maintenance contract available"
            },
            editable_fields=["maintenance_level", "seasonal_tasks", "annual_cost", "maintenance_service"],
            order=order
        )
    
    def _generate_next_steps_slide(self, project: ProjectPresentationData,
                                 plants: List[PlantPresentationData],
                                 config: PresentationConfig, order: int) -> PresentationSlide:
        """Generate next steps slide"""
        return PresentationSlide(
            id=f"slide_{order}",
            title="Volgende Stappen" if config.language == "nl" else "Next Steps",
            content_type="next_steps",
            content={
                "steps": [
                    {
                        "title": "Ontwerp Goedkeuring" if config.language == "nl" else "Design Approval",
                        "description": "Bevestiging van het definitieve ontwerp" if config.language == "nl" 
                                     else "Confirmation of final design",
                        "timeline": "1 week" if config.language == "nl" else "1 week"
                    },
                    {
                        "title": "Contract Ondertekening" if config.language == "nl" else "Contract Signing",
                        "description": "Formalisering van de opdracht" if config.language == "nl" 
                                     else "Formalization of the commission",
                        "timeline": "1 week" if config.language == "nl" else "1 week"
                    },
                    {
                        "title": "Uitvoering" if config.language == "nl" else "Implementation",
                        "description": "Realisatie van het ontwerp" if config.language == "nl" 
                                     else "Realization of the design",
                        "timeline": project.timeline or "4 weken"
                    }
                ],
                "contact_info": {
                    "company": config.company_name,
                    "phone": getattr(config, 'contact_phone', self.DEFAULT_CONTACT_INFO["phone"]),
                    "email": getattr(config, 'contact_email', self.DEFAULT_CONTACT_INFO["email"]),
                    "website": getattr(config, 'contact_website', self.DEFAULT_CONTACT_INFO["website"])
                },
                "call_to_action": "Laten we uw droomtuin realiseren!" if config.language == "nl" 
                                else "Let's create your dream garden!"
            },
            editable_fields=["steps", "contact_info", "call_to_action"],
            order=order
        )
    
    def _save_presentation(self, presentation: Dict) -> None:
        """Save presentation to database"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO presentations (id, project_id, template, config, slides, created_at, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    config = EXCLUDED.config,
                    slides = EXCLUDED.slides,
                    updated_at = NOW()
            """, (
                presentation["id"],
                presentation["project_id"],
                presentation["template"],
                json.dumps(presentation["config"]),
                json.dumps(presentation["slides"]),
                presentation["created_at"],
                presentation["version"]
            ))
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving presentation: {e}")
            self.db.rollback()
    
    def update_slide_content(self, presentation_id: str, slide_id: str, 
                           field: str, value: Any) -> bool:
        """Update specific field in a slide"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT slides FROM presentations WHERE id = %s
            """, (presentation_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            slides = json.loads(result[0])
            
            # Find and update the slide
            for slide in slides:
                if slide["id"] == slide_id:
                    if field in slide["editable_fields"]:
                        slide["content"][field] = value
                        break
            else:
                return False
            
            # Save updated slides
            cursor.execute("""
                UPDATE presentations 
                SET slides = %s, updated_at = NOW()
                WHERE id = %s
            """, (json.dumps(slides), presentation_id))
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating slide content: {e}")
            self.db.rollback()
            return False

def create_presentation_service(database_connection):
    """Factory function to create presentation service"""
    return ClientPresentationGenerator(database_connection)

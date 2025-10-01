from datetime import date

from src.models.landscape import Client, Plant, Product, Project, Supplier
from src.models.user import db


def initialize_sample_data():
    """Initialize database with realistic Dutch landscape architecture sample data"""

    # Check if data already exists
    if Supplier.query.first():
        print("Sample data already exists, skipping initialization")
        return

    print("Initializing sample data...")

    # Create Suppliers
    suppliers_data = [
        {
            "name": "Boomkwekerij Peters",
            "contact_person": "Jan Peters",
            "email": "info@boomkwekerijpeters.nl",
            "phone": "+31 20 123 4567",
            "address": "Kwekerslaan 15",
            "city": "Aalsmeer",
            "postal_code": "1431 AB",
            "website": "www.boomkwekerijpeters.nl",
            "notes": "Specialist in native Dutch trees and shrubs",
        },
        {
            "name": "Van der Berg Tuinmaterialen",
            "contact_person": "Maria van der Berg",
            "email": "verkoop@vdberg-tuin.nl",
            "phone": "+31 30 987 6543",
            "address": "Industrieweg 42",
            "city": "Utrecht",
            "postal_code": "3542 AD",
            "website": "www.vdberg-tuinmaterialen.nl",
            "notes": "Complete range of garden materials and hardscaping supplies",
        },
        {
            "name": "GreenScape Supplies",
            "contact_person": "Erik Janssen",
            "email": "orders@greenscape.nl",
            "phone": "+31 40 555 7890",
            "address": "Groenstraat 88",
            "city": "Eindhoven",
            "postal_code": "5611 CL",
            "website": "www.greenscape-supplies.nl",
            "notes": "Professional landscape supplies and irrigation systems",
        },
    ]

    suppliers = []
    for supplier_data in suppliers_data:
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
        suppliers.append(supplier)

    db.session.flush()  # Get IDs for suppliers

    # Create Plants
    plants_data = [
        {
            "name": "Acer platanoides",
            "scientific_name": "Acer platanoides",
            "common_name": "Norway Maple",
            "category": "Tree",
            "sun_requirements": "Full Sun",
            "water_requirements": "Medium",
            "soil_type": "Well-drained, fertile soil",
            "hardiness_zone": "3-7",
            "mature_height": "15-20m",
            "mature_width": "12-15m",
            "bloom_time": "April-May",
            "bloom_color": "Yellow-green",
            "foliage_color": "Green, yellow fall color",
            "maintenance_level": "Low",
            "native_to_netherlands": False,
            "deer_resistant": True,
            "drought_tolerant": False,
            "attracts_pollinators": True,
            "price": 45.50,
            "supplier_id": suppliers[0].id,
            "notes": "Excellent shade tree for urban environments",
        },
        {
            "name": "Lavandula angustifolia",
            "scientific_name": "Lavandula angustifolia",
            "common_name": "English Lavender",
            "category": "Perennial",
            "sun_requirements": "Full Sun",
            "water_requirements": "Low",
            "soil_type": "Well-drained, alkaline soil",
            "hardiness_zone": "5-9",
            "mature_height": "30-60cm",
            "mature_width": "30-45cm",
            "bloom_time": "June-August",
            "bloom_color": "Purple",
            "foliage_color": "Gray-green",
            "maintenance_level": "Low",
            "native_to_netherlands": False,
            "deer_resistant": True,
            "drought_tolerant": True,
            "attracts_pollinators": True,
            "price": 8.95,
            "supplier_id": suppliers[0].id,
            "notes": "Fragrant herb perfect for borders and herb gardens",
        },
        {
            "name": "Fagus sylvatica",
            "scientific_name": "Fagus sylvatica",
            "common_name": "European Beech",
            "category": "Tree",
            "sun_requirements": "Partial Sun",
            "water_requirements": "Medium",
            "soil_type": "Well-drained, fertile soil",
            "hardiness_zone": "4-7",
            "mature_height": "20-30m",
            "mature_width": "15-20m",
            "bloom_time": "April-May",
            "bloom_color": "Inconspicuous",
            "foliage_color": "Green, bronze fall color",
            "maintenance_level": "Low",
            "native_to_netherlands": True,
            "deer_resistant": False,
            "drought_tolerant": False,
            "attracts_pollinators": False,
            "price": 65.00,
            "supplier_id": suppliers[0].id,
            "notes": "Native Dutch tree, excellent for hedging and specimen planting",
        },
        {
            "name": "Hydrangea macrophylla",
            "scientific_name": "Hydrangea macrophylla",
            "common_name": "Bigleaf Hydrangea",
            "category": "Shrub",
            "sun_requirements": "Partial Sun",
            "water_requirements": "High",
            "soil_type": "Moist, well-drained soil",
            "hardiness_zone": "6-9",
            "mature_height": "1-2m",
            "mature_width": "1-2m",
            "bloom_time": "June-September",
            "bloom_color": "Blue, pink, white",
            "foliage_color": "Green",
            "maintenance_level": "Medium",
            "native_to_netherlands": False,
            "deer_resistant": False,
            "drought_tolerant": False,
            "attracts_pollinators": True,
            "price": 24.95,
            "supplier_id": suppliers[0].id,
            "notes": "Popular flowering shrub, color varies with soil pH",
        },
    ]

    for plant_data in plants_data:
        plant = Plant(**plant_data)
        db.session.add(plant)

    # Create Products
    products_data = [
        {
            "name": "Natural Stone Paving - Bluestone",
            "category": "Hardscaping",
            "subcategory": "Paving",
            "description": "Premium bluestone paving stones for patios and walkways",
            "price": 45.50,
            "unit": "m²",
            "sku": "BS-PAV-001",
            "supplier_id": suppliers[1].id,
            "in_stock": True,
            "minimum_order": 10,
            "delivery_time": "2-3 weeks",
            "specifications": "Thickness: 3cm, Various sizes available",
        },
        {
            "name": "Organic Compost - Premium Mix",
            "category": "Soil & Amendments",
            "subcategory": "Compost",
            "description": "High-quality organic compost for soil improvement",
            "price": 35.00,
            "unit": "m³",
            "sku": "COM-ORG-001",
            "supplier_id": suppliers[1].id,
            "in_stock": True,
            "minimum_order": 1,
            "delivery_time": "1 week",
            "specifications": "pH 6.5-7.0, Rich in organic matter",
        },
        {
            "name": "Drip Irrigation Kit - Professional",
            "category": "Irrigation",
            "subcategory": "Drip Systems",
            "description": "Complete drip irrigation system for efficient watering",
            "price": 125.00,
            "unit": "kit",
            "sku": "IRR-DRP-001",
            "supplier_id": suppliers[2].id,
            "in_stock": True,
            "minimum_order": 1,
            "delivery_time": "1-2 weeks",
            "specifications": ("Covers up to 50m², includes timer and pressure regulator"),
        },
    ]

    for product_data in products_data:
        product = Product(**product_data)
        db.session.add(product)

    # Create Clients
    clients_data = [
        {
            "name": "Familie Jansen",
            "type": "Individual",
            "contact_person": "Peter Jansen",
            "email": "p.jansen@email.nl",
            "phone": "+31 6 1234 5678",
            "address": "Tulpenstraat 25",
            "city": "Amsterdam",
            "postal_code": "1012 AB",
            "notes": "Looking for low-maintenance garden design",
        },
        {
            "name": "Gemeente Rotterdam",
            "type": "Municipality",
            "contact_person": "Sandra de Vries",
            "email": "s.devries@rotterdam.nl",
            "phone": "+31 10 123 4567",
            "address": "Stadhuis, Coolsingel 40",
            "city": "Rotterdam",
            "postal_code": "3011 AD",
            "notes": "Public park renovation project",
        },
        {
            "name": "Hotel De Gouden Leeuw",
            "type": "Business",
            "contact_person": "Mark van Dijk",
            "email": "info@goudenleeuw.nl",
            "phone": "+31 20 987 6543",
            "address": "Herengracht 123",
            "city": "Amsterdam",
            "postal_code": "1015 BE",
            "notes": "Boutique hotel seeking elegant courtyard design",
        },
    ]

    clients = []
    for client_data in clients_data:
        client = Client(**client_data)
        db.session.add(client)
        clients.append(client)

    db.session.flush()  # Get IDs for clients

    # Create Projects
    projects_data = [
        {
            "name": "Jansen Family Garden Renovation",
            "description": (
                "Complete renovation of backyard garden with focus on " "native plants and low maintenance"
            ),
            "client_id": clients[0].id,
            "status": "In Progress",
            "project_type": "Residential Garden",
            "site_area": 150.0,
            "budget": 8500.00,
            "start_date": date(2024, 3, 15),
            "end_date": date(2024, 5, 30),
            "location": "Amsterdam, North Holland",
            "soil_conditions": "Clay soil, good drainage needed",
            "sun_exposure": "Partial Sun",
            "special_requirements": ("Pet-friendly plants, child-safe design"),
        },
        {
            "name": "Vondelpark East Entrance Redesign",
            "description": ("Redesign of the eastern entrance to Vondelpark " "with sustainable landscaping"),
            "client_id": clients[1].id,
            "status": "Planning",
            "project_type": "Public Space",
            "site_area": 500.0,
            "budget": 45000.00,
            "start_date": date(2024, 6, 1),
            "end_date": date(2024, 9, 15),
            "location": "Amsterdam, Vondelpark",
            "soil_conditions": "Urban soil, compacted areas",
            "sun_exposure": "Full Sun",
            "special_requirements": ("High foot traffic resistance, native species priority"),
        },
        {
            "name": "Hotel Courtyard Garden",
            "description": ("Elegant courtyard garden design for boutique hotel " "with year-round interest"),
            "client_id": clients[2].id,
            "status": "Completed",
            "project_type": "Commercial Landscape",
            "site_area": 75.0,
            "budget": 12000.00,
            "start_date": date(2024, 1, 10),
            "end_date": date(2024, 2, 28),
            "location": "Amsterdam, Herengracht",
            "soil_conditions": "Container planting, good drainage",
            "sun_exposure": "Partial Sun",
            "special_requirements": "Elegant design, low maintenance, seasonal color",
        },
    ]

    for project_data in projects_data:
        project = Project(**project_data)
        db.session.add(project)

    # Commit all data
    db.session.commit()
    print("Sample data initialized successfully!")

    # Print summary
    print(f"Created {len(suppliers_data)} suppliers")
    print(f"Created {len(plants_data)} plants")
    print(f"Created {len(products_data)} products")
    print(f"Created {len(clients_data)} clients")
    print(f"Created {len(projects_data)} projects")

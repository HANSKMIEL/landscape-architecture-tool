import logging

from src.models.landscape import Client, Plant, Product, Project, Supplier
from src.models.user import User, db

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database tables"""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e!s}")
        raise


def populate_sample_data():
    """Populate database with sample data if empty"""
    try:
        # Always check and create users if they don't exist
        if User.query.count() == 0:
            logger.info("Creating sample users...")
            users_data = [
                {"username": "admin", "email": "admin@landscape.com", "password": "admin123", "role": "admin"},
                {
                    "username": "employee",
                    "email": "employee@landscape.com",
                    "password": "employee123",
                    "role": "employee",
                },
                {"username": "client", "email": "client@landscape.com", "password": "client123", "role": "client"},
            ]

            for user_data in users_data:
                user = User(username=user_data["username"], email=user_data["email"], role=user_data["role"])
                user.set_password(user_data["password"])
                db.session.add(user)

            db.session.commit()
            logger.info("Sample users created successfully!")

        # Check if business data already exists
        if Supplier.query.count() > 0:
            logger.info("Sample business data already exists, skipping initialization")
            return

        logger.info("Populating database with sample business data...")

        # Sample Suppliers
        suppliers_data = [
            {
                "name": "Boomkwekerij Peters",
                "contact_person": "Jan Peters",
                "email": "jan@boomkwekerijpeters.nl",
                "phone": "+31 6 12345678",
                "address": "Kwekerslaan 15",
                "city": "Boskoop",
                "postal_code": "2771 AA",
                "specialization": "Bomen en heesters",
                "website": "www.boomkwekerijpeters.nl",
                "notes": "Gespecialiseerd in inheemse boomsoorten",
            },
            {
                "name": "Tuincentrum De Groene Vingers",
                "contact_person": "Maria van der Berg",
                "email": "maria@groenevinger.nl",
                "phone": "+31 20 7654321",
                "address": "Tuinstraat 88",
                "city": "Amsterdam",
                "postal_code": "1012 AB",
                "specialization": "Vaste planten en seizoensplanten",
                "website": "www.groenevinger.nl",
                "notes": "Breed assortiment vaste planten",
            },
            {
                "name": "Kwekerij Groen & Co",
                "contact_person": "Piet Groen",
                "email": "info@groenco.nl",
                "phone": "+31 30 9876543",
                "address": "Plantsoenweg 42",
                "city": "Utrecht",
                "postal_code": "3521 XY",
                "specialization": "Biologische planten en kruiden",
                "website": "www.groenco.nl",
                "notes": "Gecertificeerd biologisch",
            },
        ]

        suppliers = []
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
            suppliers.append(supplier)

        db.session.flush()  # Flush to get IDs

        # Sample Plants
        plants_data = [
            {
                "name": "Acer platanoides",
                "common_name": "Noorse esdoorn",
                "category": "Boom",
                "height_min": 15.0,
                "height_max": 25.0,
                "width_min": 8.0,
                "width_max": 15.0,
                "sun_requirements": "Zon tot halfschaduw",
                "soil_type": "Alle grondsoorten",
                "water_needs": "Matig",
                "hardiness_zone": "4-7",
                "bloom_time": "April-Mei",
                "bloom_color": "Geel-groen",
                "foliage_color": "Groen, geel in herfst",
                "native": True,
                "supplier_id": suppliers[0].id,
                "price": 45.50,
                "availability": "Voorradig",
                "planting_season": "Herfst/Voorjaar",
                "maintenance": "Laag",
                "notes": "Sterke stadsboom, geschikt voor lanen",
            },
            {
                "name": "Lavandula angustifolia",
                "common_name": "Echte lavendel",
                "category": "Vaste plant",
                "height_min": 0.3,
                "height_max": 0.6,
                "width_min": 0.4,
                "width_max": 0.8,
                "sun_requirements": "Volle zon",
                "soil_type": "Goed doorlatend, kalkrijk",
                "water_needs": "Droog tot matig",
                "hardiness_zone": "5-9",
                "bloom_time": "Juni-Augustus",
                "bloom_color": "Paars-blauw",
                "foliage_color": "Grijs-groen",
                "native": False,
                "supplier_id": suppliers[1].id,
                "price": 8.95,
                "availability": "Voorradig",
                "planting_season": "Voorjaar",
                "maintenance": "Laag",
                "notes": "Geurend, trekt bijen aan, droogteresistent",
            },
            {
                "name": "Buxus sempervirens",
                "common_name": "Gewone buxus",
                "category": "Heester",
                "height_min": 0.5,
                "height_max": 3.0,
                "width_min": 0.5,
                "width_max": 2.0,
                "sun_requirements": "Zon tot schaduw",
                "soil_type": "Alle grondsoorten",
                "water_needs": "Matig",
                "hardiness_zone": "6-8",
                "bloom_time": "Maart-April",
                "bloom_color": "Onopvallend geel-groen",
                "foliage_color": "Donkergroen, wintergroen",
                "native": False,
                "supplier_id": suppliers[0].id,
                "price": 12.50,
                "availability": "Beperkt voorradig",
                "planting_season": "Herfst/Voorjaar",
                "maintenance": "Matig",
                "notes": "Uitstekend voor hagen en topiary",
            },
        ]

        for plant_data in plants_data:
            plant = Plant(**plant_data)
            db.session.add(plant)

        # Sample Products
        products_data = [
            {
                "name": "Premium Tuinaarde",
                "description": "Hoogwaardige tuinaarde voor alle toepassingen",
                "category": "Grond en substraat",
                "price": 3.50,
                "unit": "per 40L zak",
                "supplier_id": suppliers[1].id,
                "stock_quantity": 150,
                "sku": "TA-PREM-40L",
                "weight": 25.0,
                "dimensions": "60x40x15 cm",
                "notes": "Geschikt voor groenten, bloemen en heesters",
            },
            {
                "name": "Automatisch Druppelsysteem",
                "description": "Complete druppelirrigatie set voor 20m²",
                "category": "Irrigatie",
                "price": 89.95,
                "unit": "per set",
                "supplier_id": suppliers[2].id,
                "stock_quantity": 25,
                "sku": "IRR-AUTO-20M",
                "weight": 3.5,
                "dimensions": "30x20x15 cm",
                "notes": "Inclusief timer en alle benodigde onderdelen",
            },
            {
                "name": "Professionele Snoeischaar",
                "description": "Bypass snoeischaar voor takken tot 25mm",
                "category": "Gereedschap",
                "price": 34.50,
                "unit": "per stuk",
                "supplier_id": suppliers[0].id,
                "stock_quantity": 40,
                "sku": "TOOL-SNOE-25MM",
                "weight": 0.8,
                "dimensions": "25x8x3 cm",
                "notes": "Ergonomische handgrepen, anti-slip coating",
            },
            {
                "name": "LED Tuinverlichting Set",
                "description": "Energiezuinige LED spots voor tuinverlichting",
                "category": "Verlichting",
                "price": 125.00,
                "unit": "per 6-delige set",
                "supplier_id": suppliers[1].id,
                "stock_quantity": 18,
                "sku": "LED-TUIN-6SET",
                "weight": 2.1,
                "dimensions": "35x25x10 cm",
                "notes": "Waterdicht IP65, warm wit licht, 5 jaar garantie",
            },
        ]

        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)

        # Sample Clients
        clients_data = [
            {
                "name": "Gemeente Amsterdam",
                "contact_person": "Ing. Sarah de Vries",
                "email": "sarah.devries@amsterdam.nl",
                "phone": "+31 20 5551234",
                "address": "Amstel 1",
                "city": "Amsterdam",
                "postal_code": "1011 PN",
                "client_type": "Overheid",
                "budget_range": "€50.000 - €200.000",
                "notes": "Verantwoordelijk voor openbare groenvoorzieningen",
                "registration_date": "2024-01-15",
            },
            {
                "name": "Vondelpark Beheer BV",
                "contact_person": "Drs. Mark Janssen",
                "email": "mark.janssen@vondelpark.nl",
                "phone": "+31 20 5559876",
                "address": "Vondelpark 1",
                "city": "Amsterdam",
                "postal_code": "1071 AA",
                "client_type": "Commercieel",
                "budget_range": "€20.000 - €100.000",
                "notes": "Beheer en onderhoud historische parken",
                "registration_date": "2024-02-03",
            },
            {
                "name": "Villa Rozenhof",
                "contact_person": "Mevr. Elisabeth van Houten",
                "email": "e.vanhouten@rozenhof.nl",
                "phone": "+31 35 5554567",
                "address": "Rozenlaan 45",
                "city": "Hilversum",
                "postal_code": "1234 AB",
                "client_type": "Particulier",
                "budget_range": "€10.000 - €50.000",
                "notes": "Exclusieve privé-tuin met historische elementen",
                "registration_date": "2024-03-12",
            },
        ]

        clients = []
        for client_data in clients_data:
            client = Client(**client_data)
            db.session.add(client)
            clients.append(client)

        db.session.flush()  # Flush to get IDs

        # Sample Projects
        projects_data = [
            {
                "name": "Vondelpark Renovatie Fase 2",
                "description": ("Herinrichting van de zuidelijke zone van het Vondelpark"),
                "client_id": clients[1].id,
                "status": "In uitvoering",
                "start_date": "2024-04-01",
                "end_date": "2024-10-31",
                "budget": 75000.00,
                "location": "Vondelpark Zuid, Amsterdam",
                "project_type": "Renovatie",
                "area_size": 2500.0,
                "notes": "Focus op duurzame beplanting en waterretentie",
                "project_manager": "Hans Kmiel",
            },
            {
                "name": "Daktuin Nieuwbouw Centrum",
                "description": "Extensieve daktuin voor nieuwbouwproject",
                "client_id": clients[0].id,
                "status": "Planning",
                "start_date": "2024-08-15",
                "end_date": "2024-12-20",
                "budget": 45000.00,
                "location": "Centrum Amsterdam",
                "project_type": "Nieuwbouw",
                "area_size": 800.0,
                "notes": "Sedum-dak met biodiversiteit focus",
                "project_manager": "Hans Kmiel",
            },
            {
                "name": "Privé Tuin Rozenhof",
                "description": "Complete herinrichting van historische privé-tuin",
                "client_id": clients[2].id,
                "status": "Afgerond",
                "start_date": "2024-03-01",
                "end_date": "2024-06-30",
                "budget": 32000.00,
                "location": "Hilversum",
                "project_type": "Renovatie",
                "area_size": 1200.0,
                "notes": "Behoud van historische elementen, nieuwe rozentuin",
                "project_manager": "Hans Kmiel",
            },
        ]

        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)

        db.session.commit()

        logger.info("Sample business data created successfully!")
        logger.info(
            f"Created {len(suppliers)} suppliers, {len(plants_data)} plants, "
            f"{len(products_data)} products, {len(clients)} clients, "
            f"and {len(projects_data)} projects."
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error populating sample data: {e!s}")
        raise

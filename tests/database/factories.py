"""
Test factories for creating test data objects
"""

import random

from src.models.landscape import Plant


def create_test_plant(
    name=None,
    common_name=None,
    category=None,
    plant_type=None,
    sun_requirements=None,
    soil_type=None,
    height_min=None,
    height_max=None,
    spread_min=None,
    spread_max=None,
    width_min=None,
    width_max=None,
    hardiness_zone=None,
    water_requirements=None,
    water_needs=None,
    bloom_time=None,
    bloom_color=None,
    foliage_color=None,
    maintenance=None,
    native=None,
    wildlife_value=None,
    pollinator_friendly=None,
    deer_resistant=None,
    pest_resistance=None,
    disease_resistance=None,
    suitable_for_containers=None,
    suitable_for_hedging=None,
    suitable_for_screening=None,
    suitable_for_groundcover=None,
    suitable_for_slopes=None,
    price=None,
    soil_ph_min=None,
    soil_ph_max=None,
):
    """
    Create a test plant with default values or override with specific values
    """
    # Default values for required fields
    if name is None:
        name = f"Test Plant {random.randint(1000, 9999)}"

    if common_name is None:
        common_name = f"Common {name}"

    if plant_type is None:
        plant_type = random.choice(["tree", "shrub", "perennial", "annual"])

    if category is None:
        # If plant_type is provided, use it for category; otherwise use random
        category = (
            plant_type
            if plant_type is not None
            else random.choice(["tree", "shrub", "perennial", "annual"])
        category = plant_type or random.choice(["tree", "shrub", "perennial", "annual"])

    if sun_requirements is None:
        sun_requirements = random.choice(["full_sun", "partial_shade", "full_shade"])

    if soil_type is None:
        soil_type = random.choice(["well_drained", "moist", "wet", "dry"])

    if height_min is None:
        height_min = random.uniform(0.2, 2.0)

    if height_max is None:
        height_max = height_min + random.uniform(0.5, 3.0)

    # Handle both spread_min/max and width_min/max (for compatibility)
    if width_min is None and spread_min is not None:
        width_min = spread_min
    elif width_min is None:
        width_min = random.uniform(0.3, 1.5)

    if width_max is None and spread_max is not None:
        width_max = spread_max
    elif width_max is None:
        width_max = width_min + random.uniform(0.3, 2.0)

    if hardiness_zone is None:
        hardiness_zone = random.choice(["3-7", "4-8", "5-9", "6-10"])

    # Handle both water_requirements and water_needs (for compatibility)
    if water_needs is None and water_requirements is not None:
        water_needs = water_requirements
    elif water_needs is None:
        water_needs = random.choice(["low", "moderate", "high"])

    if bloom_time is None:
        bloom_time = random.choice(["spring", "summer", "fall", "winter"])

    if bloom_color is None:
        bloom_color = random.choice(
            ["white", "pink", "red", "yellow", "purple", "blue"]
        )

    if foliage_color is None:
        foliage_color = random.choice(["green", "variegated", "purple", "silver"])

    if maintenance is None:
        maintenance = random.choice(["low", "medium", "high"])

    if native is None:
        native = random.choice([True, False])

    if wildlife_value is None:
        wildlife_value = random.choice(["low", "medium", "high"])

    if pollinator_friendly is None:
        pollinator_friendly = random.choice([True, False])

    if deer_resistant is None:
        deer_resistant = random.choice([True, False])

    if pest_resistance is None:
        pest_resistance = random.choice(["low", "medium", "high"])

    if disease_resistance is None:
        disease_resistance = random.choice(["low", "medium", "high"])

    if suitable_for_containers is None:
        suitable_for_containers = random.choice([True, False])

    if suitable_for_hedging is None:
        suitable_for_hedging = random.choice([True, False])

    if suitable_for_screening is None:
        suitable_for_screening = random.choice([True, False])

    if suitable_for_groundcover is None:
        suitable_for_groundcover = random.choice([True, False])

    if suitable_for_slopes is None:
        suitable_for_slopes = random.choice([True, False])

    if price is None:
        price = random.uniform(10.0, 200.0)

    if soil_ph_min is None:
        soil_ph_min = random.uniform(5.0, 7.0)

    if soil_ph_max is None:
        soil_ph_max = soil_ph_min + random.uniform(0.5, 2.0)

    plant = Plant(
        name=name,
        common_name=common_name,
        category=category,  # Use category directly
        sun_requirements=sun_requirements,
        soil_type=soil_type,
        height_min=height_min,
        height_max=height_max,
        width_min=width_min,
        width_max=width_max,
        hardiness_zone=hardiness_zone,
        water_needs=water_needs,
        bloom_time=bloom_time,
        bloom_color=bloom_color,
        foliage_color=foliage_color,
        maintenance=maintenance,
        native=native,
        wildlife_value=wildlife_value,
        pollinator_friendly=pollinator_friendly,
        deer_resistant=deer_resistant,
        pest_resistance=pest_resistance,
        disease_resistance=disease_resistance,
        suitable_for_containers=suitable_for_containers,
        suitable_for_hedging=suitable_for_hedging,
        suitable_for_screening=suitable_for_screening,
        suitable_for_groundcover=suitable_for_groundcover,
        suitable_for_slopes=suitable_for_slopes,
        price=price,
        soil_ph_min=soil_ph_min,
        soil_ph_max=soil_ph_max,
    )

    # Add computed property for plant_type to match test expectations
    plant.plant_type = plant_type

    return plant

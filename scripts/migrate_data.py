"""
Migrate oil field data from norwegian_oil_fields.md to SQLite database
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import init_db, get_db_session
from app.database.models import (
    OilField, FieldLocation, LicenseBlock, Platform,
    Operator, FieldRelationship, InfrastructureCluster, ClusterMember
)


# Complete oil field data
OIL_FIELDS_DATA = [
    {
        "field_id": "EKOFISK",
        "name": "Ekofisk",
        "operator": "ConocoPhillips Skandinavia AS",
        "status": "producing",
        "discovery_year": 1969,
        "production_start_year": 1971,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "First giant field discovered on NCS, hub for southern North Sea",
        "infrastructure_notes": "Multiple platforms, subsea systems",
        "location": {
            "latitude": 56.5466,
            "longitude": 3.2183,
            "water_depth_min": 70,
            "water_depth_max": 80,
            "distance_from_shore_km": 320,
            "nearest_city": "Stavanger"
        },
        "blocks": ["2/4"],
        "platforms": [
            {"name": "Ekofisk Complex", "platform_type": "condeep", "installation_year": 1973, "operational": True}
        ],
        "satellites": ["ELDFISK", "EMBLA", "TOR", "HOD"]
    },
    {
        "field_id": "STATFJORD",
        "name": "Statfjord",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1974,
        "production_start_year": 1979,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "One of Norway's largest oil fields, cross-border field",
        "infrastructure_notes": "3 Condeep platforms operational since 1979. 85.47% Norway, 14.53% UK sector",
        "location": {
            "latitude": 61.2500,
            "longitude": 1.8500,
            "water_depth_min": 145,
            "water_depth_max": 145
        },
        "blocks": ["33/9", "33/12"],
        "platforms": [
            {"name": "Statfjord A", "platform_type": "condeep", "installation_year": 1979, "operational": True},
            {"name": "Statfjord B", "platform_type": "condeep", "installation_year": 1982, "operational": True},
            {"name": "Statfjord C", "platform_type": "condeep", "installation_year": 1985, "operational": True}
        ],
        "satellites": ["STATFJORD_NORD"]
    },
    {
        "field_id": "STATFJORD_NORD",
        "name": "Statfjord Nord",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1977,
        "production_start_year": 1995,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Satellite field to Statfjord",
        "hub_field_id": "STATFJORD",
        "location": {
            "latitude": 61.3500,
            "longitude": 1.9000,
            "water_depth_min": 145,
            "water_depth_max": 145
        },
        "blocks": ["33/12"],
        "platforms": [
            {"name": "Statfjord Nord Subsea", "platform_type": "subsea", "installation_year": 1995, "operational": True}
        ]
    },
    {
        "field_id": "STATFJORD_OST",
        "name": "Statfjord Øst",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1976,
        "production_start_year": 1994,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Tied back to Gullfaks infrastructure",
        "hub_field_id": "GULLFAKS",
        "location": {
            "latitude": 61.2000,
            "longitude": 2.0000,
            "water_depth_min": 150,
            "water_depth_max": 150
        },
        "blocks": ["33/6"],
        "platforms": [
            {"name": "Statfjord Øst Subsea", "platform_type": "subsea", "installation_year": 1994, "operational": True}
        ]
    },
    {
        "field_id": "GULLFAKS",
        "name": "Gullfaks",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1978,
        "production_start_year": 1986,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Gullfaks C taller than Eiffel Tower (380m total height)",
        "infrastructure_notes": "3 major platforms with subsea satellites",
        "location": {
            "latitude": 61.2090,
            "longitude": 2.2710,
            "water_depth_min": 130,
            "water_depth_max": 220,
            "distance_from_shore_km": 175,
            "nearest_city": "Bergen"
        },
        "blocks": ["34/10"],
        "platforms": [
            {"name": "Gullfaks A", "platform_type": "condeep", "installation_year": 1986, "operational": True},
            {"name": "Gullfaks B", "platform_type": "condeep", "installation_year": 1988, "operational": True},
            {"name": "Gullfaks C", "platform_type": "condeep", "installation_year": 1989, "operational": True}
        ],
        "satellites": ["GULLFAKS_SOR", "TORDIS", "STATFJORD_OST"]
    },
    {
        "field_id": "GULLFAKS_SOR",
        "name": "Gullfaks Sør",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1982,
        "production_start_year": 1998,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Southern extension of Gullfaks",
        "hub_field_id": "GULLFAKS",
        "location": {
            "latitude": 61.1500,
            "longitude": 2.2500,
            "water_depth_min": 135,
            "water_depth_max": 135
        },
        "blocks": ["34/10"],
        "platforms": [
            {"name": "Gullfaks Sør Subsea", "platform_type": "subsea", "installation_year": 1998, "operational": True}
        ]
    },
    {
        "field_id": "TROLL",
        "name": "Troll",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1979,
        "production_start_year": 1995,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Norway's largest gas field, Troll A tallest structure ever moved",
        "infrastructure_notes": "Troll A (gas), Troll B, Troll C (oil)",
        "location": {
            "latitude": 60.6430,
            "longitude": 3.7200,
            "water_depth_min": 303,
            "water_depth_max": 345,
            "distance_from_shore_km": 65,
            "nearest_city": "Bergen"
        },
        "blocks": ["31/2", "31/3", "31/5", "31/6"],
        "platforms": [
            {"name": "Troll A", "platform_type": "condeep", "installation_year": 1995, "operational": True, "description": "Tallest moved structure - 472m total"},
            {"name": "Troll B", "platform_type": "semi_submersible", "installation_year": 1995, "operational": True},
            {"name": "Troll C", "platform_type": "semi_submersible", "installation_year": 1999, "operational": True}
        ]
    },
    {
        "field_id": "OSEBERG",
        "name": "Oseberg",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1979,
        "production_start_year": 1988,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Major oil field with multiple satellite developments",
        "infrastructure_notes": "Multiple platforms and subsea systems",
        "location": {
            "latitude": 60.5000,
            "longitude": 2.8000,
            "water_depth_min": 100,
            "water_depth_max": 100,
            "distance_from_shore_km": 140,
            "nearest_city": "Bergen"
        },
        "blocks": ["30/6", "30/9"],
        "platforms": [
            {"name": "Oseberg A", "platform_type": "steel_jacket", "installation_year": 1988, "operational": True}
        ],
        "satellites": ["OSEBERG_SOR", "OSEBERG_OST"]
    },
    {
        "field_id": "OSEBERG_SOR",
        "name": "Oseberg Sør",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1984,
        "production_start_year": 2000,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Southern extension of Oseberg field",
        "hub_field_id": "OSEBERG",
        "location": {
            "latitude": 60.4500,
            "longitude": 2.8500,
            "water_depth_min": 105,
            "water_depth_max": 105
        },
        "blocks": ["30/9"],
        "platforms": [
            {"name": "Oseberg Sør Subsea", "platform_type": "subsea", "installation_year": 2000, "operational": True}
        ]
    },
    {
        "field_id": "OSEBERG_OST",
        "name": "Oseberg Øst",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1982,
        "production_start_year": 1999,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Eastern extension of Oseberg field",
        "hub_field_id": "OSEBERG",
        "location": {
            "latitude": 60.5500,
            "longitude": 2.9000,
            "water_depth_min": 110,
            "water_depth_max": 110
        },
        "blocks": ["30/9"],
        "platforms": [
            {"name": "Oseberg Øst Subsea", "platform_type": "subsea", "installation_year": 1999, "operational": True}
        ]
    },
    {
        "field_id": "SNORRE",
        "name": "Snorre",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1979,
        "production_start_year": 1992,
        "sea_area": "north_sea",
        "resource_type": "oil_and_gas",
        "description": "Snorre A is TLP with 16 steel tethers to seabed",
        "infrastructure_notes": "2 platforms in Tampen area",
        "location": {
            "latitude": 61.4500,
            "longitude": 2.1500,
            "water_depth_min": 300,
            "water_depth_max": 350,
            "distance_from_shore_km": 150,
            "nearest_city": "Florø"
        },
        "blocks": ["34/4", "34/7"],
        "platforms": [
            {"name": "Snorre A", "platform_type": "tlp", "installation_year": 1992, "operational": True, "description": "TLP with 16 steel tethers"},
            {"name": "Snorre B", "platform_type": "semi_submersible", "installation_year": 2001, "operational": True}
        ],
        "satellites": ["VIGDIS"]
    },
    {
        "field_id": "VIGDIS",
        "name": "Vigdis",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1986,
        "production_start_year": 1997,
        "sea_area": "north_sea",
        "resource_type": "oil",
        "description": "Satellite field to Snorre",
        "hub_field_id": "SNORRE",
        "location": {
            "latitude": 61.4000,
            "longitude": 2.2000,
            "water_depth_min": 320,
            "water_depth_max": 320
        },
        "blocks": ["34/7"],
        "platforms": [
            {"name": "Vigdis Subsea", "platform_type": "subsea", "installation_year": 1997, "operational": True}
        ]
    },
    {
        "field_id": "JOHAN_SVERDRUP",
        "name": "Johan Sverdrup",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 2010,
        "production_start_year": 2019,
        "sea_area": "north_sea",
        "resource_type": "oil",
        "description": "3rd largest field on NCS, 5th largest discovery ever in Norway",
        "estimated_resources_mmboe": 2700.0,
        "infrastructure_notes": "Multiple platforms, Phase 1 & 2",
        "location": {
            "latitude": 58.9000,
            "longitude": 2.9000,
            "water_depth_min": 110,
            "water_depth_max": 120,
            "distance_from_shore_km": 140,
            "nearest_city": "Stavanger"
        },
        "blocks": ["16/2", "16/3", "16/5", "16/6"],
        "platforms": [
            {"name": "Johan Sverdrup Phase 1", "platform_type": "steel_jacket", "installation_year": 2019, "operational": True},
            {"name": "Johan Sverdrup Phase 2", "platform_type": "steel_jacket", "installation_year": 2022, "operational": True}
        ],
        "satellites": ["BREIDABLIKK"]
    },
    {
        "field_id": "BREIDABLIKK",
        "name": "Breidablikk",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 2018,
        "production_start_year": 2024,
        "sea_area": "north_sea",
        "resource_type": "oil",
        "description": "Tied to Johan Sverdrup Phase 2",
        "hub_field_id": "JOHAN_SVERDRUP",
        "location": {
            "latitude": 58.9300,
            "longitude": 2.8500,
            "water_depth_min": 120,
            "water_depth_max": 120
        },
        "blocks": ["16/2"],
        "platforms": [
            {"name": "Breidablikk Subsea", "platform_type": "subsea", "installation_year": 2024, "operational": True}
        ]
    },
    {
        "field_id": "GRANE",
        "name": "Grane",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1991,
        "production_start_year": 2003,
        "sea_area": "north_sea",
        "resource_type": "oil",
        "description": "Heavy oil field",
        "location": {
            "latitude": 59.1700,
            "longitude": 2.3800,
            "water_depth_min": 127,
            "water_depth_max": 127,
            "distance_from_shore_km": 185,
            "nearest_city": "Haugesund"
        },
        "blocks": ["25/11"],
        "platforms": [
            {"name": "Grane", "platform_type": "semi_submersible", "installation_year": 2003, "operational": True}
        ]
    },
    # Norwegian Sea fields
    {
        "field_id": "ASGARD",
        "name": "Åsgard",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1981,
        "production_start_year": 1999,
        "sea_area": "norwegian_sea",
        "resource_type": "oil_and_gas",
        "description": "Major field in Haltenbanken area",
        "location": {
            "latitude": 65.1000,
            "longitude": 6.8000,
            "water_depth_min": 240,
            "water_depth_max": 310,
            "distance_from_shore_km": 200,
            "nearest_city": "Trondheim"
        },
        "blocks": ["6407/1", "6407/2", "6407/3"],
        "platforms": [
            {"name": "Åsgard A", "platform_type": "fpso", "installation_year": 1999, "operational": True},
            {"name": "Åsgard B", "platform_type": "semi_submersible", "installation_year": 2000, "operational": True}
        ]
    },
    {
        "field_id": "HEIDRUN",
        "name": "Heidrun",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1985,
        "production_start_year": 1995,
        "sea_area": "norwegian_sea",
        "resource_type": "oil_and_gas",
        "description": "Major deepwater TLP development",
        "location": {
            "latitude": 65.3300,
            "longitude": 7.3300,
            "water_depth_min": 345,
            "water_depth_max": 345,
            "distance_from_shore_km": 200,
            "nearest_city": "Sandnessjøen"
        },
        "blocks": ["6507/7"],
        "platforms": [
            {"name": "Heidrun", "platform_type": "tlp", "installation_year": 1995, "operational": True}
        ]
    },
    {
        "field_id": "ORMEN_LANGE",
        "name": "Ormen Lange",
        "operator": "Shell Norge AS",
        "status": "producing",
        "discovery_year": 1997,
        "production_start_year": 2007,
        "sea_area": "norwegian_sea",
        "resource_type": "gas",
        "description": "One of Europe's largest subsea developments",
        "location": {
            "latitude": 63.3500,
            "longitude": 5.2500,
            "water_depth_min": 800,
            "water_depth_max": 1100,
            "distance_from_shore_km": 120,
            "nearest_city": "Kristiansund"
        },
        "blocks": ["6305/4", "6305/5", "6305/6"],
        "platforms": [
            {"name": "Ormen Lange Subsea", "platform_type": "subsea", "installation_year": 2007, "operational": True, "description": "Subsea to Nyhamna onshore"}
        ]
    },
    # Barents Sea fields
    {
        "field_id": "SNOHVIT",
        "name": "Snøhvit",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 1984,
        "production_start_year": 2007,
        "sea_area": "barents_sea",
        "resource_type": "gas",
        "description": "First field in Barents Sea, LNG export from Melkøya",
        "location": {
            "latitude": 71.4500,
            "longitude": 21.6000,
            "water_depth_min": 310,
            "water_depth_max": 345,
            "distance_from_shore_km": 143,
            "nearest_city": "Hammerfest"
        },
        "blocks": ["7121/4"],
        "platforms": [
            {"name": "Snøhvit Subsea", "platform_type": "subsea", "installation_year": 2007, "operational": True, "description": "Subsea to Melkøya LNG"}
        ]
    },
    {
        "field_id": "GOLIAT",
        "name": "Goliat",
        "operator": "Vår Energi AS",
        "status": "producing",
        "discovery_year": 2000,
        "production_start_year": 2016,
        "sea_area": "barents_sea",
        "resource_type": "oil",
        "description": "Northernmost oil field in the world",
        "location": {
            "latitude": 71.2800,
            "longitude": 22.2500,
            "water_depth_min": 400,
            "water_depth_max": 400,
            "distance_from_shore_km": 85,
            "nearest_city": "Hammerfest"
        },
        "blocks": ["7122/7"],
        "platforms": [
            {"name": "Goliat FPSO", "platform_type": "fpso", "installation_year": 2016, "operational": True, "description": "Cylindrical FPSO"}
        ]
    },
    {
        "field_id": "JOHAN_CASTBERG",
        "name": "Johan Castberg",
        "operator": "Equinor Energy AS",
        "status": "producing",
        "discovery_year": 2011,
        "production_start_year": 2025,
        "sea_area": "barents_sea",
        "resource_type": "oil",
        "description": "Latest Barents Sea development, started production 2025",
        "location": {
            "latitude": 71.6000,
            "longitude": 21.0000,
            "water_depth_min": 360,
            "water_depth_max": 390,
            "distance_from_shore_km": 240,
            "nearest_city": "Hammerfest"
        },
        "blocks": ["7220/7", "7220/8"],
        "platforms": [
            {"name": "Johan Castberg FPSO", "platform_type": "fpso", "installation_year": 2024, "operational": True}
        ]
    }
]


# Infrastructure clusters
CLUSTERS_DATA = [
    {
        "cluster_id": "EKOFISK_AREA",
        "name": "Greater Ekofisk Area",
        "hub_field_id": "EKOFISK",
        "sea_area": "north_sea",
        "description": "Southern North Sea hub complex",
        "members": ["EKOFISK", "ELDFISK", "EMBLA", "TOR"]
    },
    {
        "cluster_id": "TAMPEN_AREA",
        "name": "Tampen Area",
        "hub_field_id": "STATFJORD",
        "sea_area": "north_sea",
        "description": "Northern North Sea cluster",
        "members": ["STATFJORD", "STATFJORD_NORD", "STATFJORD_OST", "GULLFAKS", "GULLFAKS_SOR", "SNORRE", "VIGDIS"]
    },
    {
        "cluster_id": "TROLL_AREA",
        "name": "Troll Area",
        "hub_field_id": "TROLL",
        "sea_area": "north_sea",
        "description": "Troll gas and oil fields",
        "members": ["TROLL", "OSEBERG", "OSEBERG_SOR", "OSEBERG_OST"]
    },
    {
        "cluster_id": "HALTENBANKEN",
        "name": "Haltenbanken",
        "hub_field_id": "ASGARD",
        "sea_area": "norwegian_sea",
        "description": "Norwegian Sea cluster",
        "members": ["ASGARD", "HEIDRUN"]
    },
    {
        "cluster_id": "BARENTS_SOUTH",
        "name": "South Barents Sea",
        "hub_field_id": "SNOHVIT",
        "sea_area": "barents_sea",
        "description": "Barents Sea fields",
        "members": ["SNOHVIT", "GOLIAT", "JOHAN_CASTBERG"]
    }
]


def migrate_operators(db):
    """Extract and insert unique operators"""
    print("Migrating operators...")
    operators = set(field["operator"] for field in OIL_FIELDS_DATA)

    for operator_name in operators:
        operator = Operator(
            company_name=operator_name,
            country="Norway"
        )
        db.add(operator)

    db.commit()
    print(f"✓ Migrated {len(operators)} operators")


def migrate_fields(db):
    """Migrate oil fields with locations, blocks, and platforms"""
    print("Migrating oil fields...")

    for field_data in OIL_FIELDS_DATA:
        # Create oil field
        field = OilField(
            field_id=field_data["field_id"],
            name=field_data["name"],
            operator=field_data["operator"],
            status=field_data["status"],
            discovery_year=field_data.get("discovery_year"),
            production_start_year=field_data.get("production_start_year"),
            sea_area=field_data["sea_area"],
            resource_type=field_data["resource_type"],
            description=field_data.get("description"),
            infrastructure_notes=field_data.get("infrastructure_notes"),
            estimated_resources_mmboe=field_data.get("estimated_resources_mmboe"),
            hub_field_id=field_data.get("hub_field_id")
        )
        db.add(field)

        # Create field location
        loc_data = field_data["location"]
        location = FieldLocation(
            field_id=field_data["field_id"],
            latitude=loc_data["latitude"],
            longitude=loc_data["longitude"],
            water_depth_min=loc_data.get("water_depth_min"),
            water_depth_max=loc_data.get("water_depth_max"),
            distance_from_shore_km=loc_data.get("distance_from_shore_km"),
            nearest_city=loc_data.get("nearest_city")
        )
        db.add(location)

        # Create license blocks
        for block in field_data.get("blocks", []):
            license_block = LicenseBlock(
                field_id=field_data["field_id"],
                block_number=block
            )
            db.add(license_block)

        # Create platforms
        for platform_data in field_data.get("platforms", []):
            platform = Platform(
                field_id=field_data["field_id"],
                name=platform_data["name"],
                platform_type=platform_data["platform_type"],
                installation_year=platform_data.get("installation_year"),
                operational=platform_data.get("operational", True),
                unmanned=platform_data.get("unmanned", False),
                description=platform_data.get("description")
            )
            db.add(platform)

    db.commit()
    print(f"✓ Migrated {len(OIL_FIELDS_DATA)} fields with locations, blocks, and platforms")


def migrate_relationships(db):
    """Create field relationships based on satellites"""
    print("Migrating field relationships...")

    relationship_count = 0
    for field_data in OIL_FIELDS_DATA:
        for satellite_id in field_data.get("satellites", []):
            # Check if satellite field exists
            satellite = db.query(OilField).filter_by(field_id=satellite_id).first()
            if satellite:
                relationship = FieldRelationship(
                    hub_field_id=field_data["field_id"],
                    satellite_field_id=satellite_id,
                    relationship_type="satellite"
                )
                db.add(relationship)
                relationship_count += 1

    db.commit()
    print(f"✓ Migrated {relationship_count} field relationships")


def migrate_clusters(db):
    """Create infrastructure clusters"""
    print("Migrating infrastructure clusters...")

    for cluster_data in CLUSTERS_DATA:
        cluster = InfrastructureCluster(
            cluster_id=cluster_data["cluster_id"],
            name=cluster_data["name"],
            hub_field_id=cluster_data["hub_field_id"],
            sea_area=cluster_data["sea_area"],
            description=cluster_data.get("description")
        )
        db.add(cluster)

        # Add cluster members
        for field_id in cluster_data["members"]:
            # Check if field exists
            field = db.query(OilField).filter_by(field_id=field_id).first()
            if field:
                member = ClusterMember(
                    cluster_id=cluster_data["cluster_id"],
                    field_id=field_id
                )
                db.add(member)

    db.commit()
    print(f"✓ Migrated {len(CLUSTERS_DATA)} infrastructure clusters")


def main():
    """Main migration function"""
    print("=" * 60)
    print("Norwegian Oil Fields - Data Migration")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    init_db()

    # Migrate data
    with get_db_session() as db:
        migrate_operators(db)
        migrate_fields(db)
        migrate_relationships(db)
        migrate_clusters(db)

    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)

    # Print statistics
    with get_db_session() as db:
        field_count = db.query(OilField).count()
        platform_count = db.query(Platform).count()
        location_count = db.query(FieldLocation).count()
        operator_count = db.query(Operator).count()
        relationship_count = db.query(FieldRelationship).count()
        cluster_count = db.query(InfrastructureCluster).count()

        print(f"\n📊 Database Statistics:")
        print(f"   - Oil Fields: {field_count}")
        print(f"   - Platforms: {platform_count}")
        print(f"   - Locations: {location_count}")
        print(f"   - Operators: {operator_count}")
        print(f"   - Relationships: {relationship_count}")
        print(f"   - Clusters: {cluster_count}")
        print()


if __name__ == "__main__":
    main()

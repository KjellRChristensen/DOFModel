"""
Script to load Norwegian oil field data from markdown file into structured format
Can be used to populate database or generate JSON/CSV exports
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.oil_field import (
    OilField, OilFieldLocation, Platform,
    FieldStatus, ResourceType, SeaArea, PlatformType
)


# Oil field data compiled from Norwegian Petroleum Directorate and public sources
NORWEGIAN_OIL_FIELDS_DATA = [
    {
        "field_id": "EKOFISK",
        "name": "Ekofisk",
        "operator": "ConocoPhillips Skandinavia AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1969,
        "production_start_year": 1971,
        "location": {
            "latitude": 56.5466,
            "longitude": 3.2183,
            "blocks": ["2/4"],
            "water_depth_min": 70,
            "water_depth_max": 80,
            "distance_from_shore_km": 320,
            "nearest_city": "Stavanger",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Ekofisk Complex",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1973,
                "operational": True,
                "unmanned": False
            }
        ],
        "description": "First giant field discovered on NCS, hub for southern North Sea",
        "satellite_fields": ["ELDFISK", "EMBLA", "TOR", "HOD"]
    },
    {
        "field_id": "STATFJORD",
        "name": "Statfjord",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1974,
        "production_start_year": 1979,
        "location": {
            "latitude": 61.2500,
            "longitude": 1.8500,
            "blocks": ["33/9", "33/12"],
            "water_depth_min": 145,
            "water_depth_max": 145,
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Statfjord A",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1979,
                "operational": True
            },
            {
                "name": "Statfjord B",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1982,
                "operational": True
            },
            {
                "name": "Statfjord C",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1985,
                "operational": True
            }
        ],
        "description": "One of Norway's largest oil fields, 3 Condeep platforms",
        "infrastructure_notes": "Cross-border field, 85.47% Norway, 14.53% UK"
    },
    {
        "field_id": "GULLFAKS",
        "name": "Gullfaks",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1978,
        "production_start_year": 1986,
        "location": {
            "latitude": 61.2090,
            "longitude": 2.2710,
            "blocks": ["34/10"],
            "water_depth_min": 130,
            "water_depth_max": 220,
            "distance_from_shore_km": 175,
            "nearest_city": "Bergen",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Gullfaks A",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1986,
                "operational": True
            },
            {
                "name": "Gullfaks B",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1988,
                "operational": True
            },
            {
                "name": "Gullfaks C",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1989,
                "operational": True,
                "description": "Taller than Eiffel Tower (380m total height)"
            }
        ],
        "description": "Major field with 3 Condeep platforms and subsea satellites",
        "satellite_fields": ["GULLFAKS_SOR", "TORDIS", "STATFJORD_OST"]
    },
    {
        "field_id": "TROLL",
        "name": "Troll",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1979,
        "production_start_year": 1995,
        "location": {
            "latitude": 60.6430,
            "longitude": 3.7200,
            "blocks": ["31/2", "31/3", "31/5", "31/6"],
            "water_depth_min": 303,
            "water_depth_max": 345,
            "distance_from_shore_km": 65,
            "nearest_city": "Bergen",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Troll A",
                "platform_type": PlatformType.CONDEEP,
                "installation_year": 1995,
                "operational": True,
                "description": "Tallest structure ever moved - 472m total height"
            },
            {
                "name": "Troll B",
                "platform_type": PlatformType.SEMI_SUBMERSIBLE,
                "installation_year": 1995,
                "operational": True
            },
            {
                "name": "Troll C",
                "platform_type": PlatformType.SEMI_SUBMERSIBLE,
                "installation_year": 1999,
                "operational": True
            }
        ],
        "description": "Norway's largest gas field, Troll A is world's tallest moved structure"
    },
    {
        "field_id": "OSEBERG",
        "name": "Oseberg",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1979,
        "production_start_year": 1988,
        "location": {
            "latitude": 60.5000,
            "longitude": 2.8000,
            "blocks": ["30/6", "30/9"],
            "water_depth_min": 100,
            "water_depth_max": 100,
            "distance_from_shore_km": 140,
            "nearest_city": "Bergen",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Oseberg A",
                "platform_type": PlatformType.STEEL_JACKET,
                "installation_year": 1988,
                "operational": True
            }
        ],
        "description": "Major oil field with multiple satellite developments",
        "satellite_fields": ["OSEBERG_SOR", "OSEBERG_OST", "BYRDING", "BOYLA"]
    },
    {
        "field_id": "SNORRE",
        "name": "Snorre",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1979,
        "production_start_year": 1992,
        "location": {
            "latitude": 61.4500,
            "longitude": 2.1500,
            "blocks": ["34/4", "34/7"],
            "water_depth_min": 300,
            "water_depth_max": 350,
            "distance_from_shore_km": 150,
            "nearest_city": "Florø",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Snorre A",
                "platform_type": PlatformType.TLP,
                "installation_year": 1992,
                "operational": True,
                "description": "TLP moored with 16 steel tethers"
            },
            {
                "name": "Snorre B",
                "platform_type": PlatformType.SEMI_SUBMERSIBLE,
                "installation_year": 2001,
                "operational": True
            }
        ],
        "description": "Tampen area field with TLP and semi-sub platforms",
        "satellite_fields": ["VIGDIS"]
    },
    {
        "field_id": "JOHAN_SVERDRUP",
        "name": "Johan Sverdrup",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 2010,
        "production_start_year": 2019,
        "location": {
            "latitude": 58.9000,
            "longitude": 2.9000,
            "blocks": ["16/2", "16/3", "16/5", "16/6"],
            "water_depth_min": 110,
            "water_depth_max": 120,
            "distance_from_shore_km": 140,
            "nearest_city": "Stavanger",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL,
        "platforms": [
            {
                "name": "Johan Sverdrup Phase 1",
                "platform_type": PlatformType.STEEL_JACKET,
                "installation_year": 2019,
                "operational": True
            },
            {
                "name": "Johan Sverdrup Phase 2",
                "platform_type": PlatformType.STEEL_JACKET,
                "installation_year": 2022,
                "operational": True
            }
        ],
        "description": "3rd largest field on NCS, 5th largest discovery ever in Norway",
        "estimated_resources_mmboe": 2700,
        "satellite_fields": ["BREIDABLIKK"]
    },
    {
        "field_id": "GRANE",
        "name": "Grane",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1991,
        "production_start_year": 2003,
        "location": {
            "latitude": 59.1700,
            "longitude": 2.3800,
            "blocks": ["25/11"],
            "water_depth_min": 127,
            "water_depth_max": 127,
            "distance_from_shore_km": 185,
            "nearest_city": "Haugesund",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL,
        "platforms": [
            {
                "name": "Grane",
                "platform_type": PlatformType.SEMI_SUBMERSIBLE,
                "installation_year": 2003,
                "operational": True
            }
        ],
        "description": "Heavy oil field"
    },
    {
        "field_id": "VALHALL",
        "name": "Valhall",
        "operator": "Aker BP ASA",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1975,
        "production_start_year": 1982,
        "location": {
            "latitude": 56.2800,
            "longitude": 3.4000,
            "blocks": ["2/8", "2/11", "3/5", "3/6"],
            "water_depth_min": 70,
            "water_depth_max": 70,
            "distance_from_shore_km": 290,
            "nearest_city": "Stavanger",
            "sea_area": SeaArea.NORTH_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Valhall",
                "platform_type": PlatformType.STEEL_JACKET,
                "installation_year": 2011,
                "operational": True,
                "description": "Redeveloped field"
            }
        ],
        "description": "Major chalky reservoir, redeveloped",
        "satellite_fields": ["HOD"]
    },
    {
        "field_id": "ASGARD",
        "name": "Åsgard",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1981,
        "production_start_year": 1999,
        "location": {
            "latitude": 65.1000,
            "longitude": 6.8000,
            "blocks": ["6407/1", "6407/2", "6407/3"],
            "water_depth_min": 240,
            "water_depth_max": 310,
            "distance_from_shore_km": 200,
            "nearest_city": "Trondheim",
            "sea_area": SeaArea.NORWEGIAN_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Åsgard A",
                "platform_type": PlatformType.FPSO,
                "installation_year": 1999,
                "operational": True
            },
            {
                "name": "Åsgard B",
                "platform_type": PlatformType.SEMI_SUBMERSIBLE,
                "installation_year": 2000,
                "operational": True
            }
        ],
        "description": "Major field in Haltenbanken area"
    },
    {
        "field_id": "HEIDRUN",
        "name": "Heidrun",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1985,
        "production_start_year": 1995,
        "location": {
            "latitude": 65.3300,
            "longitude": 7.3300,
            "blocks": ["6507/7"],
            "water_depth_min": 345,
            "water_depth_max": 345,
            "distance_from_shore_km": 200,
            "nearest_city": "Sandnessjøen",
            "sea_area": SeaArea.NORWEGIAN_SEA
        },
        "resource_type": ResourceType.OIL_AND_GAS,
        "platforms": [
            {
                "name": "Heidrun",
                "platform_type": PlatformType.TLP,
                "installation_year": 1995,
                "operational": True
            }
        ],
        "description": "Major deepwater TLP development"
    },
    {
        "field_id": "ORMEN_LANGE",
        "name": "Ormen Lange",
        "operator": "Shell Norge AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1997,
        "production_start_year": 2007,
        "location": {
            "latitude": 63.3500,
            "longitude": 5.2500,
            "blocks": ["6305/4", "6305/5", "6305/6"],
            "water_depth_min": 800,
            "water_depth_max": 1100,
            "distance_from_shore_km": 120,
            "nearest_city": "Kristiansund",
            "sea_area": SeaArea.NORWEGIAN_SEA
        },
        "resource_type": ResourceType.GAS,
        "platforms": [
            {
                "name": "Ormen Lange Subsea",
                "platform_type": PlatformType.SUBSEA,
                "installation_year": 2007,
                "operational": True,
                "description": "Subsea to Nyhamna onshore"
            }
        ],
        "description": "One of Europe's largest subsea developments"
    },
    {
        "field_id": "SNOHVIT",
        "name": "Snøhvit",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 1984,
        "production_start_year": 2007,
        "location": {
            "latitude": 71.4500,
            "longitude": 21.6000,
            "blocks": ["7121/4"],
            "water_depth_min": 310,
            "water_depth_max": 345,
            "distance_from_shore_km": 143,
            "nearest_city": "Hammerfest",
            "sea_area": SeaArea.BARENTS_SEA
        },
        "resource_type": ResourceType.GAS,
        "platforms": [
            {
                "name": "Snøhvit Subsea",
                "platform_type": PlatformType.SUBSEA,
                "installation_year": 2007,
                "operational": True,
                "description": "Subsea to Melkøya LNG"
            }
        ],
        "description": "First field in Barents Sea, LNG export from Melkøya"
    },
    {
        "field_id": "GOLIAT",
        "name": "Goliat",
        "operator": "Vår Energi AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 2000,
        "production_start_year": 2016,
        "location": {
            "latitude": 71.2800,
            "longitude": 22.2500,
            "blocks": ["7122/7"],
            "water_depth_min": 400,
            "water_depth_max": 400,
            "distance_from_shore_km": 85,
            "nearest_city": "Hammerfest",
            "sea_area": SeaArea.BARENTS_SEA
        },
        "resource_type": ResourceType.OIL,
        "platforms": [
            {
                "name": "Goliat FPSO",
                "platform_type": PlatformType.FPSO,
                "installation_year": 2016,
                "operational": True,
                "description": "Cylindrical FPSO, northernmost oil field"
            }
        ],
        "description": "Northernmost oil field in the world"
    },
    {
        "field_id": "JOHAN_CASTBERG",
        "name": "Johan Castberg",
        "operator": "Equinor Energy AS",
        "status": FieldStatus.PRODUCING,
        "discovery_year": 2011,
        "production_start_year": 2025,
        "location": {
            "latitude": 71.6000,
            "longitude": 21.0000,
            "blocks": ["7220/7", "7220/8"],
            "water_depth_min": 360,
            "water_depth_max": 390,
            "distance_from_shore_km": 240,
            "nearest_city": "Hammerfest",
            "sea_area": SeaArea.BARENTS_SEA
        },
        "resource_type": ResourceType.OIL,
        "platforms": [
            {
                "name": "Johan Castberg FPSO",
                "platform_type": PlatformType.FPSO,
                "installation_year": 2024,
                "operational": True
            }
        ],
        "description": "Latest Barents Sea development, started production 2025"
    }
]


def create_oil_fields() -> List[OilField]:
    """Create OilField objects from data"""
    fields = []
    for data in NORWEGIAN_OIL_FIELDS_DATA:
        field = OilField(**data)
        fields.append(field)
    return fields


def export_to_json(fields: List[OilField], output_path: str):
    """Export oil fields to JSON"""
    data = [field.model_dump(mode='json') for field in fields]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Exported {len(fields)} fields to {output_path}")


def export_to_csv(fields: List[OilField], output_path: str):
    """Export oil fields to CSV (flattened)"""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'field_id', 'name', 'operator', 'status', 'discovery_year',
            'production_start_year', 'latitude', 'longitude', 'sea_area',
            'water_depth_min', 'water_depth_max', 'resource_type',
            'distance_from_shore_km', 'description'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for field in fields:
            row = {
                'field_id': field.field_id,
                'name': field.name,
                'operator': field.operator,
                'status': field.status.value,
                'discovery_year': field.discovery_year,
                'production_start_year': field.production_start_year,
                'latitude': field.location.latitude,
                'longitude': field.location.longitude,
                'sea_area': field.location.sea_area.value,
                'water_depth_min': field.location.water_depth_min,
                'water_depth_max': field.location.water_depth_max,
                'resource_type': field.resource_type.value,
                'distance_from_shore_km': field.location.distance_from_shore_km,
                'description': field.description
            }
            writer.writerow(row)
    print(f"Exported {len(fields)} fields to {output_path}")


if __name__ == "__main__":
    # Create oil field objects
    fields = create_oil_fields()
    print(f"Created {len(fields)} oil field objects")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    # Export to JSON
    json_path = output_dir / "norwegian_oil_fields.json"
    export_to_json(fields, str(json_path))

    # Export to CSV
    csv_path = output_dir / "norwegian_oil_fields.csv"
    export_to_csv(fields, str(csv_path))

    print("\nSample field:")
    print(fields[0].model_dump_json(indent=2))

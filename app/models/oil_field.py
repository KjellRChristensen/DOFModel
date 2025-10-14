"""
Oil field and installation models for Norwegian Continental Shelf
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """Types of offshore platforms"""
    CONDEEP = "condeep"  # Concrete gravity-based
    STEEL_JACKET = "steel_jacket"
    FPSO = "fpso"  # Floating Production Storage Offloading
    SEMI_SUBMERSIBLE = "semi_submersible"
    TLP = "tlp"  # Tension Leg Platform
    SPAR = "spar"
    SUBSEA = "subsea"
    UNMANNED = "unmanned"
    ONSHORE = "onshore"


class FieldStatus(str, Enum):
    """Operational status of fields"""
    PRODUCING = "producing"
    PLANNED = "planned"
    UNDER_DEVELOPMENT = "under_development"
    SHUTDOWN = "shutdown"
    DECOMMISSIONED = "decommissioned"


class ResourceType(str, Enum):
    """Types of resources"""
    OIL = "oil"
    GAS = "gas"
    OIL_AND_GAS = "oil_and_gas"
    CONDENSATE = "condensate"
    GAS_AND_CONDENSATE = "gas_and_condensate"


class SeaArea(str, Enum):
    """Regions of the Norwegian Continental Shelf"""
    NORTH_SEA = "north_sea"
    NORWEGIAN_SEA = "norwegian_sea"
    BARENTS_SEA = "barents_sea"


class OilFieldLocation(BaseModel):
    """Geographic location of an oil/gas field"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    blocks: List[str] = Field(default_factory=list, description="License blocks (e.g., ['2/4', '2/7'])")
    water_depth_min: Optional[float] = Field(None, description="Minimum water depth in meters")
    water_depth_max: Optional[float] = Field(None, description="Maximum water depth in meters")
    distance_from_shore_km: Optional[float] = Field(None, description="Distance from shore in kilometers")
    nearest_city: Optional[str] = None
    sea_area: SeaArea

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 56.5466,
                "longitude": 3.2183,
                "blocks": ["2/4"],
                "water_depth_min": 70,
                "water_depth_max": 80,
                "distance_from_shore_km": 320,
                "nearest_city": "Stavanger",
                "sea_area": "north_sea"
            }
        }


class Platform(BaseModel):
    """Individual platform or installation"""
    name: str = Field(..., description="Platform name (e.g., 'Statfjord A')")
    platform_type: PlatformType
    installation_year: Optional[int] = None
    operational: bool = True
    unmanned: bool = False
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Statfjord A",
                "platform_type": "condeep",
                "installation_year": 1979,
                "operational": True,
                "unmanned": False
            }
        }


class OilField(BaseModel):
    """Complete oil/gas field information"""
    field_id: str = Field(..., description="Unique field identifier")
    name: str = Field(..., description="Field name")
    operator: str = Field(..., description="Operating company")
    status: FieldStatus
    discovery_year: Optional[int] = Field(None, ge=1960, le=2030)
    production_start_year: Optional[int] = Field(None, ge=1960, le=2030)
    location: OilFieldLocation
    resource_type: ResourceType
    platforms: List[Platform] = Field(default_factory=list)

    # Additional details
    description: Optional[str] = None
    infrastructure_notes: Optional[str] = None
    estimated_resources_mmboe: Optional[float] = Field(None, description="Million barrels of oil equivalent")

    # Relationships
    hub_field: Optional[str] = Field(None, description="Field ID if this is a satellite/tieback")
    satellite_fields: List[str] = Field(default_factory=list, description="Connected satellite field IDs")

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_source: str = "Norwegian Petroleum Directorate"

    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "EKOFISK",
                "name": "Ekofisk",
                "operator": "ConocoPhillips Skandinavia AS",
                "status": "producing",
                "discovery_year": 1969,
                "production_start_year": 1971,
                "location": {
                    "latitude": 56.5466,
                    "longitude": 3.2183,
                    "blocks": ["2/4"],
                    "water_depth_min": 70,
                    "water_depth_max": 80,
                    "sea_area": "north_sea"
                },
                "resource_type": "oil_and_gas",
                "platforms": [
                    {
                        "name": "Ekofisk Complex",
                        "platform_type": "condeep",
                        "installation_year": 1973,
                        "operational": True
                    }
                ],
                "description": "First giant field discovered on NCS, hub for southern North Sea",
                "satellite_fields": ["ELDFISK", "EMBLA", "TOR"]
            }
        }


class OilFieldSummary(BaseModel):
    """Lightweight summary for lists and maps"""
    field_id: str
    name: str
    operator: str
    status: FieldStatus
    latitude: float
    longitude: float
    sea_area: SeaArea
    resource_type: ResourceType
    production_start_year: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "EKOFISK",
                "name": "Ekofisk",
                "operator": "ConocoPhillips Skandinavia AS",
                "status": "producing",
                "latitude": 56.5466,
                "longitude": 3.2183,
                "sea_area": "north_sea",
                "resource_type": "oil_and_gas",
                "production_start_year": 1971
            }
        }


class CableRoute(BaseModel):
    """Submarine cable route between installations"""
    route_id: str
    name: str
    start_field_id: str
    end_field_id: str
    cable_type: str = Field(..., description="Type of cable (power, communication, umbilical)")
    length_km: float
    installation_year: Optional[int] = None
    operational: bool = True
    inspection_required: bool = True
    last_inspection_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "ROUTE_EKOFISK_EMDEN",
                "name": "Ekofisk-Emden Cable",
                "start_field_id": "EKOFISK",
                "end_field_id": "ONSHORE_EMDEN",
                "cable_type": "power",
                "length_km": 440,
                "installation_year": 2005,
                "operational": True,
                "inspection_required": True
            }
        }


class InfrastructureCluster(BaseModel):
    """Group of interconnected fields and infrastructure"""
    cluster_id: str
    name: str
    hub_field_id: str
    connected_field_ids: List[str]
    sea_area: SeaArea
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": "EKOFISK_AREA",
                "name": "Greater Ekofisk Area",
                "hub_field_id": "EKOFISK",
                "connected_field_ids": ["ELDFISK", "EMBLA", "TOR", "HOD", "TOMMELITEN_A"],
                "sea_area": "north_sea",
                "description": "Southern North Sea hub complex"
            }
        }

"""
Cable models for underwater cable tracking and inspection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CableCondition(str, Enum):
    """Cable condition assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class IssueSeverity(str, Enum):
    """Severity levels for detected issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CableLocation(BaseModel):
    """Geographic location of a cable segment or inspection point"""
    id: str = Field(..., description="Unique identifier for this location")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    depth: Optional[float] = Field(None, description="Depth in meters (positive = below sea level)")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "loc_001",
                "latitude": 69.3296,
                "longitude": 16.1274,
                "depth": 150.0,
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }


class CableSegment(BaseModel):
    """Represents a segment of underwater cable"""
    id: str = Field(..., description="Unique identifier for the cable segment")
    name: str = Field(..., description="Name or designation of the cable segment")
    start_location: CableLocation
    end_location: CableLocation
    length_meters: float = Field(..., gt=0, description="Length of cable segment in meters")
    cable_type: str = Field(..., description="Type of cable (fiber optic, power, etc.)")
    installation_date: Optional[datetime] = Field(None, description="Date when cable was installed")
    last_inspection_date: Optional[datetime] = Field(None, description="Date of last inspection")
    condition: CableCondition = CableCondition.UNKNOWN
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "cable_seg_001",
                "name": "North Sea Segment A",
                "cable_type": "fiber_optic",
                "length_meters": 5000,
                "condition": "good"
            }
        }


class InspectionPoint(BaseModel):
    """A specific point along the cable where inspection occurred"""
    id: str = Field(..., description="Unique identifier for this inspection point")
    cable_segment_id: str = Field(..., description="ID of the cable segment being inspected")
    location: CableLocation
    image_id: Optional[str] = Field(None, description="ID of the associated image")
    condition: CableCondition = CableCondition.UNKNOWN
    detected_issues: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    inspection_date: datetime = Field(default_factory=datetime.utcnow)
    inspector: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "insp_001",
                "cable_segment_id": "cable_seg_001",
                "location": {
                    "id": "loc_001",
                    "latitude": 69.3296,
                    "longitude": 16.1274,
                    "depth": 150.0
                },
                "condition": "fair",
                "detected_issues": ["minor corrosion", "biological growth"],
                "confidence_score": 0.85
            }
        }


class DetectedIssue(BaseModel):
    """Detailed information about a detected cable issue"""
    issue_type: str = Field(..., description="Type of issue (corrosion, damage, wear, etc.)")
    severity: IssueSeverity
    description: str
    location_on_image: Optional[dict] = Field(
        None,
        description="Bounding box or coordinates of issue in image {x, y, width, height}"
    )
    confidence: float = Field(..., ge=0, le=1)
    recommended_action: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "issue_type": "corrosion",
                "severity": "medium",
                "description": "Surface corrosion detected on cable sheath",
                "confidence": 0.82,
                "recommended_action": "Schedule maintenance within 3 months"
            }
        }


class InspectionReport(BaseModel):
    """Complete inspection report for a cable segment"""
    id: str = Field(..., description="Unique identifier for this report")
    cable_segment_id: str
    inspection_points: List[InspectionPoint]
    overall_condition: CableCondition
    total_issues_found: int = 0
    critical_issues: int = 0
    high_severity_issues: int = 0
    recommendations: List[str] = Field(default_factory=list)
    inspection_date: datetime = Field(default_factory=datetime.utcnow)
    inspector: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "report_001",
                "cable_segment_id": "cable_seg_001",
                "overall_condition": "good",
                "total_issues_found": 3,
                "critical_issues": 0,
                "high_severity_issues": 1,
                "recommendations": [
                    "Monitor corrosion areas in sector B",
                    "Schedule full inspection in 6 months"
                ]
            }
        }

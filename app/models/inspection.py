"""
AI Visual Inspection Models for Pipeline and Subsea Asset Inspection
Supports frontend requirements from AI_VISUAL_INSPECTION_IMPLEMENTATION.md
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DefectType(str, Enum):
    """Types of defects that can be detected by AI"""
    CORROSION = "corrosion"
    CRACK = "crack"
    WELD = "weld"
    COATING = "coating"
    FOULING = "fouling"
    DAMAGE = "damage"
    WEAR = "wear"
    UNKNOWN = "unknown"


class DefectSeverity(str, Enum):
    """Severity levels for detected defects"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetCondition(str, Enum):
    """Overall condition assessment"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class DefectLocation(BaseModel):
    """Bounding box location of defect in image"""
    x: int = Field(..., description="X coordinate of top-left corner")
    y: int = Field(..., description="Y coordinate of top-left corner")
    width: int = Field(..., description="Width of bounding box")
    height: int = Field(..., description="Height of bounding box")


class DefectDimensions(BaseModel):
    """Physical dimensions of the defect"""
    length: Optional[float] = Field(None, description="Length in mm")
    width: Optional[float] = Field(None, description="Width in mm")
    depth: Optional[float] = Field(None, description="Depth in mm")


class DetectedDefect(BaseModel):
    """Detailed information about a single detected defect"""
    id: str = Field(..., description="Unique defect identifier")
    type: DefectType = Field(..., description="Type of defect")
    severity: DefectSeverity = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0, le=1, description="AI confidence score")
    location: DefectLocation = Field(..., description="Location in image")
    description: str = Field(..., description="Detailed description of defect")
    dimensions: Optional[DefectDimensions] = Field(None, description="Physical dimensions")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "defect_001",
                "type": "corrosion",
                "severity": "medium",
                "confidence": 0.96,
                "location": {
                    "x": 245,
                    "y": 378,
                    "width": 120,
                    "height": 85
                },
                "description": "Surface corrosion covering approximately 120mm² area",
                "dimensions": {
                    "length": 12.5,
                    "width": 8.3,
                    "depth": 2.1
                }
            }
        }


class AnalysisResult(BaseModel):
    """Complete analysis result from AI inspection"""
    overall_condition: AssetCondition = Field(..., description="Overall asset condition")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence score")
    defects_detected: List[DetectedDefect] = Field(default_factory=list, description="List of detected defects")
    recommendations: List[str] = Field(default_factory=list, description="AI-generated recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "overall_condition": "Fair",
                "confidence": 0.94,
                "defects_detected": [
                    {
                        "id": "defect_001",
                        "type": "corrosion",
                        "severity": "medium",
                        "confidence": 0.96,
                        "location": {"x": 245, "y": 378, "width": 120, "height": 85},
                        "description": "Surface corrosion covering approximately 120mm² area"
                    }
                ],
                "recommendations": [
                    "Schedule maintenance within 6 months",
                    "Monitor corrosion progression"
                ]
            }
        }


class AnalysisResponse(BaseModel):
    """Response structure matching frontend expectations"""
    id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Analysis status")
    processed_at: datetime = Field(..., description="Processing timestamp")
    result: AnalysisResult = Field(..., description="Analysis results")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "analysis_12345",
                "status": "completed",
                "processed_at": "2025-10-17T12:00:00Z",
                "result": {
                    "overall_condition": "Fair",
                    "confidence": 0.94,
                    "defects_detected": [],
                    "recommendations": []
                }
            }
        }


class ImageAnalysisRequest(BaseModel):
    """Request structure for image analysis from frontend"""
    imageData: str = Field(..., description="Base64 encoded image data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    metadata: Optional[Dict] = Field(None, description="Optional metadata (location, depth, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "timestamp": "2025-10-17T12:00:00Z",
                "metadata": {
                    "latitude": 60.5,
                    "longitude": 3.5,
                    "depth": 125.5
                }
            }
        }


class InspectionTask(BaseModel):
    """Inspection task model matching frontend structure"""
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: str = Field(..., description="Task status")
    aiAutomationEnabled: bool = Field(False, description="Whether AI is enabled")
    aiConfidenceScore: Optional[float] = Field(None, ge=0, le=1, description="AI confidence")
    defectsDetected: int = Field(0, description="Number of defects detected")
    findings: Optional[str] = Field(None, description="Summary of findings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    location: Optional[Dict] = Field(None, description="Geographic location")
    depth: Optional[float] = Field(None, description="Depth in meters")
    assignedVessel: Optional[str] = Field(None, description="Assigned vessel")
    scheduledDate: Optional[datetime] = Field(None, description="Scheduled date")
    completedDate: Optional[datetime] = Field(None, description="Completion date")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TASK001",
                "name": "Pipeline Section A Visual Inspection",
                "status": "completed",
                "aiAutomationEnabled": True,
                "aiConfidenceScore": 0.94,
                "defectsDetected": 3,
                "findings": "Minor corrosion detected at 3 locations",
                "recommendations": [
                    "Schedule maintenance within 6 months",
                    "Monitor corrosion progression"
                ]
            }
        }

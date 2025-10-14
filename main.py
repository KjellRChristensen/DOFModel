from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from datetime import datetime
import uuid
from app.models.inference import CableAnalysisModel
from app.models.cable import (
    CableSegment, CableLocation, InspectionPoint,
    CableCondition, DetectedIssue, IssueSeverity
)

app = FastAPI(
    title="Underwater Cable Analysis API",
    description="ML-powered image analysis for underwater cables",
    version="1.0.0"
)

# CORS configuration for iOS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your iOS app requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class AnalysisResult(BaseModel):
    image_id: str
    timestamp: str
    analysis_status: str
    confidence_score: Optional[float] = None
    detected_issues: List[str] = []
    cable_condition: Optional[str] = None
    recommendations: List[str] = []

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# Create directories for image storage
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize ML model
ml_model = CableAnalysisModel()

# In-memory storage for demo (replace with database in production)
cable_segments: List[CableSegment] = []
inspection_points: List[InspectionPoint] = []


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        message="Underwater Cable Analysis API is running",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude of image location"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude of image location"),
    depth: Optional[float] = Query(None, description="Depth in meters"),
    cable_segment_id: Optional[str] = Query(None, description="ID of cable segment being inspected")
):
    """
    Main endpoint for underwater cable image analysis

    Accepts an image file and optional location data, returns analysis results including:
    - Cable condition assessment
    - Detected issues (corrosion, damage, wear, etc.)
    - Confidence scores
    - Recommendations
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    # Generate unique ID for this analysis
    image_id = str(uuid.uuid4())

    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"{image_id}_{file.filename}")
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Perform ML inference
    try:
        analysis_result = await ml_model.analyze_image(file_path)

        # Create inspection point if location data provided
        if latitude is not None and longitude is not None:
            location = CableLocation(
                id=f"loc_{image_id}",
                latitude=latitude,
                longitude=longitude,
                depth=depth,
                timestamp=datetime.now()
            )

            inspection = InspectionPoint(
                id=f"insp_{image_id}",
                cable_segment_id=cable_segment_id or "unknown",
                location=location,
                image_id=image_id,
                condition=CableCondition(analysis_result.get("cable_condition", "unknown")),
                detected_issues=analysis_result.get("detected_issues", []),
                confidence_score=analysis_result.get("confidence_score", 0.0),
                inspection_date=datetime.now()
            )

            inspection_points.append(inspection)

        return AnalysisResult(
            image_id=image_id,
            timestamp=datetime.now().isoformat(),
            analysis_status="completed",
            confidence_score=analysis_result.get("confidence_score", 0.0),
            detected_issues=analysis_result.get("detected_issues", []),
            cable_condition=analysis_result.get("cable_condition", "unknown"),
            recommendations=analysis_result.get("recommendations", [])
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/api/v1/batch-analyze")
async def batch_analyze_images(files: List[UploadFile] = File(...)):
    """
    Batch endpoint for analyzing multiple images
    """
    results = []

    for file in files:
        try:
            result = await analyze_image(file)
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "filename": file.filename
            })

    return {
        "total_images": len(files),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/analysis/{image_id}", response_model=AnalysisResult)
async def get_analysis_result(image_id: str):
    """
    Retrieve previous analysis results by image ID
    """
    # TODO: Implement database/storage retrieval
    raise HTTPException(
        status_code=501,
        detail="Analysis retrieval not yet implemented"
    )


# Cable Management Endpoints

@app.post("/api/v1/cables", response_model=CableSegment, status_code=201)
async def create_cable_segment(cable: CableSegment):
    """
    Register a new cable segment for tracking
    """
    cable_segments.append(cable)
    return cable


@app.get("/api/v1/cables", response_model=List[CableSegment])
async def get_cable_segments(
    condition: Optional[CableCondition] = Query(None, description="Filter by cable condition")
):
    """
    Get all registered cable segments
    """
    if condition:
        return [c for c in cable_segments if c.condition == condition]
    return cable_segments


@app.get("/api/v1/cables/{cable_id}", response_model=CableSegment)
async def get_cable_segment(cable_id: str):
    """
    Get specific cable segment by ID
    """
    cable = next((c for c in cable_segments if c.id == cable_id), None)
    if not cable:
        raise HTTPException(status_code=404, detail="Cable segment not found")
    return cable


@app.get("/api/v1/cables/{cable_id}/inspections", response_model=List[InspectionPoint])
async def get_cable_inspections(cable_id: str):
    """
    Get all inspection points for a specific cable segment
    """
    inspections = [i for i in inspection_points if i.cable_segment_id == cable_id]
    return inspections


# Location-based Endpoints

@app.get("/api/v1/inspections/nearby")
async def get_nearby_inspections(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, description="Search radius in kilometers")
):
    """
    Get inspection points near a specific location (for MapKit integration)
    """
    from math import radians, sin, cos, sqrt, atan2

    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth radius in kilometers
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    nearby = []
    for inspection in inspection_points:
        distance = haversine_distance(
            latitude, longitude,
            inspection.location.latitude,
            inspection.location.longitude
        )
        if distance <= radius_km:
            nearby.append({
                "inspection": inspection,
                "distance_km": round(distance, 2)
            })

    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


@app.get("/api/v1/inspections", response_model=List[InspectionPoint])
async def get_all_inspections(
    condition: Optional[CableCondition] = Query(None, description="Filter by condition"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """
    Get all inspection points (for map display)
    """
    filtered = inspection_points
    if condition:
        filtered = [i for i in filtered if i.condition == condition]

    return filtered[:limit]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

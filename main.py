from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime
import uuid
import json
from app.models.inference import CableAnalysisModel
from app.models.cable import (
    CableSegment, CableLocation, InspectionPoint,
    CableCondition, DetectedIssue, IssueSeverity
)
from app.models.inspection import (
    ImageAnalysisRequest,
    AnalysisResponse as InspectionAnalysisResponse
)
from app.services.visual_inspection import VisualInspectionService
from app.services.multi_model_inference import (
    MultiModelInferenceService,
    ModelType,
    MultiModelResult
)
from app.database.database import get_db, init_db
from app.database import queries
from app.database.models import CableRoute, CableInspection, ClientProfile
from app.schemas.client_profile import ClientProfileResponse, ClientProfileUpdate

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

# Initialize ML models
ml_model = CableAnalysisModel()
visual_inspection_service = VisualInspectionService()
multi_model_service = MultiModelInferenceService()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and check system status on startup"""
    import sys
    import platform
    from pathlib import Path

    print("\n" + "="*60)
    print("🚀 DOF Backend - Underwater Cable Analysis API")
    print("="*60)

    # Python and Platform Info
    print(f"\n📦 System Information:")
    print(f"   Python Version: {sys.version.split()[0]}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")

    # Check MPS (Metal Performance Shaders) for Mac
    print(f"\n🔧 Hardware Acceleration:")
    try:
        import torch
        if torch.backends.mps.is_available():
            print(f"   ✅ MPS (Metal Performance Shaders): Available")
            print(f"   Device: {torch.backends.mps.is_built()}")
        else:
            print(f"   ⚠️  MPS: Not Available")
    except ImportError:
        print(f"   ℹ️  PyTorch not installed (MPS check skipped)")
    except Exception as e:
        print(f"   ⚠️  MPS check failed: {str(e)}")

    # Check Ollama
    print(f"\n🤖 ML Model Status:")
    try:
        import ollama
        # Try to list models
        models = ollama.list()
        print(f"   ✅ Ollama: Connected")

        # Check if our model is available
        model_name = ml_model.model_name
        model_found = any(model_name in str(m) for m in models.get('models', []))

        if model_found:
            print(f"   ✅ Model '{model_name}': Available")
        else:
            print(f"   ⚠️  Model '{model_name}': Not found")
            print(f"   Run: ollama pull {model_name}")

    except Exception as e:
        print(f"   ❌ Ollama: Not connected ({str(e)})")
        print(f"   Make sure Ollama is running")

    # Check SQLite Database
    print(f"\n💾 Database Status:")
    try:
        db_path = Path(__file__).parent / "data" / "oil_fields.db"

        # Initialize database
        init_db()

        if db_path.exists():
            db_size = db_path.stat().st_size / 1024  # Size in KB
            print(f"   ✅ SQLite Database: Connected")
            print(f"   Location: {db_path}")
            print(f"   Size: {db_size:.2f} KB")
        else:
            print(f"   ✅ SQLite Database: Created (new)")
            print(f"   Location: {db_path}")

        # Get database statistics and seed default profile
        from app.database.database import get_db_session
        with get_db_session() as db:
            from app.database.models import OilField, CableRoute, CableInspection
            field_count = db.query(OilField).count()
            cable_count = db.query(CableRoute).count()
            inspection_count = db.query(CableInspection).count()

            print(f"   📊 Records:")
            print(f"      - Oil Fields: {field_count}")
            print(f"      - Cable Routes: {cable_count}")
            print(f"      - Inspections: {inspection_count}")

            # Ensure default client profile exists
            profile = queries.get_or_create_default_profile(db)
            print(f"\n👤 Client Profile:")
            print(f"   Name: {profile.name}")
            print(f"   Company: {profile.company}")
            print(f"   Role: {profile.role}")

    except Exception as e:
        print(f"   ❌ Database Error: {str(e)}")

    # Check Tailscale VPN
    print(f"\n🔒 Network Status:")
    try:
        import subprocess
        import socket

        # Check if Tailscale is running
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            import json
            tailscale_data = json.loads(result.stdout)

            # Get Tailscale IP
            self_info = tailscale_data.get("Self", {})
            tailscale_ips = self_info.get("TailscaleIPs", [])

            if tailscale_ips:
                print(f"   ✅ Tailscale VPN: Connected")
                print(f"   Tailscale IP: {tailscale_ips[0]}")

                # Get hostname
                hostname = socket.gethostname()
                print(f"   Hostname: {hostname}")

                # Backend status
                backend_state = tailscale_data.get("BackendState", "unknown")
                print(f"   Status: {backend_state}")
            else:
                print(f"   ⚠️  Tailscale VPN: Running but no IP assigned")
        else:
            print(f"   ⚠️  Tailscale VPN: Not connected")
            print(f"   Run: tailscale up")

    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Tailscale VPN: Command timeout")
    except FileNotFoundError:
        print(f"   ℹ️  Tailscale: Not installed")
        print(f"   Install from: https://tailscale.com/download")
    except Exception as e:
        print(f"   ⚠️  Tailscale check failed: {str(e)}")

    # Server Info
    print(f"\n🌐 Server Configuration:")
    print(f"   Host: 0.0.0.0")
    print(f"   Port: 4000")
    print(f"   Local URL: http://localhost:4000")
    print(f"   API Docs: http://localhost:4000/docs")
    print(f"   ReDoc: http://localhost:4000/redoc")

    # Add Tailscale URL if connected
    try:
        if result.returncode == 0 and tailscale_ips:
            print(f"   Tailscale URL: http://{tailscale_ips[0]}:4000")
    except:
        pass

    print("\n" + "="*60)
    print("✅ Backend ready for connections")
    print("="*60 + "\n")


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


# AI Visual Inspection Endpoints (Phase 2)

@app.post("/api/analyze", response_model=InspectionAnalysisResponse)
async def analyze_visual_inspection(request: ImageAnalysisRequest):
    """
    AI-powered visual inspection endpoint for pipeline and subsea assets

    Accepts base64 encoded image and returns:
    - Overall condition assessment
    - Detected defects with bounding boxes
    - Confidence scores
    - AI-generated recommendations

    This endpoint matches frontend expectations from AI_VISUAL_INSPECTION_IMPLEMENTATION.md
    """
    try:
        # Perform AI analysis
        result = await visual_inspection_service.analyze_image(request.imageData)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Visual inspection analysis failed: {str(e)}"
        )


@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude of image location"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude of image location"),
    depth: Optional[float] = Query(None, description="Depth in meters"),
    cable_route_id: Optional[str] = Query(None, description="Route ID of cable being inspected"),
    db: Session = Depends(get_db)
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

        # Save inspection to database if cable_route_id and location provided
        inspection_id = f"insp_{image_id}"
        if cable_route_id and latitude is not None and longitude is not None:
            # Get cable route from database
            cable = queries.get_cable_route_by_id(db, cable_route_id)
            if cable:
                # Create inspection record
                inspection = CableInspection(
                    inspection_id=inspection_id,
                    cable_route_id=cable.id,
                    inspection_date=datetime.utcnow(),
                    latitude=latitude,
                    longitude=longitude,
                    depth=depth,
                    image_id=image_id,
                    condition=analysis_result.get("cable_condition", "unknown"),
                    detected_issues=json.dumps(analysis_result.get("detected_issues", [])),
                    confidence_score=analysis_result.get("confidence_score", 0.0),
                    recommendations=json.dumps(analysis_result.get("recommendations", []))
                )
                db.add(inspection)

                # Update cable's last inspection date
                cable.last_inspection_date = datetime.utcnow()

                db.commit()

        return AnalysisResult(
            image_id=image_id,
            timestamp=datetime.utcnow().isoformat(),
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
async def get_analysis_result(image_id: str, db: Session = Depends(get_db)):
    """
    Retrieve previous analysis results by image ID
    """
    # Find inspection by image_id
    inspection = db.query(CableInspection).filter(
        CableInspection.image_id == image_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found for image_id: {image_id}"
        )

    return AnalysisResult(
        image_id=image_id,
        timestamp=inspection.inspection_date.isoformat(),
        analysis_status="completed",
        confidence_score=inspection.confidence_score,
        detected_issues=json.loads(inspection.detected_issues) if inspection.detected_issues else [],
        cable_condition=inspection.condition,
        recommendations=json.loads(inspection.recommendations) if inspection.recommendations else []
    )


# Cable Management Endpoints

@app.post("/api/v1/cables", status_code=201)
async def create_cable_route(
    route_id: str = Query(..., description="Unique route identifier"),
    name: str = Query(..., description="Cable route name"),
    start_field_id: str = Query(..., description="Starting field ID"),
    end_field_id: str = Query(..., description="Ending field ID"),
    cable_type: str = Query(..., description="Type of cable"),
    length_km: float = Query(..., gt=0, description="Length in kilometers"),
    installation_year: Optional[int] = Query(None, description="Installation year"),
    db: Session = Depends(get_db)
):
    """
    Register a new cable route for tracking
    """
    # Check if route_id already exists
    existing = queries.get_cable_route_by_id(db, route_id)
    if existing:
        raise HTTPException(status_code=400, detail="Cable route with this ID already exists")

    cable = CableRoute(
        route_id=route_id,
        name=name,
        start_field_id=start_field_id,
        end_field_id=end_field_id,
        cable_type=cable_type,
        length_km=length_km,
        installation_year=installation_year,
        operational=True,
        inspection_required=True
    )
    db.add(cable)
    db.commit()
    db.refresh(cable)
    return cable


@app.get("/api/v1/cables")
async def get_cable_routes(
    operational: Optional[bool] = Query(None, description="Filter by operational status"),
    needs_inspection: Optional[bool] = Query(None, description="Filter cables needing inspection"),
    db: Session = Depends(get_db)
):
    """
    Get all cable routes
    """
    if needs_inspection:
        cables = queries.get_cables_needing_inspection(db, days_since_last_inspection=180)
    else:
        cables = db.query(CableRoute).all()
        if operational is not None:
            cables = [c for c in cables if c.operational == operational]

    return cables


@app.get("/api/v1/cables/{route_id}")
async def get_cable_route(route_id: str, db: Session = Depends(get_db)):
    """
    Get specific cable route by ID
    """
    cable = queries.get_cable_route_by_id(db, route_id)
    if not cable:
        raise HTTPException(status_code=404, detail="Cable route not found")
    return cable


@app.get("/api/v1/cables/{route_id}/inspections")
async def get_cable_inspections(route_id: str, db: Session = Depends(get_db)):
    """
    Get all inspection points for a specific cable route
    """
    cable = queries.get_cable_route_by_id(db, route_id)
    if not cable:
        raise HTTPException(status_code=404, detail="Cable route not found")

    inspections = queries.get_inspections_for_cable(db, cable.id)
    return inspections


# Location-based Endpoints

@app.get("/api/v1/inspections/nearby")
async def get_nearby_inspections(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Get inspection points near a specific location (for MapKit integration)
    """
    inspections_with_distance = queries.get_inspections_near_location(
        db, latitude, longitude, radius_km
    )

    nearby = []
    for inspection, distance in inspections_with_distance:
        nearby.append({
            "inspection": {
                "inspection_id": inspection.inspection_id,
                "cable_route_id": inspection.cable_route_id,
                "inspection_date": inspection.inspection_date.isoformat(),
                "latitude": inspection.latitude,
                "longitude": inspection.longitude,
                "depth": inspection.depth,
                "condition": inspection.condition,
                "detected_issues": json.loads(inspection.detected_issues) if inspection.detected_issues else [],
                "confidence_score": inspection.confidence_score
            },
            "distance_km": round(distance, 2)
        })

    return nearby


@app.get("/api/v1/inspections")
async def get_all_inspections(
    condition: Optional[str] = Query(None, description="Filter by condition"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get all inspection points (for map display)
    """
    if condition:
        inspections = queries.get_inspections_by_condition(db, condition)
    else:
        inspections = db.query(CableInspection).order_by(
            CableInspection.inspection_date.desc()
        ).limit(limit).all()

    return inspections


# Client Profile Endpoints

@app.get("/api/v1/profile", response_model=ClientProfileResponse)
async def get_client_profile(db: Session = Depends(get_db)):
    """
    Get the current client profile
    """
    profile = queries.get_or_create_default_profile(db)
    return profile


@app.put("/api/v1/profile", response_model=ClientProfileResponse)
async def update_client_profile(
    profile_update: ClientProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the client profile

    Only provided fields will be updated. Fields set to null will be ignored.
    """
    # Get update data excluding None values
    update_data = profile_update.model_dump(exclude_unset=True, exclude_none=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No valid fields provided for update"
        )

    # Update the default profile
    profile = queries.update_profile(db, "default_profile", update_data)

    if not profile:
        # If profile doesn't exist, create it
        profile = queries.create_profile(db, {
            "profile_key": "default_profile",
            **update_data
        })

    return profile


# Multi-Model AI Analysis Endpoints

@app.get("/api/v1/models/status")
async def get_models_status():
    """
    Get status of all available AI models

    Returns information about:
    - YOLOv8 Crack Detection
    - PDS-YOLO Pipeline Defect Detection
    - MAS-YOLOv11 General Underwater Detection
    """
    return multi_model_service.get_model_status()


@app.post("/api/v1/models/{model_type}/load")
async def load_model(model_type: str):
    """
    Load a specific AI model

    Args:
        model_type: One of 'yolov8_crack', 'pds_yolo', 'mas_yolov11'
    """
    try:
        model_enum = ModelType(model_type)
        success = await multi_model_service.load_model(model_enum)

        if success:
            return {
                "status": "success",
                "message": f"Model {model_type} loaded successfully",
                "model_info": multi_model_service.get_model_status()[model_type]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model {model_type}"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model type: {model_type}. Valid types: yolov8_crack, pds_yolo, mas_yolov11"
        )


@app.post("/api/v1/models/{model_type}/unload")
async def unload_model(model_type: str):
    """
    Unload a specific AI model from memory
    """
    try:
        model_enum = ModelType(model_type)
        await multi_model_service.unload_model(model_enum)

        return {
            "status": "success",
            "message": f"Model {model_type} unloaded successfully"
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model type: {model_type}"
        )


@app.post("/api/v1/models/load-all")
async def load_all_models():
    """
    Load all available AI models
    """
    results = await multi_model_service.load_all_models()

    success_count = sum(1 for success in results.values() if success)

    return {
        "status": "completed",
        "models_loaded": success_count,
        "total_models": len(results),
        "results": {k.value: v for k, v in results.items()},
        "model_status": multi_model_service.get_model_status()
    }


class MultiModelAnalysisRequest(BaseModel):
    imageData: str
    models: Optional[List[str]] = None  # If None, use all loaded models
    timestamp: Optional[datetime] = None
    metadata: Optional[dict] = None


class MultiModelAnalysisResponse(BaseModel):
    id: str
    status: str
    analyzed_at: datetime
    models_used: List[str]
    detections_by_model: dict
    consensus_detections: List[dict]
    overall_confidence: float
    model_confidences: dict
    metadata: dict


@app.post("/api/v1/analyze-multi-model", response_model=MultiModelAnalysisResponse)
async def analyze_with_multiple_models(request: MultiModelAnalysisRequest):
    """
    Analyze image with multiple AI models for improved accuracy

    This endpoint analyzes a suspect image using multiple specialized models:
    - Improved YOLOv8: Underwater crack detection
    - PDS-YOLO: Pipeline defect detection
    - MAS-YOLOv11: General underwater object detection

    Returns aggregated results with consensus detections where multiple models agree.
    """
    try:
        # Decode base64 image
        from PIL import Image
        import io
        import base64

        if ',' in request.imageData:
            image_data = request.imageData.split(',')[1]
        else:
            image_data = request.imageData

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Convert model names to enums
        models_to_use = None
        if request.models:
            try:
                models_to_use = [ModelType(m) for m in request.models]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model type in request: {str(e)}"
                )

        # Run multi-model analysis
        result: MultiModelResult = await multi_model_service.analyze_with_multiple_models(
            image,
            models=models_to_use,
            aggregate=True
        )

        # Generate analysis ID
        analysis_id = f"multi_analysis_{uuid.uuid4().hex[:12]}"

        # Format detections by model
        detections_by_model = {}
        for model_type, detections in result.detections_by_model.items():
            detections_by_model[model_type.value] = [
                {
                    "bbox": det.bbox,
                    "confidence": det.confidence,
                    "class_name": det.class_name,
                    "defect_type": det.defect_type.value,
                    "severity": det.severity.value
                }
                for det in detections
            ]

        # Format consensus detections
        consensus_detections = [
            {
                "id": det.id,
                "type": det.type.value,
                "severity": det.severity.value,
                "confidence": det.confidence,
                "location": {
                    "x": det.location.x,
                    "y": det.location.y,
                    "width": det.location.width,
                    "height": det.location.height
                },
                "description": det.description,
                "dimensions": {
                    "length": det.dimensions.length,
                    "width": det.dimensions.width,
                    "depth": det.dimensions.depth
                } if det.dimensions else None
            }
            for det in result.consensus_detections
        ]

        return MultiModelAnalysisResponse(
            id=analysis_id,
            status="completed",
            analyzed_at=datetime.utcnow(),
            models_used=result.analysis_metadata.get("models_used", []),
            detections_by_model=detections_by_model,
            consensus_detections=consensus_detections,
            overall_confidence=result.overall_confidence,
            model_confidences={k.value: v for k, v in result.model_confidences.items()},
            metadata=result.analysis_metadata
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"No models loaded. Load models first using /api/v1/models/load-all"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-model analysis failed: {str(e)}"
        )


@app.post("/api/v1/analyze-enhanced", response_model=InspectionAnalysisResponse)
async def analyze_enhanced_visual_inspection(
    request: ImageAnalysisRequest,
    use_multi_model: bool = Query(True, description="Use multiple AI models for analysis")
):
    """
    Enhanced AI visual inspection with optional multi-model analysis

    This endpoint can use either:
    - Single model (faster, good for real-time analysis)
    - Multiple models (more accurate, better for suspect/critical images)

    When multi_model=True, uses all loaded AI models and returns consensus results.
    """
    try:
        if use_multi_model:
            # Use multi-model analysis
            from PIL import Image
            import io
            import base64

            # Decode image
            if ',' in request.imageData:
                image_data = request.imageData.split(',')[1]
            else:
                image_data = request.imageData

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Run multi-model analysis
            multi_result: MultiModelResult = await multi_model_service.analyze_with_multiple_models(
                image,
                models=None,  # Use all loaded models
                aggregate=True
            )

            # Convert to standard inspection response
            from app.models.inspection import AnalysisResult, AssetCondition
            from app.services.visual_inspection import SeverityScoringEngine, RecommendationEngine

            severity_scorer = SeverityScoringEngine()
            recommendation_engine = RecommendationEngine()

            # Calculate overall condition
            overall_condition = severity_scorer.calculate_overall_condition(multi_result.consensus_detections)

            # Generate recommendations
            recommendations = recommendation_engine.generate_recommendations(
                multi_result.consensus_detections,
                overall_condition
            )

            # Build response
            analysis_id = f"enhanced_analysis_{uuid.uuid4().hex[:12]}"

            result = AnalysisResult(
                overall_condition=overall_condition,
                confidence=multi_result.overall_confidence,
                defects_detected=multi_result.consensus_detections,
                recommendations=recommendations
            )

            return InspectionAnalysisResponse(
                id=analysis_id,
                status="completed",
                processed_at=datetime.utcnow(),
                result=result
            )
        else:
            # Use standard single-model analysis
            result = await visual_inspection_service.analyze_image(request.imageData)
            return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)

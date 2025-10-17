"""
Multi-Model Inference Service for Underwater Defect Detection

Integrates three specialized YOLO models:
1. Improved YOLOv8 - Underwater crack detection for infrastructure
2. PDS-YOLO - Pipeline defect detection for subsea pipelines
3. MAS-YOLOv11 - Enhanced YOLOv11 for general underwater object detection

Allows analyzing images with multiple models for more accurate and comprehensive detection.
"""

import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from PIL import Image
import numpy as np
from enum import Enum

from app.models.inspection import (
    DetectedDefect,
    DefectType,
    DefectSeverity,
    DefectLocation,
    DefectDimensions,
    AssetCondition
)


class ModelType(str, Enum):
    """Available AI models for defect detection"""
    YOLOV8_CRACK = "yolov8_crack"           # Improved YOLOv8 for underwater cracks
    PDS_YOLO = "pds_yolo"                   # PDS-YOLO for pipeline defects
    MAS_YOLOV11 = "mas_yolov11"             # MAS-YOLOv11 for general detection


class ModelStatus(str, Enum):
    """Model loading status"""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


class ModelInfo:
    """Information about a loaded model"""
    def __init__(self, model_type: ModelType, model_path: str):
        self.model_type = model_type
        self.model_path = model_path
        self.status = ModelStatus.NOT_LOADED
        self.model = None
        self.loaded_at: Optional[datetime] = None
        self.error_message: Optional[str] = None

        # Model-specific metadata
        self.specialization = self._get_specialization()
        self.confidence_threshold = 0.25
        self.iou_threshold = 0.45

    def _get_specialization(self) -> str:
        """Get model specialization description"""
        specializations = {
            ModelType.YOLOV8_CRACK: "Underwater infrastructure crack detection",
            ModelType.PDS_YOLO: "Subsea pipeline defect detection",
            ModelType.MAS_YOLOV11: "General underwater object detection"
        }
        return specializations.get(self.model_type, "Unknown specialization")


class ModelDetection:
    """Single detection result from a model"""
    def __init__(
        self,
        model_type: ModelType,
        bbox: List[int],
        confidence: float,
        class_id: int,
        class_name: str,
        defect_type: DefectType,
        severity: DefectSeverity
    ):
        self.model_type = model_type
        self.bbox = bbox  # [x, y, width, height]
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        self.defect_type = defect_type
        self.severity = severity


class MultiModelResult:
    """Aggregated result from multiple models"""
    def __init__(self):
        self.detections_by_model: Dict[ModelType, List[ModelDetection]] = {}
        self.consensus_detections: List[DetectedDefect] = []
        self.model_confidences: Dict[ModelType, float] = {}
        self.overall_confidence: float = 0.0
        self.analysis_metadata: Dict[str, Any] = {}


class MultiModelInferenceService:
    """
    Service for running multiple YOLO models on the same image
    and aggregating results for improved accuracy
    """

    def __init__(self):
        self.models: Dict[ModelType, ModelInfo] = {}
        self.enabled_models: List[ModelType] = []

        # Initialize model registry
        self._initialize_model_registry()

    def _initialize_model_registry(self):
        """Initialize available models (not loading them yet)"""
        # YOLOv8 Crack Detection Model
        self.models[ModelType.YOLOV8_CRACK] = ModelInfo(
            model_type=ModelType.YOLOV8_CRACK,
            model_path="models/yolov8_underwater_crack.pt"
        )

        # PDS-YOLO Pipeline Defect Detection
        self.models[ModelType.PDS_YOLO] = ModelInfo(
            model_type=ModelType.PDS_YOLO,
            model_path="models/pds_yolo_pipeline.pt"
        )

        # MAS-YOLOv11 General Detection
        self.models[ModelType.MAS_YOLOV11] = ModelInfo(
            model_type=ModelType.MAS_YOLOV11,
            model_path="models/mas_yolov11_underwater.pt"
        )

    async def load_model(self, model_type: ModelType, model_path: Optional[str] = None) -> bool:
        """
        Load a specific YOLO model

        Args:
            model_type: Type of model to load
            model_path: Optional custom path to model weights

        Returns:
            True if model loaded successfully
        """
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")

        model_info = self.models[model_type]
        model_info.status = ModelStatus.LOADING

        try:
            # Use custom path if provided
            if model_path:
                model_info.model_path = model_path

            # Load YOLO model using ultralytics
            from ultralytics import YOLO

            model_info.model = YOLO(model_info.model_path)
            model_info.status = ModelStatus.READY
            model_info.loaded_at = datetime.utcnow()

            # Add to enabled models
            if model_type not in self.enabled_models:
                self.enabled_models.append(model_type)

            print(f"✅ Loaded {model_type.value}: {model_info.specialization}")
            return True

        except Exception as e:
            model_info.status = ModelStatus.ERROR
            model_info.error_message = str(e)
            print(f"❌ Failed to load {model_type.value}: {str(e)}")
            return False

    async def load_all_models(self) -> Dict[ModelType, bool]:
        """
        Load all available models

        Returns:
            Dictionary mapping model type to load success status
        """
        results = {}
        for model_type in ModelType:
            results[model_type] = await self.load_model(model_type)
        return results

    async def unload_model(self, model_type: ModelType):
        """Unload a specific model from memory"""
        if model_type in self.models:
            model_info = self.models[model_type]
            model_info.model = None
            model_info.status = ModelStatus.NOT_LOADED
            model_info.loaded_at = None

            if model_type in self.enabled_models:
                self.enabled_models.remove(model_type)

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        status = {}
        for model_type, model_info in self.models.items():
            status[model_type.value] = {
                "status": model_info.status.value,
                "specialization": model_info.specialization,
                "loaded_at": model_info.loaded_at.isoformat() if model_info.loaded_at else None,
                "error": model_info.error_message,
                "confidence_threshold": model_info.confidence_threshold,
                "iou_threshold": model_info.iou_threshold
            }
        return status

    async def analyze_with_multiple_models(
        self,
        image: Image.Image,
        models: Optional[List[ModelType]] = None,
        aggregate: bool = True
    ) -> MultiModelResult:
        """
        Analyze image with multiple models

        Args:
            image: PIL Image to analyze
            models: List of models to use (None = all enabled models)
            aggregate: Whether to aggregate results into consensus detections

        Returns:
            MultiModelResult containing all detections and consensus
        """
        result = MultiModelResult()

        # Use specified models or all enabled models
        models_to_use = models if models else self.enabled_models

        if not models_to_use:
            raise ValueError("No models enabled. Load models first.")

        # Run inference on each model
        for model_type in models_to_use:
            if model_type not in self.enabled_models:
                print(f"⚠️  Skipping {model_type.value} - not loaded")
                continue

            model_info = self.models[model_type]

            if model_info.status != ModelStatus.READY:
                print(f"⚠️  Skipping {model_type.value} - not ready")
                continue

            # Run model inference
            detections = await self._run_model_inference(image, model_info)
            result.detections_by_model[model_type] = detections

            # Calculate model confidence
            if detections:
                avg_confidence = sum(d.confidence for d in detections) / len(detections)
                result.model_confidences[model_type] = round(avg_confidence, 3)
            else:
                result.model_confidences[model_type] = 0.0

        # Aggregate results if requested
        if aggregate:
            result.consensus_detections = self._aggregate_detections(result)
            result.overall_confidence = self._calculate_overall_confidence(result)

        # Add metadata
        result.analysis_metadata = {
            "models_used": [m.value for m in models_to_use],
            "total_detections": sum(len(dets) for dets in result.detections_by_model.values()),
            "consensus_detections": len(result.consensus_detections),
            "analyzed_at": datetime.utcnow().isoformat()
        }

        return result

    async def _run_model_inference(
        self,
        image: Image.Image,
        model_info: ModelInfo
    ) -> List[ModelDetection]:
        """
        Run inference on a single model

        Args:
            image: PIL Image
            model_info: Model information

        Returns:
            List of detections from this model
        """
        detections = []

        try:
            # Convert PIL to numpy array
            img_array = np.array(image)

            # Run YOLO inference
            results = model_info.model.predict(
                img_array,
                conf=model_info.confidence_threshold,
                iou=model_info.iou_threshold,
                verbose=False
            )

            # Process results
            for result in results:
                boxes = result.boxes

                for i, box in enumerate(boxes):
                    # Extract bbox coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    width = int(x2 - x1)
                    height = int(y2 - y1)
                    bbox = [int(x1), int(y1), width, height]

                    # Extract confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                    # Map to defect type and severity
                    defect_type = self._map_class_to_defect_type(class_name, model_info.model_type)
                    severity = self._calculate_severity(confidence, bbox, defect_type)

                    detection = ModelDetection(
                        model_type=model_info.model_type,
                        bbox=bbox,
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                        defect_type=defect_type,
                        severity=severity
                    )
                    detections.append(detection)

        except Exception as e:
            print(f"❌ Error during {model_info.model_type.value} inference: {str(e)}")

        return detections

    def _aggregate_detections(self, result: MultiModelResult) -> List[DetectedDefect]:
        """
        Aggregate detections from multiple models into consensus detections

        Strategy:
        1. Use Non-Maximum Suppression (NMS) across all models
        2. Weight by model confidence
        3. Prioritize detections confirmed by multiple models
        """
        all_detections = []

        # Collect all detections
        for model_type, detections in result.detections_by_model.items():
            all_detections.extend(detections)

        if not all_detections:
            return []

        # Group overlapping detections
        consensus_groups = self._group_overlapping_detections(all_detections)

        # Convert to DetectedDefect objects
        consensus_defects = []
        for group in consensus_groups:
            defect = self._create_consensus_defect(group)
            consensus_defects.append(defect)

        return consensus_defects

    def _group_overlapping_detections(
        self,
        detections: List[ModelDetection],
        iou_threshold: float = 0.5
    ) -> List[List[ModelDetection]]:
        """
        Group detections that overlap (same defect detected by multiple models)
        """
        groups = []
        used = set()

        for i, det1 in enumerate(detections):
            if i in used:
                continue

            group = [det1]
            used.add(i)

            for j, det2 in enumerate(detections[i+1:], start=i+1):
                if j in used:
                    continue

                # Calculate IoU
                iou = self._calculate_iou(det1.bbox, det2.bbox)

                if iou >= iou_threshold:
                    group.append(det2)
                    used.add(j)

            groups.append(group)

        return groups

    def _calculate_iou(self, bbox1: List[int], bbox2: List[int]) -> float:
        """Calculate Intersection over Union between two bounding boxes"""
        x1_1, y1_1, w1, h1 = bbox1
        x2_1, y2_1 = x1_1 + w1, y1_1 + h1

        x1_2, y1_2, w2, h2 = bbox2
        x2_2, y2_2 = x1_2 + w2, y1_2 + h2

        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)

        if x2_i < x1_i or y2_i < y1_i:
            return 0.0

        intersection = (x2_i - x1_i) * (y2_i - y1_i)

        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def _create_consensus_defect(self, group: List[ModelDetection]) -> DetectedDefect:
        """
        Create a consensus defect from a group of overlapping detections
        """
        # Average bbox coordinates
        avg_x = int(np.mean([d.bbox[0] for d in group]))
        avg_y = int(np.mean([d.bbox[1] for d in group]))
        avg_w = int(np.mean([d.bbox[2] for d in group]))
        avg_h = int(np.mean([d.bbox[3] for d in group]))

        # Weighted confidence (weight by number of models agreeing)
        avg_confidence = np.mean([d.confidence for d in group])
        consensus_boost = min(len(group) * 0.05, 0.15)  # Boost up to 15% for multi-model agreement
        final_confidence = min(avg_confidence + consensus_boost, 1.0)

        # Most common defect type
        defect_types = [d.defect_type for d in group]
        most_common_type = max(set(defect_types), key=defect_types.count)

        # Highest severity
        severities = [d.severity for d in group]
        severity_order = [DefectSeverity.LOW, DefectSeverity.MEDIUM, DefectSeverity.HIGH, DefectSeverity.CRITICAL]
        highest_severity = max(severities, key=lambda s: severity_order.index(s))

        # Build description
        models_detected = [d.model_type.value for d in group]
        description = f"{most_common_type.value.title()} detected by {len(group)} model(s): {', '.join(models_detected)}"

        # Estimate dimensions from bbox
        dimensions = DefectDimensions(
            length=float(avg_w) / 10,  # Rough conversion, needs calibration
            width=float(avg_h) / 10,
            depth=None  # Cannot estimate from 2D image
        )

        return DetectedDefect(
            id=f"defect_{uuid.uuid4().hex[:8]}",
            type=most_common_type,
            severity=highest_severity,
            confidence=round(final_confidence, 3),
            location=DefectLocation(x=avg_x, y=avg_y, width=avg_w, height=avg_h),
            description=description,
            dimensions=dimensions
        )

    def _calculate_overall_confidence(self, result: MultiModelResult) -> float:
        """Calculate overall confidence from all models"""
        if not result.model_confidences:
            return 0.0

        # Weight by number of detections
        total_detections = sum(len(dets) for dets in result.detections_by_model.values())

        if total_detections == 0:
            return 0.95  # High confidence if no defects found by any model

        # Average confidence weighted by detection count
        weighted_sum = 0.0
        for model_type, confidence in result.model_confidences.items():
            detection_count = len(result.detections_by_model.get(model_type, []))
            weighted_sum += confidence * detection_count

        return round(weighted_sum / total_detections, 3)

    def _map_class_to_defect_type(self, class_name: str, model_type: ModelType) -> DefectType:
        """Map YOLO class name to DefectType"""
        class_lower = class_name.lower()

        # Common mappings
        if 'crack' in class_lower or 'fracture' in class_lower:
            return DefectType.CRACK
        elif 'corrosion' in class_lower or 'rust' in class_lower:
            return DefectType.CORROSION
        elif 'weld' in class_lower:
            return DefectType.WELD
        elif 'coating' in class_lower or 'paint' in class_lower:
            return DefectType.COATING
        elif 'fouling' in class_lower or 'biofouling' in class_lower or 'marine growth' in class_lower:
            return DefectType.FOULING
        elif 'damage' in class_lower or 'dent' in class_lower:
            return DefectType.DAMAGE
        elif 'wear' in class_lower or 'erosion' in class_lower:
            return DefectType.WEAR
        else:
            return DefectType.UNKNOWN

    def _calculate_severity(self, confidence: float, bbox: List[int], defect_type: DefectType) -> DefectSeverity:
        """Calculate severity based on confidence, size, and type"""
        # Base severity on confidence
        if confidence >= 0.90:
            base_severity = DefectSeverity.HIGH
        elif confidence >= 0.75:
            base_severity = DefectSeverity.MEDIUM
        else:
            base_severity = DefectSeverity.LOW

        # Adjust based on defect size
        width, height = bbox[2], bbox[3]
        area = width * height

        # Large defects are more severe
        if area > 15000:  # Large defect
            severity_order = [DefectSeverity.LOW, DefectSeverity.MEDIUM, DefectSeverity.HIGH, DefectSeverity.CRITICAL]
            current_idx = severity_order.index(base_severity)
            if current_idx < len(severity_order) - 1:
                base_severity = severity_order[current_idx + 1]

        # Critical defect types
        if defect_type in [DefectType.CRACK, DefectType.DAMAGE]:
            if base_severity == DefectSeverity.HIGH and confidence >= 0.95:
                base_severity = DefectSeverity.CRITICAL

        return base_severity

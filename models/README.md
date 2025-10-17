# AI Models Directory

This directory contains the trained YOLO model weights for underwater defect detection.

## Available Models

### 1. YOLOv8 Crack Detection (yolov8_underwater_crack.pt)
- **Specialization**: Underwater infrastructure crack detection
- **Model Type**: Improved YOLOv8
- **Purpose**: Detects cracks in underwater infrastructure (pipelines, cables, platforms)
- **Input Size**: 640x640
- **Classes**: Various crack types, fractures, structural damage

**Download/Training**: Place your trained YOLOv8 crack detection model here, or train one using:
```bash
yolo task=detect mode=train model=yolov8n.pt data=underwater_cracks.yaml epochs=100
```

### 2. PDS-YOLO Pipeline Defect Detection (pds_yolo_pipeline.pt)
- **Specialization**: Subsea pipeline defect detection
- **Model Type**: PDS-YOLO (Pipeline Defect Specialized YOLO)
- **Purpose**: Detects defects specifically in subsea pipelines
- **Input Size**: 640x640
- **Classes**: Corrosion, coating damage, dents, weld defects, marine fouling

**Download/Training**: This is a specialized model for pipeline inspection. Place the trained model here.

### 3. MAS-YOLOv11 Underwater Detection (mas_yolov11_underwater.pt)
- **Specialization**: General underwater object detection
- **Model Type**: MAS-YOLOv11 (Marine-Adapted Specialized YOLOv11)
- **Purpose**: Enhanced YOLOv11 for general underwater object and defect detection
- **Input Size**: 640x640
- **Classes**: Multiple defect types, marine objects, infrastructure damage

**Download/Training**: Enhanced YOLOv11 model. Train using:
```bash
yolo task=detect mode=train model=yolov11n.pt data=underwater_general.yaml epochs=100
```

## Model Placement

Place your trained model weights in this directory with the exact filenames:
- `yolov8_underwater_crack.pt`
- `pds_yolo_pipeline.pt`
- `mas_yolov11_underwater.pt`

## Using Pre-trained Models

If you don't have custom-trained models yet, you can use general YOLO models as placeholders:

```bash
# Download base YOLOv8 model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O yolov8_underwater_crack.pt

# Download base YOLOv11 model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11n.pt -O mas_yolov11_underwater.pt

# For PDS-YOLO, you can use YOLOv8 as a starting point
cp yolov8_underwater_crack.pt pds_yolo_pipeline.pt
```

**Note**: Base models won't detect underwater defects accurately. They are only for testing the system architecture. For production, use models trained on underwater defect datasets.

## Model Training Recommendations

### Dataset Requirements
- **Minimum Images**: 500+ per defect type
- **Image Resolution**: 1920x1080 or higher
- **Annotations**: YOLO format (class x_center y_center width height)
- **Augmentation**: Underwater-specific augmentations (color cast, blur, contrast variations)

### Training Tips
1. **Underwater Color Correction**: Apply preprocessing to training data
2. **Class Balance**: Ensure balanced representation of all defect types
3. **Transfer Learning**: Start with COCO-pretrained weights
4. **Validation Split**: Use 80/20 train/val split
5. **Monitoring**: Track mAP@0.5 and mAP@0.5:0.95

## Model Loading

Models are loaded via the API:

```bash
# Load all models
curl -X POST http://localhost:4000/api/v1/models/load-all

# Load specific model
curl -X POST http://localhost:4000/api/v1/models/yolov8_crack/load

# Check model status
curl http://localhost:4000/api/v1/models/status
```

## Multi-Model Analysis

The system uses consensus-based detection by running all loaded models and aggregating results:

1. Each model processes the image independently
2. Detections are grouped by overlap (IoU > 0.5)
3. Consensus detections boost confidence scores
4. Final results show which models detected each defect

This multi-model approach improves accuracy and reduces false positives.

## Performance Notes

- **Memory**: Each model requires ~50-200MB RAM
- **Inference Time**: ~50-200ms per model per image (CPU), ~10-30ms (GPU)
- **GPU Recommended**: For real-time multi-model analysis
- **Batch Processing**: Process multiple images together for efficiency

## Model Updates

To update models:
1. Place new model weights in this directory
2. Restart the backend server
3. Or use the unload/load API endpoints

## License

Ensure you have appropriate licenses for:
- Ultralytics YOLOv8/YOLOv11 (AGPL-3.0)
- Custom trained models (your organization's license)
- Training datasets used

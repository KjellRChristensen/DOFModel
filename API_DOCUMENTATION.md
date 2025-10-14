# Underwater Cable Analysis API Documentation

Backend API for underwater cable inspection with ML-powered image analysis and MapKit integration.

## Base URL
```
http://localhost:8000
```

## API Endpoints

### Health & Status

#### `GET /`
Basic health check
```json
{
  "status": "ok",
  "message": "Underwater Cable Analysis API is running",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### `GET /health`
Detailed health status
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### Image Analysis

#### `POST /api/v1/analyze`
Analyze underwater cable image with optional location data

**Request:**
- **Form Data:**
  - `file` (required): Image file (JPEG/PNG)
- **Query Parameters:**
  - `latitude` (optional): Latitude (-90 to 90)
  - `longitude` (optional): Longitude (-180 to 180)
  - `depth` (optional): Depth in meters
  - `cable_segment_id` (optional): ID of cable segment

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze?latitude=69.3296&longitude=16.1274&depth=150" \
  -F "file=@cable_image.jpg"
```

**Response:**
```json
{
  "image_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-15T10:30:00Z",
  "analysis_status": "completed",
  "confidence_score": 0.85,
  "detected_issues": ["minor corrosion", "biological growth"],
  "cable_condition": "fair",
  "recommendations": [
    "Monitor corrosion areas",
    "Schedule maintenance within 3 months"
  ]
}
```

#### `POST /api/v1/batch-analyze`
Analyze multiple images in one request

**Request:**
- **Form Data:**
  - `files`: Multiple image files

**Response:**
```json
{
  "total_images": 3,
  "results": [...],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### Cable Management

#### `POST /api/v1/cables`
Register a new cable segment

**Request Body:**
```json
{
  "id": "cable_seg_001",
  "name": "North Sea Segment A",
  "start_location": {
    "id": "loc_start",
    "latitude": 69.3296,
    "longitude": 16.1274,
    "depth": 150.0,
    "timestamp": "2025-01-15T10:00:00Z"
  },
  "end_location": {
    "id": "loc_end",
    "latitude": 69.4000,
    "longitude": 16.2000,
    "depth": 160.0,
    "timestamp": "2025-01-15T10:00:00Z"
  },
  "length_meters": 5000,
  "cable_type": "fiber_optic",
  "condition": "good"
}
```

**Response:** Same as request body (201 Created)

#### `GET /api/v1/cables`
Get all cable segments

**Query Parameters:**
- `condition` (optional): Filter by condition (excellent, good, fair, poor, critical)

**Response:**
```json
[
  {
    "id": "cable_seg_001",
    "name": "North Sea Segment A",
    "cable_type": "fiber_optic",
    "length_meters": 5000,
    "condition": "good",
    ...
  }
]
```

#### `GET /api/v1/cables/{cable_id}`
Get specific cable segment

**Response:** Single cable segment object

#### `GET /api/v1/cables/{cable_id}/inspections`
Get all inspections for a cable segment

**Response:**
```json
[
  {
    "id": "insp_001",
    "cable_segment_id": "cable_seg_001",
    "location": {
      "latitude": 69.3296,
      "longitude": 16.1274,
      "depth": 150.0
    },
    "condition": "fair",
    "detected_issues": ["minor corrosion"],
    "confidence_score": 0.85,
    "inspection_date": "2025-01-15T10:30:00Z"
  }
]
```

---

### Location-Based Queries (MapKit Integration)

#### `GET /api/v1/inspections/nearby`
Find inspection points near a location

**Query Parameters:**
- `latitude` (required): Center latitude
- `longitude` (required): Center longitude
- `radius_km` (optional, default: 10.0): Search radius in kilometers

**Example:**
```bash
curl "http://localhost:8000/api/v1/inspections/nearby?latitude=69.3296&longitude=16.1274&radius_km=5"
```

**Response:**
```json
[
  {
    "inspection": {
      "id": "insp_001",
      "location": {...},
      "condition": "fair",
      ...
    },
    "distance_km": 2.3
  }
]
```

#### `GET /api/v1/inspections`
Get all inspection points (for map display)

**Query Parameters:**
- `condition` (optional): Filter by condition
- `limit` (optional, default: 100): Maximum results (1-1000)

**Response:** Array of inspection points

---

## Data Models

### Cable Conditions
- `excellent` - No issues detected
- `good` - Minor wear, no action needed
- `fair` - Some issues, monitoring recommended
- `poor` - Multiple issues, maintenance needed
- `critical` - Severe damage, immediate action required
- `unknown` - Not yet analyzed

### Issue Severity Levels
- `low` - Minor issues
- `medium` - Notable issues requiring monitoring
- `high` - Serious issues requiring maintenance
- `critical` - Severe issues requiring immediate action

---

## Integration with iOS/Swift

### Using URLSession

```swift
func analyzeImage(_ image: UIImage, latitude: Double, longitude: Double) async throws {
    guard let imageData = image.jpegData(compressionQuality: 0.8) else {
        throw AnalysisError.invalidImage
    }

    let boundary = UUID().uuidString
    var request = URLRequest(url: URL(string: "http://localhost:8000/api/v1/analyze?latitude=\\(latitude)&longitude=\\(longitude)")!)
    request.httpMethod = "POST"
    request.setValue("multipart/form-data; boundary=\\(boundary)", forHTTPHeaderField: "Content-Type")

    var body = Data()
    body.append("--\\(boundary)\\r\\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\\"file\\"; filename=\\"image.jpg\\"\\r\\n".data(using: .utf8)!)
    body.append("Content-Type: image/jpeg\\r\\n\\r\\n".data(using: .utf8)!)
    body.append(imageData)
    body.append("\\r\\n--\\(boundary)--\\r\\n".data(using: .utf8)!)

    let (data, _) = try await URLSession.shared.upload(for: request, from: body)
    let result = try JSONDecoder().decode(AnalysisResult.self, from: data)
}
```

### MapKit Integration

Use `/api/v1/inspections` endpoint to fetch all inspection points and display them as map annotations:

```swift
import MapKit

struct InspectionAnnotation: Identifiable {
    let id: String
    let coordinate: CLLocationCoordinate2D
    let condition: CableCondition
}

// Fetch and display on map
let inspections = try await fetchInspections()
let annotations = inspections.map { inspection in
    InspectionAnnotation(
        id: inspection.id,
        coordinate: CLLocationCoordinate2D(
            latitude: inspection.location.latitude,
            longitude: inspection.location.longitude
        ),
        condition: inspection.condition
    )
}
```

---

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API testing and detailed schema information.

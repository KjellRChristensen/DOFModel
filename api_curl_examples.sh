#!/bin/bash

# DOF Backend API - Quick Curl Examples
# Individual curl commands for easy copy-paste
# Usage: Source this file or copy individual commands

BASE_URL="http://localhost:4000"

# ===========================================
# HEALTH CHECK ENDPOINTS
# ===========================================

# Root health check
curl $BASE_URL/

# Detailed health check
curl $BASE_URL/health | jq '.'

# ===========================================
# AI MODELS MANAGEMENT
# ===========================================

# Get all models status
curl $BASE_URL/api/models/status | jq '.'

# Load all models
curl -X POST $BASE_URL/api/models/load-all | jq '.'

# Load specific model (YOLOv8 crack detection)
curl -X POST $BASE_URL/api/models/yolov8_crack/load | jq '.'

# Load specific model (PDS-YOLO)
curl -X POST $BASE_URL/api/models/pds_yolo/load | jq '.'

# Load specific model (MAS-YOLOv11)
curl -X POST $BASE_URL/api/models/mas_yolov11/load | jq '.'

# Unload model
curl -X POST $BASE_URL/api/models/yolov8_crack/unload | jq '.'

# ===========================================
# AI VISUAL INSPECTION
# ===========================================

# Single model visual inspection
curl -X POST $BASE_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
    "timestamp": "2025-10-17T12:00:00Z",
    "metadata": {
      "latitude": 60.5,
      "longitude": 3.5,
      "depth": 125.5
    }
  }' | jq '.'

# Multi-model analysis with all models
curl -X POST $BASE_URL/api/analyze-multi-model \
  -H "Content-Type: application/json" \
  -d '{
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
    "timestamp": "2025-10-17T12:00:00Z"
  }' | jq '.'

# Multi-model analysis with specific models
curl -X POST $BASE_URL/api/analyze-multi-model \
  -H "Content-Type: application/json" \
  -d '{
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
    "models": ["yolov8_crack", "pds_yolo"],
    "timestamp": "2025-10-17T12:00:00Z"
  }' | jq '.'

# Enhanced analysis with multi-model
curl -X POST "$BASE_URL/api/analyze-enhanced?use_multi_model=true" \
  -H "Content-Type: application/json" \
  -d '{
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
    "timestamp": "2025-10-17T12:00:00Z"
  }' | jq '.'

# Enhanced analysis with single model
curl -X POST "$BASE_URL/api/analyze-enhanced?use_multi_model=false" \
  -H "Content-Type: application/json" \
  -d '{
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
    "timestamp": "2025-10-17T12:00:00Z"
  }' | jq '.'

# ===========================================
# FILE UPLOAD IMAGE ANALYSIS
# ===========================================

# Analyze image file
curl -X POST $BASE_URL/api/analyze \
  -F "file=@/path/to/image.jpg" \
  -F "latitude=60.5" \
  -F "longitude=3.5" \
  -F "depth=125.5" \
  -F "cable_route_id=CABLE001" | jq '.'

# Batch analyze multiple images
curl -X POST $BASE_URL/api/batch-analyze \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.jpg" \
  -F "files=@/path/to/image3.jpg" | jq '.'

# Get analysis result by image ID
curl $BASE_URL/api/analysis/IMAGE_ID_HERE | jq '.'

# ===========================================
# CABLE MANAGEMENT
# ===========================================

# Get all cable routes
curl $BASE_URL/api/cables | jq '.'

# Get operational cables only
curl "$BASE_URL/api/cables?operational=true" | jq '.'

# Get cables needing inspection
curl "$BASE_URL/api/cables?needs_inspection=true" | jq '.'

# Create new cable route
curl -X POST "$BASE_URL/api/cables?route_id=CABLE001&name=Main%20Pipeline%20Cable&start_field_id=FIELD001&end_field_id=FIELD002&cable_type=power&length_km=25.5&installation_year=2020" | jq '.'

# Get specific cable route
curl $BASE_URL/api/cables/CABLE001 | jq '.'

# Get inspections for cable route
curl $BASE_URL/api/cables/CABLE001/inspections | jq '.'

# ===========================================
# INSPECTIONS
# ===========================================

# Get all inspections
curl $BASE_URL/api/inspections | jq '.'

# Get inspections with limit
curl "$BASE_URL/api/inspections?limit=50" | jq '.'

# Get inspections by condition
curl "$BASE_URL/api/inspections?condition=good" | jq '.'
curl "$BASE_URL/api/inspections?condition=poor" | jq '.'
curl "$BASE_URL/api/inspections?condition=critical" | jq '.'

# Get nearby inspections
curl "$BASE_URL/api/inspections/nearby?latitude=60.5&longitude=3.5&radius_km=50" | jq '.'

# ===========================================
# CLIENT PROFILE
# ===========================================

# Get client profile
curl $BASE_URL/api/profile | jq '.'

# Update client profile
curl -X PUT $BASE_URL/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "company": "DOF Subsea AS",
    "role": "Senior Inspection Engineer",
    "email": "john.doe@dofsubsea.com",
    "phone": "+47 12345678"
  }' | jq '.'

# Partial update (only name and email)
curl -X PUT $BASE_URL/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane.smith@dofsubsea.com"
  }' | jq '.'

# ===========================================
# USEFUL COMBINED COMMANDS
# ===========================================

# Load all models and check status
curl -X POST $BASE_URL/api/models/load-all && \
curl $BASE_URL/api/models/status | jq '.'

# Create cable and get all cables
curl -X POST "$BASE_URL/api/cables?route_id=TEST001&name=Test%20Cable&start_field_id=F001&end_field_id=F002&cable_type=power&length_km=10.5" && \
curl $BASE_URL/api/cables | jq '.'

# Get health, models status, and profile
curl $BASE_URL/health | jq '.' && \
curl $BASE_URL/api/models/status | jq '.' && \
curl $BASE_URL/api/profile | jq '.'

# ===========================================
# TESTING WITH REAL IMAGE
# ===========================================

# Convert image to base64 and analyze
# base64 -i underwater_image.jpg | tr -d '\n' > image_base64.txt
# IMAGE_DATA=$(cat image_base64.txt)
# curl -X POST $BASE_URL/api/analyze-multi-model \
#   -H "Content-Type: application/json" \
#   -d "{\"imageData\": \"$IMAGE_DATA\"}" | jq '.'

# ===========================================
# MONITORING AND DEBUGGING
# ===========================================

# Monitor API response times
time curl $BASE_URL/health

# Test with verbose output
curl -v $BASE_URL/api/models/status

# Save response to file
curl $BASE_URL/api/cables > cables_response.json

# Watch models status in real-time (refresh every 2 seconds)
watch -n 2 "curl -s $BASE_URL/api/models/status | jq '.'"

# ===========================================
# DOCUMENTATION
# ===========================================

# Open Swagger UI (browser)
# open $BASE_URL/docs

# Open ReDoc (browser)
# open $BASE_URL/redoc

# Get OpenAPI schema
curl $BASE_URL/openapi.json | jq '.'

# ===========================================
# BATCH OPERATIONS
# ===========================================

# Load all models, analyze image, then unload all models
curl -X POST $BASE_URL/api/models/load-all && \
curl -X POST $BASE_URL/api/analyze-multi-model \
  -H "Content-Type: application/json" \
  -d '{"imageData": "BASE64_IMAGE_DATA"}' && \
curl -X POST $BASE_URL/api/models/yolov8_crack/unload && \
curl -X POST $BASE_URL/api/models/pds_yolo/unload && \
curl -X POST $BASE_URL/api/models/mas_yolov11/unload

# ===========================================
# ERROR TESTING
# ===========================================

# Test invalid model type
curl -X POST $BASE_URL/api/models/invalid_model/load

# Test invalid cable route
curl $BASE_URL/api/cables/NONEXISTENT

# Test invalid image data
curl -X POST $BASE_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"imageData": "invalid_base64"}'

# ===========================================
# PERFORMANCE TESTING
# ===========================================

# Time single model analysis
time curl -X POST $BASE_URL/api/analyze-enhanced?use_multi_model=false \
  -H "Content-Type: application/json" \
  -d '{"imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="}' \
  -o /dev/null -s

# Time multi-model analysis
time curl -X POST $BASE_URL/api/analyze-enhanced?use_multi_model=true \
  -H "Content-Type: application/json" \
  -d '{"imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="}' \
  -o /dev/null -s

# ===========================================
# NOTES
# ===========================================

# Replace BASE_URL with your actual server URL:
#   - Local: http://localhost:4000
#   - Tailscale: http://TAILSCALE_IP:4000
#   - Remote: https://your-domain.com

# Replace image data with actual base64 encoded images

# Use jq for pretty JSON output (install: brew install jq)

# For file uploads, replace paths with actual image file paths

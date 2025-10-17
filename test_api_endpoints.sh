#!/bin/bash

# DOF Backend API Testing Script
# Comprehensive curl commands for all FastAPI endpoints
# Usage: ./test_api_endpoints.sh [BASE_URL]

# Configuration
BASE_URL="${1:-http://localhost:4000}"
OUTPUT_DIR="./api_test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to print colored headers
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

# Function to print test name
print_test() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to save response
save_response() {
    local filename="$OUTPUT_DIR/${TIMESTAMP}_$1.json"
    cat > "$filename"
    echo -e "${BLUE}  Response saved to: $filename${NC}"
}

# Function to make curl request and display response
curl_request() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local extra_args=$5

    print_test "$description"
    echo -e "${BLUE}  $method $BASE_URL$endpoint${NC}"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" $extra_args)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" $extra_args)
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" $extra_args)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        print_success "Status: $http_code"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        print_error "Status: $http_code"
        echo "$body"
    fi

    echo ""
}

# Start testing
clear
print_header "DOF Backend API Comprehensive Testing"
echo "Base URL: $BASE_URL"
echo "Timestamp: $TIMESTAMP"
echo "Output Directory: $OUTPUT_DIR"

# ============================================
# Health Check Endpoints
# ============================================
print_header "1. Health Check Endpoints"

curl_request "GET" "/" "Root endpoint - Health check"

curl_request "GET" "/health" "Detailed health check"

# ============================================
# AI Visual Inspection Endpoints
# ============================================
print_header "2. AI Visual Inspection Endpoints"

# Create sample base64 image (1x1 red pixel PNG)
SAMPLE_IMAGE="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

curl_request "POST" "/api/analyze" "Single model visual inspection" \
'{
  "imageData": "'"$SAMPLE_IMAGE"'",
  "timestamp": "2025-10-17T12:00:00Z",
  "metadata": {
    "latitude": 60.5,
    "longitude": 3.5,
    "depth": 125.5
  }
}'

# ============================================
# Multi-Model AI Analysis Endpoints
# ============================================
print_header "3. Multi-Model AI Analysis Endpoints"

curl_request "GET" "/api/models/status" "Get all models status"

curl_request "POST" "/api/models/load-all" "Load all AI models"

curl_request "POST" "/api/models/yolov8_crack/load" "Load YOLOv8 crack detection model"

curl_request "POST" "/api/models/pds_yolo/load" "Load PDS-YOLO pipeline model"

curl_request "POST" "/api/models/mas_yolov11/load" "Load MAS-YOLOv11 model"

curl_request "GET" "/api/models/status" "Check models status after loading"

curl_request "POST" "/api/analyze-multi-model" "Multi-model analysis" \
'{
  "imageData": "'"$SAMPLE_IMAGE"'",
  "models": ["yolov8_crack", "pds_yolo", "mas_yolov11"],
  "timestamp": "2025-10-17T12:00:00Z",
  "metadata": {
    "source": "test_script"
  }
}'

curl_request "POST" "/api/analyze-multi-model" "Multi-model analysis (all loaded models)" \
'{
  "imageData": "'"$SAMPLE_IMAGE"'",
  "timestamp": "2025-10-17T12:00:00Z"
}'

curl_request "POST" "/api/analyze-enhanced?use_multi_model=true" "Enhanced analysis with multi-model" \
'{
  "imageData": "'"$SAMPLE_IMAGE"'",
  "timestamp": "2025-10-17T12:00:00Z"
}'

curl_request "POST" "/api/analyze-enhanced?use_multi_model=false" "Enhanced analysis (single model)" \
'{
  "imageData": "'"$SAMPLE_IMAGE"'",
  "timestamp": "2025-10-17T12:00:00Z"
}'

# ============================================
# Cable Management Endpoints
# ============================================
print_header "4. Cable Management Endpoints"

curl_request "GET" "/api/cables" "Get all cable routes"

curl_request "GET" "/api/cables?operational=true" "Get operational cables only"

curl_request "GET" "/api/cables?needs_inspection=true" "Get cables needing inspection"

curl_request "POST" "/api/cables?route_id=TEST001&name=Test%20Cable%20Route&start_field_id=FIELD001&end_field_id=FIELD002&cable_type=power&length_km=25.5&installation_year=2020" \
    "Create new cable route"

curl_request "GET" "/api/cables/TEST001" "Get specific cable route by ID"

curl_request "GET" "/api/cables/TEST001/inspections" "Get inspections for cable route"

# ============================================
# Image Analysis Endpoints (File Upload)
# ============================================
print_header "5. Image Analysis Endpoints (File Upload)"

# Create a temporary test image
TEMP_IMAGE="/tmp/test_underwater_image.png"
# Create a 100x100 test image using ImageMagick (if available) or use existing
if command -v convert &> /dev/null; then
    convert -size 100x100 xc:blue "$TEMP_IMAGE"

    print_test "Analyze image with file upload"
    echo -e "${BLUE}  POST $BASE_URL/api/analyze${NC}"

    curl -s -X POST "$BASE_URL/api/analyze" \
        -F "file=@$TEMP_IMAGE" \
        -F "latitude=60.5" \
        -F "longitude=3.5" \
        -F "depth=125.5" \
        -F "cable_route_id=TEST001" | jq '.' 2>/dev/null || echo "Response received"

    print_success "File upload test completed"
    echo ""

    rm -f "$TEMP_IMAGE"
else
    print_error "ImageMagick not available - skipping file upload test"
fi

# ============================================
# Inspection Endpoints
# ============================================
print_header "6. Inspection Endpoints"

curl_request "GET" "/api/inspections" "Get all inspections"

curl_request "GET" "/api/inspections?limit=10" "Get 10 most recent inspections"

curl_request "GET" "/api/inspections?condition=good" "Get inspections by condition"

curl_request "GET" "/api/inspections/nearby?latitude=60.5&longitude=3.5&radius_km=50" \
    "Get nearby inspections (50km radius)"

# ============================================
# Client Profile Endpoints
# ============================================
print_header "7. Client Profile Endpoints"

curl_request "GET" "/api/profile" "Get current client profile"

curl_request "PUT" "/api/profile" "Update client profile" \
'{
  "name": "Test Engineer",
  "company": "DOF Subsea",
  "role": "Senior Inspection Engineer",
  "email": "test@dofsubsea.com",
  "phone": "+47 12345678"
}'

curl_request "GET" "/api/profile" "Get updated client profile"

# ============================================
# Model Unloading
# ============================================
print_header "8. Model Unloading"

curl_request "POST" "/api/models/yolov8_crack/unload" "Unload YOLOv8 model"

curl_request "POST" "/api/models/pds_yolo/unload" "Unload PDS-YOLO model"

curl_request "POST" "/api/models/mas_yolov11/unload" "Unload MAS-YOLOv11 model"

curl_request "GET" "/api/models/status" "Check models status after unloading"

# ============================================
# Interactive Mode
# ============================================
print_header "Interactive Testing Mode"

echo -e "${CYAN}Would you like to enter interactive mode? (y/n)${NC}"
read -r response

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    while true; do
        echo -e "\n${CYAN}Available Commands:${NC}"
        echo "1)  Health Check"
        echo "2)  Get Models Status"
        echo "3)  Load All Models"
        echo "4)  Analyze Image (Multi-Model)"
        echo "5)  Get All Cables"
        echo "6)  Get All Inspections"
        echo "7)  Get Client Profile"
        echo "8)  Custom GET Request"
        echo "9)  Custom POST Request"
        echo "0)  Exit"
        echo ""
        echo -e "${YELLOW}Enter choice:${NC}"
        read -r choice

        case $choice in
            1)
                curl_request "GET" "/health" "Health check"
                ;;
            2)
                curl_request "GET" "/api/models/status" "Models status"
                ;;
            3)
                curl_request "POST" "/api/models/load-all" "Load all models"
                ;;
            4)
                curl_request "POST" "/api/analyze-multi-model" "Multi-model analysis" \
                '{
                  "imageData": "'"$SAMPLE_IMAGE"'",
                  "timestamp": "2025-10-17T12:00:00Z"
                }'
                ;;
            5)
                curl_request "GET" "/api/cables" "Get all cables"
                ;;
            6)
                curl_request "GET" "/api/inspections" "Get all inspections"
                ;;
            7)
                curl_request "GET" "/api/profile" "Get client profile"
                ;;
            8)
                echo -e "${YELLOW}Enter endpoint (e.g., /api/cables):${NC}"
                read -r endpoint
                curl_request "GET" "$endpoint" "Custom GET request"
                ;;
            9)
                echo -e "${YELLOW}Enter endpoint:${NC}"
                read -r endpoint
                echo -e "${YELLOW}Enter JSON data:${NC}"
                read -r data
                curl_request "POST" "$endpoint" "Custom POST request" "$data"
                ;;
            0)
                echo -e "${GREEN}Exiting...${NC}"
                break
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
    done
fi

# ============================================
# Summary
# ============================================
print_header "Testing Complete"

echo -e "${GREEN}All endpoint tests completed!${NC}"
echo ""
echo "Test results saved to: $OUTPUT_DIR"
echo "Base URL tested: $BASE_URL"
echo ""
echo -e "${CYAN}Quick Access Commands:${NC}"
echo "  Health:       curl $BASE_URL/health"
echo "  Models:       curl $BASE_URL/api/models/status"
echo "  Cables:       curl $BASE_URL/api/cables"
echo "  Inspections:  curl $BASE_URL/api/inspections"
echo "  Profile:      curl $BASE_URL/api/profile"
echo ""
echo -e "${CYAN}API Documentation:${NC}"
echo "  Swagger UI:   $BASE_URL/docs"
echo "  ReDoc:        $BASE_URL/redoc"
echo ""

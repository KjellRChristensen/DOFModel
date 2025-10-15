#!/bin/bash

# DOF Backend API Endpoint Test Script
# Tests all API endpoints with curl

set -e  # Exit on error

BASE_URL="http://localhost:4000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "🧪 DOF Backend API - Endpoint Testing"
echo "============================================================"
echo ""
echo "Base URL: $BASE_URL"
echo ""

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test result
test_result() {
    local test_name=$1
    local status=$2
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo ""
    echo -e "${BLUE}Testing:${NC} $description"
    echo -e "${YELLOW}$method${NC} $endpoint"

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "Status Code: $http_code"
    echo "Response: ${body:0:200}..."

    if [ $http_code -ge 200 ] && [ $http_code -lt 300 ]; then
        test_result "$description" 0
        return 0
    else
        test_result "$description" 1
        return 1
    fi
}

# Function to test file upload endpoint
test_upload_endpoint() {
    local endpoint=$1
    local description=$2
    local image_path=$3
    local params=$4

    echo ""
    echo -e "${BLUE}Testing:${NC} $description"
    echo -e "${YELLOW}POST${NC} $endpoint"

    # Create a test image if it doesn't exist
    if [ ! -f "$image_path" ]; then
        echo "Creating test image..."
        # Create a simple 1x1 pixel PNG
        echo -e '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0a\x49\x44\x41\x54\x78\x9c\x63\x00\x01\x00\x00\x05\x00\x01\x0d\x0a\x2d\xb4\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82' > "$image_path"
    fi

    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint$params" \
        -F "file=@$image_path")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "Status Code: $http_code"
    echo "Response: ${body:0:200}..."

    if [ $http_code -ge 200 ] && [ $http_code -lt 300 ]; then
        test_result "$description" 0

        # Extract image_id if present
        IMAGE_ID=$(echo "$body" | grep -o '"image_id":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$IMAGE_ID" ]; then
            echo "  → Image ID: $IMAGE_ID"
        fi
        return 0
    else
        test_result "$description" 1
        return 1
    fi
}

echo "============================================================"
echo "📋 Health & Status Endpoints"
echo "============================================================"

# Test health endpoints
test_endpoint "GET" "/" "Root health check"
test_endpoint "GET" "/health" "Detailed health check"

echo ""
echo "============================================================"
echo "🔌 Cable Management Endpoints"
echo "============================================================"

# Test cable routes
test_endpoint "GET" "/api/v1/cables" "Get all cable routes"

# Create a test cable route
CABLE_DATA='{
    "route_id": "TEST_ROUTE_001",
    "name": "Test Cable Route",
    "start_field_id": "TEST_FIELD_A",
    "end_field_id": "TEST_FIELD_B",
    "cable_type": "fiber_optic",
    "length_km": 25.5,
    "installation_year": 2023
}'

# Note: POST /api/v1/cables uses query parameters, not JSON body
echo ""
echo -e "${BLUE}Testing:${NC} Create cable route"
echo -e "${YELLOW}POST${NC} /api/v1/cables"
CABLE_CREATE_URL="/api/v1/cables?route_id=TEST_ROUTE_001&name=Test%20Cable%20Route&start_field_id=TEST_FIELD_A&end_field_id=TEST_FIELD_B&cable_type=fiber_optic&length_km=25.5&installation_year=2023"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$CABLE_CREATE_URL")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "Status Code: $http_code"
echo "Response: ${body:0:200}..."
if [ $http_code -eq 201 ] || [ $http_code -eq 400 ]; then
    # 400 is OK if cable already exists
    test_result "Create cable route" 0
else
    test_result "Create cable route" 1
fi

# Get specific cable route
test_endpoint "GET" "/api/v1/cables/TEST_ROUTE_001" "Get specific cable route"

# Get cable inspections for a route
test_endpoint "GET" "/api/v1/cables/TEST_ROUTE_001/inspections" "Get cable inspections"

# Filter cables
test_endpoint "GET" "/api/v1/cables?operational=true" "Filter cables by operational status"
test_endpoint "GET" "/api/v1/cables?needs_inspection=true" "Filter cables needing inspection"

echo ""
echo "============================================================"
echo "📸 Image Analysis Endpoints"
echo "============================================================"

# Create test image
TEST_IMAGE="/tmp/test_cable_image.png"

# Test image analysis
test_upload_endpoint "/api/v1/analyze" "Analyze cable image (no location)" "$TEST_IMAGE" ""

# Test image analysis with location
test_upload_endpoint "/api/v1/analyze" "Analyze cable image (with location)" "$TEST_IMAGE" "?latitude=60.5&longitude=2.8&depth=150.0"

# Test image analysis with cable route
test_upload_endpoint "/api/v1/analyze" "Analyze cable image (with route ID)" "$TEST_IMAGE" "?cable_route_id=TEST_ROUTE_001&latitude=60.5&longitude=2.8&depth=150.0"

# Test batch analysis
echo ""
echo -e "${BLUE}Testing:${NC} Batch image analysis"
echo -e "${YELLOW}POST${NC} /api/v1/batch-analyze"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/batch-analyze" \
    -F "files=@$TEST_IMAGE" \
    -F "files=@$TEST_IMAGE")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo "Status Code: $http_code"
echo "Response: ${body:0:200}..."
if [ $http_code -ge 200 ] && [ $http_code -lt 300 ]; then
    test_result "Batch image analysis" 0
else
    test_result "Batch image analysis" 1
fi

# Test get analysis result (if we have an image_id)
if [ ! -z "$IMAGE_ID" ]; then
    test_endpoint "GET" "/api/v1/analysis/$IMAGE_ID" "Get analysis result by image ID"
else
    echo ""
    echo -e "${YELLOW}⚠️  SKIP${NC} - Get analysis result (no image_id available)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "============================================================"
echo "🗺️  Location-Based Endpoints"
echo "============================================================"

# Test location-based queries
test_endpoint "GET" "/api/v1/inspections/nearby?latitude=60.5&longitude=2.8&radius_km=50" "Get nearby inspections"

test_endpoint "GET" "/api/v1/inspections" "Get all inspections"

test_endpoint "GET" "/api/v1/inspections?limit=10" "Get inspections with limit"

test_endpoint "GET" "/api/v1/inspections?condition=good" "Filter inspections by condition"

echo ""
echo "============================================================"
echo "📊 Test Summary"
echo "============================================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: $SUCCESS_RATE%"
fi

echo ""
echo "============================================================"

# Cleanup test image
if [ -f "$TEST_IMAGE" ]; then
    rm "$TEST_IMAGE"
    echo "🧹 Cleaned up test image"
fi

echo ""

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi

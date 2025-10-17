"""
Test script for AI Visual Inspection endpoint
Tests the /api/analyze endpoint with a sample image
"""

import asyncio
import base64
import json
from datetime import datetime
from PIL import Image
import io


def create_test_image() -> str:
    """Create a simple test image and return as base64"""
    # Create a simple 640x640 RGB image
    img = Image.new('RGB', (640, 640), color=(73, 109, 137))

    # Add some patterns to simulate underwater pipeline
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    # Draw a pipeline-like structure
    draw.rectangle([100, 250, 540, 390], fill=(100, 100, 100), outline=(80, 80, 80), width=3)

    # Add some spots to simulate corrosion
    draw.ellipse([200, 280, 250, 330], fill=(150, 80, 60))  # Rust-colored spot
    draw.ellipse([400, 300, 440, 340], fill=(140, 70, 50))  # Another corrosion spot

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64


async def test_visual_inspection_service():
    """Test the visual inspection service directly"""
    from app.services.visual_inspection import VisualInspectionService

    print("="*60)
    print("Testing AI Visual Inspection Service")
    print("="*60)

    # Create service instance
    service = VisualInspectionService()

    # Create test image
    print("\n1. Creating test image...")
    image_data = create_test_image()
    print(f"   ✓ Test image created (base64 length: {len(image_data)})")

    # Analyze image
    print("\n2. Analyzing image...")
    try:
        result = await service.analyze_image(image_data)

        print(f"   ✓ Analysis completed successfully")
        print(f"\n3. Results:")
        print(f"   Analysis ID: {result.id}")
        print(f"   Status: {result.status}")
        print(f"   Processed at: {result.processed_at}")
        print(f"\n   Overall Condition: {result.result.overall_condition}")
        print(f"   Confidence Score: {result.result.confidence}")
        print(f"   Defects Detected: {len(result.result.defects_detected)}")

        if result.result.defects_detected:
            print(f"\n4. Detected Defects:")
            for i, defect in enumerate(result.result.defects_detected, 1):
                print(f"\n   Defect {i}:")
                print(f"      ID: {defect.id}")
                print(f"      Type: {defect.type}")
                print(f"      Severity: {defect.severity}")
                print(f"      Confidence: {defect.confidence:.2%}")
                print(f"      Location: x={defect.location.x}, y={defect.location.y}, "
                      f"w={defect.location.width}, h={defect.location.height}")
                print(f"      Description: {defect.description}")
                if defect.dimensions:
                    print(f"      Dimensions: L={defect.dimensions.length}mm, "
                          f"W={defect.dimensions.width}mm, D={defect.dimensions.depth}mm")

        if result.result.recommendations:
            print(f"\n5. Recommendations:")
            for i, rec in enumerate(result.result.recommendations, 1):
                print(f"   {i}. {rec}")

        print("\n" + "="*60)
        print("✅ Test completed successfully!")
        print("="*60)

        return True

    except Exception as e:
        print(f"   ❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_request_format():
    """Test the request format that frontend will use"""
    from app.models.inspection import ImageAnalysisRequest

    print("\n" + "="*60)
    print("Testing Frontend Request Format")
    print("="*60)

    # Create test image
    image_data = create_test_image()

    # Create request matching frontend format
    request = ImageAnalysisRequest(
        imageData=image_data,
        timestamp=datetime.utcnow(),
        metadata={
            "latitude": 60.5,
            "longitude": 3.5,
            "depth": 125.5
        }
    )

    print("\n✓ Request structure validated")
    print(f"  Image data length: {len(request.imageData)}")
    print(f"  Timestamp: {request.timestamp}")
    print(f"  Metadata: {request.metadata}")

    # Test with service
    from app.services.visual_inspection import VisualInspectionService
    service = VisualInspectionService()

    result = await service.analyze_image(request.imageData)

    print(f"\n✓ Analysis completed")
    print(f"  Response format: {type(result).__name__}")
    print(f"  Status: {result.status}")
    print(f"  Defects: {len(result.result.defects_detected)}")

    print("\n" + "="*60)
    print("✅ Frontend format test completed!")
    print("="*60)


def test_models():
    """Test that all models are properly defined"""
    print("\n" + "="*60)
    print("Testing Model Definitions")
    print("="*60)

    try:
        from app.models.inspection import (
            DefectType, DefectSeverity, AssetCondition,
            DefectLocation, DefectDimensions, DetectedDefect,
            AnalysisResult, AnalysisResponse, ImageAnalysisRequest
        )

        print("\n✓ All models imported successfully")

        # Test enum values
        print(f"\nDefect Types: {[t.value for t in DefectType]}")
        print(f"Severities: {[s.value for s in DefectSeverity]}")
        print(f"Conditions: {[c.value for c in AssetCondition]}")

        print("\n" + "="*60)
        print("✅ Model tests completed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Error importing models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("🔬 AI Visual Inspection - Test Suite")
    print("="*60)

    # Test 1: Model definitions
    test_models()

    # Test 2: Visual inspection service
    await test_visual_inspection_service()

    # Test 3: Frontend request format
    await test_api_request_format()

    print("\n")
    print("="*60)
    print("🎉 All tests completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the server: python main.py")
    print("2. Test the endpoint: POST http://localhost:4000/api/analyze")
    print("3. View API docs: http://localhost:4000/docs")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())

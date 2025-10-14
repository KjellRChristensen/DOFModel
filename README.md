# Underwater Cable Analysis API

FastAPI backend for ML-powered underwater cable image analysis, integrating Ollama and other ML frameworks.

## Features

- 🔍 Image analysis for underwater cables
- 🤖 ML integration with Ollama vision models
- 📊 Detailed condition assessment and defect detection
- 🚀 RESTful API endpoints for iOS frontend
- 📦 Batch image processing support

## Setup

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed locally

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama vision model:
```bash
ollama pull llama3.2-vision:11b
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running the API

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Image Analysis
- `POST /api/v1/analyze` - Analyze single underwater cable image
- `POST /api/v1/batch-analyze` - Analyze multiple images
- `GET /api/v1/analysis/{image_id}` - Retrieve analysis results

## API Documentation

Once running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
DOFBacend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── models/
│   │   └── inference.py   # ML inference logic
│   ├── services/          # Business logic services
│   └── schemas/           # Pydantic models
└── uploads/               # Uploaded images storage
```

## iOS Integration

The API is configured with CORS for iOS frontend communication. Send images via multipart/form-data POST requests to `/api/v1/analyze`.

## Next Steps

1. Integrate authentication (JWT tokens)
2. Add database for storing analysis history
3. Fine-tune ML models for specific cable defects
4. Implement real-time analysis status updates
5. Add image preprocessing pipelines
# DOFModel

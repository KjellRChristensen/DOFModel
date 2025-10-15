# Project Rules

## Python Version
- Always use `python3` command, never `python`
- This project requires Python 3.9+

## Server Management
- **NEVER** start the server automatically
- **ALWAYS** ask the user to start the server
- The user will run `python3 main.py` or `uvicorn main:app --reload`
- Server runs on **port 4000** (not 8000)

## Virtual Environment
- Virtual environment name: **DOF**
- Activate with: `source DOF/bin/activate`
- VS Code auto-activates this environment

## Code Standards
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Document functions and classes with docstrings

## Database
- SQLite for development
- Use SQLAlchemy ORM for all database operations
- Never use raw SQL unless absolutely necessary
- Database location: `data/oil_fields.db`

## API Development
- Use FastAPI for all endpoints
- Include proper error handling and validation
- Document endpoints with clear docstrings
- Return appropriate HTTP status codes

## Dependencies
- All dependencies must be listed in `requirements.txt`
- Pin versions for production stability

## Testing
- Test endpoints before committing
- Ensure database migrations are reversible

## API URLs
- Base URL: http://localhost:4000
- Swagger UI: http://localhost:4000/docs
- ReDoc: http://localhost:4000/redoc

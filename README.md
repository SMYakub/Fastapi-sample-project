
# FastAPI CRUD with PostgreSQL

A FastAPI application with PostgreSQL database for item and inventory management.

## Features

- CRUD operations for items
- Inventory management with stock tracking
- Search and filtering capabilities
- Docker containerization
- PostgreSQL database

## Setup and Running

### Using Docker (Recommended)

1. Clone the repository
2. Run: `docker-compose up --build`
3. Access the API at: `http://localhost:8000`
4. API documentation at: `http://localhost:8000/docs`

### Manual Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up PostgreSQL database
3. Update DATABASE_URL in .env file
4. Run: `uvicorn app.main:app --reload`

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `GET /docs` - API documentation

See the full API documentation at `/docs` when running the application.

# How to run the project:

- Create the project directory structure as shown above

- Copy all the files to their respective locations

- Run: docker-compose up --build

- Access the API at: http://localhost:8000

- API documentation at: http://localhost:8000/docs
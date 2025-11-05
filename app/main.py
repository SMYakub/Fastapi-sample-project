

from fastapi import FastAPI
from app.models.database import engine, Base
from app.routes.items import router as items_router
from app.routes.status import router as status_router
from app.routes.inventory import router as inventory_router
from datetime import datetime

# Import models to ensure they are registered with Base
from app.models.items_models import ItemModel
from app.models.status_models import ItemStatus

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI CRUD with PostgreSQL",
    version="1.0.0",
    description="A simple CRUD API with PostgreSQL database and inventory management"
)

# Include routers
app.include_router(items_router, prefix="/api/v1", tags=["items"])
app.include_router(status_router, prefix="/api/v1", tags=["status"])
app.include_router(inventory_router, prefix="/api/v1", tags=["inventory"])

# Health check endpoints
@app.get("/")
async def root():
    return {"message": "FastAPI CRUD API with PostgreSQL is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "database": "PostgreSQL",
        "timestamp": datetime.now().isoformat()
    }
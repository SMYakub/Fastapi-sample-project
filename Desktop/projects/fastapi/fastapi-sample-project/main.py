

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/fastapi_db"
)

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Added length for PostgreSQL
    description = Column(Text, nullable=True)  # Changed to Text for longer descriptions
    price = Column(Float)
    category = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
    
    model_config = {"from_attributes": True}

# FastAPI app
app = FastAPI(
    title="FastAPI CRUD with PostgreSQL",
    version="1.0.0",
    description="A simple CRUD API with PostgreSQL database"
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def generate_id():
    return str(uuid.uuid4())

# CRUD Operations
@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    item_id = generate_id()
    current_time = datetime.now()
    
    db_item = ItemModel(
        id=item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        created_at=current_time,
        updated_at=current_time
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[ItemResponse])
async def read_all_items(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    items = db.query(ItemModel).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str, 
    item: ItemUpdate, 
    db: Session = Depends(get_db)
):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update only provided fields
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    # Update timestamp
    db_item.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Search items
@app.get("/items/search/", response_model=List[ItemResponse])
async def search_items(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ItemModel)
    
    if name:
        query = query.filter(ItemModel.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(ItemModel.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(ItemModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ItemModel.price <= max_price)
    
    items = query.all()
    return items

# Health check endpoint
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
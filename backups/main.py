from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from sqlalchemy.orm import relationship

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

# SQLAlchemy Models
class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    category = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Relationship with ItemStatus (one-to-one)
    status = relationship("ItemStatus", back_populates="item", uselist=False, cascade="all, delete-orphan")

class ItemStatus(Base):
    __tablename__ = "item_status"
    
    id = Column(String, ForeignKey('items.id'), primary_key=True)
    total_sell = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with ItemModel (one-to-one)
    item = relationship("ItemModel", back_populates="status")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    stock: Optional[int] = 0

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class StatusCreate(BaseModel):
    total_sell: int = 0
    stock: int = 0

class StatusUpdate(BaseModel):
    total_sell: Optional[int] = None
    stock: Optional[int] = None

class StatusResponse(BaseModel):
    id: str
    total_sell: int
    stock: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    created_at: datetime
    updated_at: datetime
    status: Optional[StatusResponse] = None
    
    model_config = {"from_attributes": True}

class ItemWithStatusResponse(BaseModel):
    item: ItemResponse
    status: StatusResponse
    
    model_config = {"from_attributes": True}

# FastAPI app
app = FastAPI(
    title="FastAPI CRUD with PostgreSQL",
    version="1.0.0",
    description="A simple CRUD API with PostgreSQL database and inventory management"
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

# Item CRUD Operations
@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    item_id = generate_id()
    current_time = datetime.now()
    
    # Create item
    db_item = ItemModel(
        id=item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        created_at=current_time,
        updated_at=current_time
    )
    
    # Create status for the item
    db_status = ItemStatus(
        id=item_id,
        total_sell=0,
        stock=item.stock
    )
    
    db.add(db_item)
    db.add(db_status)
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

# Status CRUD Operations
@app.post("/items/{item_id}/status/", response_model=StatusResponse)
async def create_item_status(
    item_id: str, 
    status: StatusCreate, 
    db: Session = Depends(get_db)
):
    # Check if item exists
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if status already exists
    existing_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if existing_status:
        raise HTTPException(status_code=400, detail="Status already exists for this item")
    
    # Create status
    db_status = ItemStatus(
        id=item_id,
        total_sell=status.total_sell,
        stock=status.stock
    )
    
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

@app.get("/items/{item_id}/status/", response_model=StatusResponse)
async def get_item_status(item_id: str, db: Session = Depends(get_db)):
    status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    return status

@app.put("/items/{item_id}/status/", response_model=StatusResponse)
async def update_item_status(
    item_id: str, 
    status: StatusUpdate, 
    db: Session = Depends(get_db)
):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    
    # Update only provided fields
    update_data = status.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_status, field, value)
    
    # Update timestamp
    db_status.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_status)
    return db_status

@app.delete("/items/{item_id}/status/")
async def delete_item_status(item_id: str, db: Session = Depends(get_db)):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    
    db.delete(db_status)
    db.commit()
    return {"message": "Item status deleted successfully"}

# Combined Operations
@app.get("/items/{item_id}/full", response_model=ItemWithStatusResponse)
async def get_item_with_status(item_id: str, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    
    return {
        "item": item,
        "status": status
    }

# Inventory Management Operations
@app.post("/items/{item_id}/sell/", response_model=StatusResponse)
async def sell_item(
    item_id: str, 
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Item status not found")
    
    if db_status.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Update stock and total sales
    db_status.stock -= quantity
    db_status.total_sell += quantity
    db_status.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_status)
    return db_status

@app.post("/items/{item_id}/restock/", response_model=StatusResponse)
async def restock_item(
    item_id: str, 
    quantity: int,
    db: Session = Depends(get_db)
):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Item status not found")
    
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    # Update stock
    db_status.stock += quantity
    db_status.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_status)
    return db_status

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

# Inventory search
@app.get("/inventory/low-stock/", response_model=List[ItemResponse])
async def get_low_stock_items(
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    # Get items with low stock
    low_stock_items = db.query(ItemModel).join(ItemStatus).filter(ItemStatus.stock <= threshold).all()
    return low_stock_items

@app.get("/inventory/top-sellers/", response_model=List[ItemResponse])
async def get_top_sellers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # Get top selling items
    top_sellers = db.query(ItemModel).join(ItemStatus).order_by(ItemStatus.total_sell.desc()).limit(limit).all()
    return top_sellers

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

# Inventory summary
@app.get("/inventory/summary/")
async def inventory_summary(db: Session = Depends(get_db)):
    total_items = db.query(ItemModel).count()
    total_status = db.query(ItemStatus).count()
    
    # Calculate total stock and sales
    total_stock = db.query(db.func.sum(ItemStatus.stock)).scalar() or 0
    total_sales = db.query(db.func.sum(ItemStatus.total_sell)).scalar() or 0
    
    # Low stock items
    low_stock_count = db.query(ItemStatus).filter(ItemStatus.stock <= 10).count()
    
    return {
        "total_items": total_items,
        "items_with_status": total_status,
        "total_stock": total_stock,
        "total_sales": total_sales,
        "low_stock_items": low_stock_count
    }
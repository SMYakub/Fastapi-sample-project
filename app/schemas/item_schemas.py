

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
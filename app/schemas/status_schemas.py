

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .item_schemas import ItemResponse

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

class ItemWithStatusResponse(BaseModel):
    item: ItemResponse
    status: StatusResponse
    
    model_config = {"from_attributes": True}
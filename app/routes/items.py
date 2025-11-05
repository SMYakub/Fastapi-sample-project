from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.schemas.item_schemas import ItemCreate, ItemUpdate, ItemResponse
from app.schemas.status_schemas import ItemWithStatusResponse
from app.crud.items_crud import create_item, get_items, get_item, update_item, delete_item, search_items
from app.crud.status_crud import get_status

router = APIRouter()

@router.post("/items/", response_model=ItemResponse)
async def create_item_route(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db, item)

@router.get("/items/", response_model=List[ItemResponse])
async def read_all_items(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_items(db, skip, limit)

@router.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: str, db: Session = Depends(get_db)):
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item_route(
    item_id: str, 
    item: ItemUpdate, 
    db: Session = Depends(get_db)
):
    updated_item = update_item(db, item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/items/{item_id}")
async def delete_item_route(item_id: str, db: Session = Depends(get_db)):
    success = delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

@router.get("/items/{item_id}/full", response_model=ItemWithStatusResponse)
async def get_item_with_status(item_id: str, db: Session = Depends(get_db)):
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_status = get_status(db, item_id)
    
    return {
        "item": db_item,
        "status": db_status
    }

@router.get("/items/search/", response_model=List[ItemResponse])
async def search_items_route(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    return search_items(db, name, category, min_price, max_price)
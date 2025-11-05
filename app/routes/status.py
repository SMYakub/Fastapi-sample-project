from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.status_schemas import StatusCreate, StatusUpdate, StatusResponse
from app.crud.status_crud import create_status, get_status, update_status, delete_status, sell_item, restock_item
from app.crud.items_crud import get_item

router = APIRouter()

@router.post("/items/{item_id}/status/", response_model=StatusResponse)
async def create_item_status_route(
    item_id: str, 
    status: StatusCreate, 
    db: Session = Depends(get_db)
):
    # Check if item exists
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if status already exists
    existing_status = get_status(db, item_id)
    if existing_status:
        raise HTTPException(status_code=400, detail="Status already exists for this item")
    
    return create_status(db, item_id, status)

@router.get("/items/{item_id}/status/", response_model=StatusResponse)
async def get_item_status_route(item_id: str, db: Session = Depends(get_db)):
    db_status = get_status(db, item_id)
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    return db_status

@router.put("/items/{item_id}/status/", response_model=StatusResponse)
async def update_item_status_route(
    item_id: str, 
    status: StatusUpdate, 
    db: Session = Depends(get_db)
):
    updated_status = update_status(db, item_id, status)
    if not updated_status:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    return updated_status

@router.delete("/items/{item_id}/status/")
async def delete_item_status_route(item_id: str, db: Session = Depends(get_db)):
    success = delete_status(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Status not found for this item")
    return {"message": "Item status deleted successfully"}

@router.post("/items/{item_id}/sell/", response_model=StatusResponse)
async def sell_item_route(
    item_id: str, 
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    result = sell_item(db, item_id, quantity)
    if not result:
        raise HTTPException(status_code=400, detail="Item status not found or insufficient stock")
    return result

@router.post("/items/{item_id}/restock/", response_model=StatusResponse)
async def restock_item_route(
    item_id: str, 
    quantity: int,
    db: Session = Depends(get_db)
):
    result = restock_item(db, item_id, quantity)
    if not result:
        raise HTTPException(status_code=404, detail="Item status not found")
    return result
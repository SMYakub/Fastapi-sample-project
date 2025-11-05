from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.schemas.item_schemas import ItemResponse
from app.crud.status_crud import get_low_stock_items, get_top_sellers
from app.models.items_models import ItemModel
from app.models.status_models import ItemStatus
from sqlalchemy import func

router = APIRouter()

@router.get("/inventory/low-stock/", response_model=List[ItemResponse])
async def get_low_stock_items_route(
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    return get_low_stock_items(db, threshold)

@router.get("/inventory/top-sellers/", response_model=List[ItemResponse])
async def get_top_sellers_route(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_top_sellers(db, limit)

@router.get("/inventory/summary/")
async def inventory_summary_route(db: Session = Depends(get_db)):
    total_items = db.query(ItemModel).count()
    total_status = db.query(ItemStatus).count()
    
    total_stock = db.query(func.sum(ItemStatus.stock)).scalar() or 0
    total_sales = db.query(func.sum(ItemStatus.total_sell)).scalar() or 0
    
    low_stock_count = db.query(ItemStatus).filter(ItemStatus.stock <= 10).count()
    
    return {
        "total_items": total_items,
        "items_with_status": total_status,
        "total_stock": total_stock,
        "total_sales": total_sales,
        "low_stock_items": low_stock_count
    }
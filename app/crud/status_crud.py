

from sqlalchemy.orm import Session
from app.models.status_models import ItemStatus
from app.models.items_models import ItemModel
from app.schemas.status_schemas import StatusCreate, StatusUpdate
from datetime import datetime

def create_status(db: Session, item_id: str, status: StatusCreate):
    db_status = ItemStatus(
        id=item_id,
        total_sell=status.total_sell,
        stock=status.stock
    )
    
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

def get_status(db: Session, item_id: str):
    return db.query(ItemStatus).filter(ItemStatus.id == item_id).first()

def update_status(db: Session, item_id: str, status: StatusUpdate):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        return None
    
    update_data = status.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_status, field, value)
    
    db_status.updated_at = datetime.now()
    db.commit()
    db.refresh(db_status)
    return db_status

def delete_status(db: Session, item_id: str):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if db_status:
        db.delete(db_status)
        db.commit()
        return True
    return False

def sell_item(db: Session, item_id: str, quantity: int = 1):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        return None
    
    if db_status.stock < quantity:
        return None
    
    db_status.stock -= quantity
    db_status.total_sell += quantity
    db_status.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_status)
    return db_status

def restock_item(db: Session, item_id: str, quantity: int):
    db_status = db.query(ItemStatus).filter(ItemStatus.id == item_id).first()
    if not db_status:
        return None
    
    db_status.stock += quantity
    db_status.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_status)
    return db_status

def get_low_stock_items(db: Session, threshold: int = 10):
    return db.query(ItemModel).join(ItemStatus).filter(ItemStatus.stock <= threshold).all()

def get_top_sellers(db: Session, limit: int = 10):
    return db.query(ItemModel).join(ItemStatus).order_by(ItemStatus.total_sell.desc()).limit(limit).all()
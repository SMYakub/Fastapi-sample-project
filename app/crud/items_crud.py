

from sqlalchemy.orm import Session
from app.models.items_models import ItemModel
from app.models.status_models import ItemStatus
from app.schemas.item_schemas import ItemCreate, ItemUpdate
from app.utils.helpers import generate_id
from datetime import datetime

def create_item(db: Session, item: ItemCreate):
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
    
    db_status = ItemStatus(
        id=item_id,
        stock=item.stock
    )
    
    db.add(db_item)
    db.add(db_status)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ItemModel).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: str):
    return db.query(ItemModel).filter(ItemModel.id == item_id).first()

def update_item(db: Session, item_id: str, item: ItemUpdate):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        return None
    
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db_item.updated_at = datetime.now()
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: str):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def search_items(db: Session, name: str = None, category: str = None, 
                min_price: float = None, max_price: float = None):
    query = db.query(ItemModel)
    
    if name:
        query = query.filter(ItemModel.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(ItemModel.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(ItemModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ItemModel.price <= max_price)
    
    return query.all()
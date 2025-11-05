

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class ItemStatus(Base):
    __tablename__ = "item_status"
    
    id = Column(String, ForeignKey('items.id'), primary_key=True)
    total_sell = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with ItemModel (one-to-one)
    item = relationship("ItemModel", back_populates="status")
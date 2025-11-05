

from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with ItemStatus (one-to-one)
    status = relationship("ItemStatus", back_populates="item", uselist=False, cascade="all, delete-orphan")
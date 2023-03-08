from sqlalchemy import (Column, DateTime, ForeignKey,
                        Integer, String)
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship

from models.user import User
from datetime import datetime
from .base import Base


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(TEXT, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', primaryjoin='Category.user_id == User.id')


class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    purchase_name = Column(String(150), nullable=True)
    price = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    category = relationship('Category', primaryjoin='Category.id == Purchase.category_id')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, cascade='delete')
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)

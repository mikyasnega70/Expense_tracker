from sqlalchemy import Column, Integer, Numeric, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
from .database import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    expenses = relationship('Expense', back_populates='user', cascade='all, delete-orphan')

class Catagory(Base):
    __tablename__ = 'catagories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    expenses = relationship('Expense', back_populates='catagory')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2))
    description = Column(String)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    catagory_id = Column(Integer, ForeignKey('catagories.id'))

    user = relationship('Users', back_populates='expenses')
    catagory = relationship('Catagory', back_populates='expenses')




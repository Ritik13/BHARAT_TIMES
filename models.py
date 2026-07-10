from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content= Column(String, nullable=False)
    published= Column(Boolean, default=False)
    created_at= Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

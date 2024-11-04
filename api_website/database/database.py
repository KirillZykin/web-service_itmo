from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session, relationship
from typing import List

# SQLite database URL
DATABASE_URL = "postgresql://myuser:5322@localhost:5432/webdatabase"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Base class for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Связь с пользователем
    owner = relationship("User", back_populates="chats")

# Добавим связь в модель User
User.chats = relationship("Chat", back_populates="owner", cascade="all, delete-orphan")

def get_user_chats(db: Session, user_id: int) -> List[Chat]:
    return db.query(Chat).filter(Chat.owner_id == user_id).all()
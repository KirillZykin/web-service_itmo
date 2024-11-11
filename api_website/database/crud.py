from passlib.context import CryptContext
from orm import UserCreate, ChatCreate
from sqlalchemy.orm import Session
from database import User, Chat

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# CRUD для пользователей
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# CRUD для чатов
def create_chat(db: Session, chat: ChatCreate, owner_id: int):
    db_chat = Chat(name=chat.name, owner_id=owner_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chats_by_user(db: Session, user_id: int):
    return db.query(Chat).filter(Chat.owner_id == user_id).all()

def get_chat_by_id(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).first()

def search_chats_by_name(db: Session, search_term: str):
    return db.query(Chat).filter(Chat.name.ilike(f"%{search_term}%")).all()

def delete_chat(db: Session, chat_id: int, user_id: int):
    chat = get_chat_by_id(db, chat_id)
    if chat and chat.owner_id == user_id:
        db.delete(chat)
        db.commit()
        return True
    return False
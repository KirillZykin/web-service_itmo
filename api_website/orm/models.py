from pydantic import BaseModel, Field
from typing import List, Optional
# Pydantic model for user registration
class UserCreate(BaseModel):
    email: str
    password: str

# Pydantic model for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    id: int

class UserResponse(BaseModel):
    message: str
    user: User


# Схема для создания чата
class ChatCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)

# Схема для отображения информации о чате
class Chat(BaseModel):
    id: int
    name: str
    owner_id: int
    class Config:
        from_attributes = True

# Схема для отображения списка чатов
class ChatListResponse(BaseModel):
    chats: List[Chat]

# Дополнительная схема для успешных операций с чатом
class ChatResponse(BaseModel):
    message: str
    chat: Optional[Chat] = None

class ChatTokenRequest(BaseModel):
    chat_name: str
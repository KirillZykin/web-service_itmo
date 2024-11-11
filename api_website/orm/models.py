from pydantic import BaseModel, Field
from typing import List, Optional
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    id: int

class UserResponse(BaseModel):
    message: str
    user: User


class ChatCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)

class Chat(BaseModel):
    id: int
    name: str
    owner_id: int
    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    chats: List[Chat]

class ChatResponse(BaseModel):
    message: str
    chat: Optional[Chat] = None

class ChatTokenRequest(BaseModel):
    chat_name: str
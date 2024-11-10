import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import Optional, Tuple
from fastapi.middleware.cors import CORSMiddleware
import logging

from auth import get_user_chat
from models import ConnectionManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
manager = ConnectionManager()

async def authenticate_user(websocket: WebSocket, token: str) -> Optional[Tuple[str, str]]:
    user = get_user_chat(token, "email")
    chat = get_user_chat(token, "name_chat")
    if user and chat:
        return user, chat
    else:
        await websocket.send_text("Ошибка: не удалось подключиться")
        return None

async def handle_authentication(websocket: WebSocket, token: str) -> Optional[str]:
    user_data = await authenticate_user(websocket, token)
    if user_data:
        user, chat = user_data
        await manager.update_chat_for_connection(websocket, chat) #TODO надо ли?
        await manager.broadcast(chat, f"{user} присоединился к чату {chat}, поприветствуйте!")
        return chat
    return None

async def handle_message(websocket: WebSocket, chat: str, user: str, message: str):
    if chat:
        await manager.broadcast(f"{user} : {message}", chat)
    else:
        await websocket.send_text("Ошибка: сообщение не отправлено. Вы не подключены к чату.")


@app.websocket("/ws/chat/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "")

    name_chat = ""
    name_user = ""
    try:
        while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "join":
                    token = message.get("token")
                    name_chat = await handle_authentication(websocket, token)
                    name_user = get_user_chat(token, "email")
                else:
                    message = message.get("content")
                    await handle_message(websocket, name_chat, name_user, message)


    except WebSocketDisconnect:
        manager.disconnect(websocket)
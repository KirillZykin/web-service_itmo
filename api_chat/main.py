import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from auth import get_user_chat, auth_user
from models import ConnectionManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
manager = ConnectionManager()

async def handle_authentication(websocket: WebSocket, token: str) -> Optional[str]:
    user_data = await auth_user(websocket, token)
    if user_data:
        user, chat = user_data
        await manager.update_chat_for_connection(websocket, chat)
        await manager.broadcast(f"{user} присоединился к чату, поприветствуйте!", chat)
        return chat
    return None

async def handle_message(websocket: WebSocket, chat: str, user: str, message: str):
    if chat:
        await manager.broadcast(f"{user} : {message}", chat)
    else:
        await websocket.send_text("Ошибка: сообщение не отправлено. Вы не подключены к чату.")

@app.get("/chat/", response_class=HTMLResponse)
def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

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
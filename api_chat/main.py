from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import logging

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_personal_message("Welcome to the WebSocket server!", websocket)
        while True:
            try:
                data = await websocket.receive()
                logger.info(f"Received data: {data}")
                if "text" in data and isinstance(data['type'], str):
                    await manager.broadcast(f"{data['text']}")
                elif "bytes" in data and isinstance(data['bytes'], bytes):
                    await manager.broadcast_binary(data['bytes'])
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                await websocket.close(reason=str(e))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
from typing import List, Tuple
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Tuple[WebSocket,str]] = []

    async def connect(self, websocket: WebSocket, name_chat: str):
        await websocket.accept()
        self.active_connections.append((websocket, name_chat))

    def disconnect(self, websocket: WebSocket):
        # Находим кортеж по WebSocket и удаляем его
        self.active_connections = [
            (conn, chat) for conn, chat in self.active_connections if conn != websocket
        ]

    async def broadcast(self, message: str, name_chat: str):
        for connection, chat in self.active_connections:
            if chat == name_chat:
                try:
                    await connection.send_text(message)
                except Exception:
                    self.disconnect(connection)

    async def update_chat(self, websocket: WebSocket, new_chat: str):
        self.active_connections = [
            (conn, new_chat) if conn == websocket else (conn, chat)
            for conn, chat in self.active_connections
        ]
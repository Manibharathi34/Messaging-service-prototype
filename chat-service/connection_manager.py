import asyncio
import json
import logging
from typing import Dict
from datetime import datetime
from fastapi import WebSocket
from fastapi.websockets import WebSocketState


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            old_ws = self.active_connections[client_id]
            await old_ws.close(code=1000)
            logger.info(f"Replaced existing connection for client {client_id}")
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("connected succesfully!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info(
            f"Client {client_id} connected. Total connections: {len(self.active_connections)}"
        )
        await self.send_message(
            client_id,
            {
                "type": "system",
                "message": f"Connected as {client_id}",
            },
        )

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(
                f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}"
            )

    async def send_message(self, client_id: str, message: dict):
        websocket = self.active_connections.get(client_id)
        if not websocket:
            logger.warning(
                f"Attempted to send message to unknown client_id: {client_id}"
            )
            return

        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                await self.disconnect(client_id)

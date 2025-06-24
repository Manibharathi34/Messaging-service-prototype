import logging
from typing import Dict
from fastapi import WebSocket
from fastapi.websockets import WebSocketState


logger = logging.getLogger(__name__)


class ConnectionManager:
    active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            old_ws = self.active_connections[client_id]
            await old_ws.close(code=1000)
            logger.info("Replaced existing connection for client%s", client_id)
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("connected succesfully!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info(
            "Client %s connected. Total connections: %s",
            client_id,
            len(self.active_connections),
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
                "Client %s disconnected. Total connections: %s",
                client_id,
                len(self.active_connections),
            )

    async def send_message(self, client_id: str, message: dict):
        websocket = self.active_connections.get(client_id)
        if not websocket:
            logger.warning(
                "Attempted to send message to unknown client_id: %s", client_id
            )
            return

        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("Failed to send message to %s: %s", client_id, e)
                await self.disconnect(client_id)

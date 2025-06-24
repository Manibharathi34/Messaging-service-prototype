import json
import logging
from zoneinfo import ZoneInfo
from session_manager import SessionManager
from connection_manager import ConnectionManager
from db.db import DataBase


db = DataBase()
logger = logging.getLogger(__name__)
connection = ConnectionManager()
session = SessionManager()


class MessageProcessor:
    async def process_message(self, message: str):
        """Process incoming WebSocket message and route to appropriate handler."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON message: %s", e)
            return ""
        logger.debug("incoming message is %s", data)
        msg_type = data.get("type")
        if not msg_type:
            logger.error("Message missing 'type' field %s", data)
            return ""
        client_id = ""

        match msg_type:
            case "register":
                client_id = await session.get_user_id(data.get("name"))
                await self.send_undelivered_msgs(client_id)
                return client_id
            case "search_users":
                print(f"incoming message fior search {data}")
                client_id = await session.get_user_id(data.get("name"))
                matches = await session.search_users(data.get("term", ""))
                print(f"sending message for {client_id}")
                await connection.send_message(
                    client_id, {"type": "search_results", "matches": matches}
                )
            case "direct_message":
                await self.send_direct_message(data)
            case "heartbeat":
                logger.info(
                    "Heartbeat received from %s",
                    await session.get_user_id(data.get("name")),
                )
            case _:
                logger.warning("Unknown message type: %s", msg_type)
                await connection.send_message(
                    client_id,
                    {"type": "error", "message": f"Unknown message type: {msg_type}"},
                )

        return client_id

    async def send_direct_message(self, data):
        to_client_id = await session.get_user_id(data["to"])
        from_client_id = await session.get_user_id(data["from"])
        if not to_client_id:
            logger.error("Recipient '%s' not found", data["to"])
            return ""
        status = await connection.send_message(
            to_client_id,
            {
                "type": "direct_message",
                "message": data["text"],
                "from": data["from"],
            },
        )
        await db.save_message_with_chat(
            receiver_id=to_client_id,
            sender_id=from_client_id,
            text=data["text"],
            status=status,
        )
        await connection.send_message(
            from_client_id,
            {
                "type": "message_delivery_status",
                "status": status,
            },
        )

    async def send_undelivered_msgs(self, user_id: str):
        results = await db.get_undelivered_messages(user_id)
        messages = []
        for record in results:
            utc_time = record["time"].astimezone(ZoneInfo("UTC"))
            formatted_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(
                {
                    "sender": record["sender_name"],
                    "text": record["text"],
                    "time": formatted_time,
                }
            )
        await connection.send_message(
            user_id,
            {
                "type": "unread_messages",
                "messages": messages,
            },
        )

import json
import logging
from session_manager import SessionManager
from connection_manager import ConnectionManager


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
                return client_id
            case "search_users":
                client_id = session.get_user_client_id(data.get("name"))
                matches = await session.search_users(data.get("term", ""))
                await connection.send_message(
                    client_id, {"type": "search_results", "matches": matches}
                )
            case "direct_message":
                to_client_id = session.get_user_client_id(data["to"])
                if not to_client_id:
                    logger.error("Recipient '%s' not found", data["to"])
                    return ""
                await connection.send_message(
                    to_client_id,
                    {
                        "type": "direct_message",
                        "message": data["text"],
                        "from": data["from"],
                    },
                )
            case "heartbeat":
                logger.info(
                    "Heartbeat received from %s",
                    session.get_user_client_id(data.get("name")),
                )
            case _:
                logger.warning("Unknown message type: %s", msg_type)
                await connection.send_message(
                    client_id,
                    {"type": "error", "message": f"Unknown message type: {msg_type}"},
                )

        return client_id

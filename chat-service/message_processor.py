import json
import logging
from session_manager import SessionManager
from connection_manager import ConnectionManager


logger = logging.getLogger(__name__)
connection = ConnectionManager()
session = SessionManager()


class MessageProcessor:
    async def process_message(self, message: str):
        data = json.loads(message)
        print(f"incoming msg = {data}")
        msg_type = data.get("type")
        client_id = ""

        match msg_type:
            case "register":
                return client_id
            case "search_users":
                client_id = session.get_user_client_id(data.get("name"))
                matches = session.get_user(data.get("term", ""))
                await connection.send_message(
                    client_id, {"type": "search_results", "matches": matches}
                )
            case "direct_message":
                to_client_id = session.get_user_client_id(data["to"])
                print(f"to client is {to_client_id}")
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
                    f"💓 Heartbeat received from {session.get_user_client_id(data.get('name'))}"
                )
            case _:
                await connection.send_message(
                    client_id,
                    {"type": "error", "message": f"Unknown message type: {msg_type}"},
                )

        return client_id

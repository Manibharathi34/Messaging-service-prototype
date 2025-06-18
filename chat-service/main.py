from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse
from connection_manager import ConnectionManager
from session_manager import SessionManager
import logging
import json

connection = ConnectionManager()
session = SessionManager()

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/startchat")
async def start_chat(name: str = Query(...)):
    user_client_id = session.get_user_client_id(name)
    return JSONResponse(
        {"status": "ok", "message": "initiate chat", "id": user_client_id}
    )


@app.websocket("/startchat/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = websocket.query_params.get("clientId")
    logger.info(f"Client ID received in WebSocket initiation: {client_id}")
    await connection.connect(client_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            client_id = await process_message(message)  # ✅ Pass websocket context
    except Exception as e:
        logger.warning(f"WebSocket disconnected: {e}")
        await connection.disconnect(client_id)  # ✅ Await this!


# to be moved to seperate service
async def process_message(message: str):
    data = json.loads(message)
    msg_type = data.get("type")
    client_id = data.get("client_id")

    match msg_type:
        case "register":
            # Already connected in initial handshake
            return client_id
        case "search_users":
            matches = session.get_user(data.get("id", ""))
            await connection.send_message(
                client_id, {"type": "search_results", "matches": matches}
            )
        case "heartbeat":
            logger.info(f"💓 Heartbeat received from {client_id}")
        case _:
            await connection.send_message(
                client_id,
                {"type": "error", "message": f"Unknown message type: {msg_type}"},
            )

    return client_id

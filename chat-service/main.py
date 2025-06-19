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
    session.initialize_session(name)
    return JSONResponse({"status": "ok", "message": "initiate chat", "id": name})


@app.websocket("/startchat/ws")
async def websocket_endpoint(websocket: WebSocket):
    name = websocket.query_params.get("name")
    logger.info(f"name received in WebSocket initiation: {name}")
    client_id = session.get_user_client_id(name)
    await connection.connect(client_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            client_id = await process_message(message)
    except Exception as e:
        logger.warning(f"WebSocket disconnected: {e}")
        await connection.disconnect(client_id)


# to be moved to seperate service
async def process_message(message: str):
    print(f"incoming message = {message}")
    data = json.loads(message)
    msg_type = data.get("type")
    client_id = ""

    match msg_type:
        case "register":
            # Already connected in initial handshake
            return client_id
        case "search_users":
            client_id = session.get_user_client_id(data.get("name"))
            matches = session.get_user(data.get("term", ""))
            await connection.send_message(
                client_id, {"type": "search_results", "matches": matches}
            )
        case "direct_message":
            to_client_id = session.get_user_client_id(data["to"])
            print(f"direct message incoming {data} to {to_client_id} for {data['to']}")
            await connection.send_message(
                to_client_id,
                {
                    "type": "direct_message",
                    "message": data["text"],
                    "from": data["from"],
                },
            )
        case "heartbeat":
            logger.info(f"💓 Heartbeat received from {client_id}")
        case _:
            await connection.send_message(
                client_id,
                {"type": "error", "message": f"Unknown message type: {msg_type}"},
            )

    return client_id

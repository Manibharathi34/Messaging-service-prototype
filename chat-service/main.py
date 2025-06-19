from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse
from connection_manager import ConnectionManager
from session_manager import SessionManager
from message_processor import MessageProcessor
import logging

connection = ConnectionManager()
session = SessionManager()
msg_processor = MessageProcessor()
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
            client_id = await msg_processor.process_message(message)
    except Exception as e:
        logger.warning(f"WebSocket disconnected: {e}")
        await connection.disconnect(client_id)

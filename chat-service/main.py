from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse
from connection_manager import ConnectionManager
from session_manager import SessionManager
from message_processor import MessageProcessor
import logging
from db.db_connection import database, engine
from db.models import metadata

connection = ConnectionManager()
session = SessionManager()
msg_processor = MessageProcessor()
app = FastAPI()
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    try:
        metadata.create_all(engine)
        print("#### tables created #################")
        await database.connect()
        print("Database connected successfully!!!!!!!!!! ##########")

        logger.info(" Connected to DB")
    except Exception as e:
        logger.error(f"DB connection failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/startchat")
async def start_chat(name: str = Query(...)):
    await session.initialize_session(name)
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

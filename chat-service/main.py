import logging
from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse
from connection_manager import ConnectionManager
from session_manager import SessionManager
from message_processor import MessageProcessor
from db.db_connection import database, engine
from db.models import metadata
from utils.logger import setup_logger

setup_logger()

connection = ConnectionManager()
session = SessionManager()
msg_processor = MessageProcessor()
app = FastAPI()
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    try:
        metadata.create_all(engine)
        logger.info("#### tables created #################")
        await database.connect()
        logger.info("Database connected successfully!!!!!!!!!! ##########")

        logger.info(" Connected to DB")
    except Exception as e:
        logger.error(f"DB connection failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/startchat")
async def start_chat(name: str = Query(...)):
    await session.get_user_id(name)
    return JSONResponse({"status": "ok", "message": "initiate chat", "id": name})


@app.websocket("/startchat/ws")
async def websocket_endpoint(websocket: WebSocket):
    name = websocket.query_params.get("name")
    logger.info("name received in WebSocket initiation: %s", name)
    client_id = await session.get_user_id(name)
    await connection.connect(client_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            client_id = await msg_processor.process_message(message)
    except Exception as e:
        logger.warning("WebSocket disconnected: %s", e)
        await connection.disconnect(client_id)

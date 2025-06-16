from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/startchat")
async def start_chat(name: str = Query(...), id: str = Query(...)):
    print(f"Received {name} and {id}")
    return JSONResponse({"status": "ok", "message": "initiate chat", "id": id})

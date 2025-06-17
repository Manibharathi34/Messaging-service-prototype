from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/startchat")
async def start_chat(name: str = Query(...), id: str = Query(...)):
    print(f"Received {name} and {id}")
    return JSONResponse({"status": "ok", "message": "initiate chat", "id": id})


@app.websocket("/startchat/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received over WS: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket disconnected: {e}")

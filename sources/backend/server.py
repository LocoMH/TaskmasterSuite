from typing import List
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import uvicorn
import multiprocessing

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        print(f"client connected")

    async def broadcast(self, data: str):
        print(f"broadcasting: \"{data}\"")
        for connection in self.connections:
            await connection.send_text(data)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
        print(f"client disconnected")


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.split("+++")[0] == "":
                pass

            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Start up API
if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8001, loop='asyncio')

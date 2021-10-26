import threading
import logging
from typing import List
from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
import uvicorn
import multiprocessing
from loader import generate_files
import ctypes
import helper
import db

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)


manager = ConnectionManager()

app.mount("/home/", StaticFiles(directory=helper.find_root()), name="static")


@app.get("/data/contestants")
async def get_contestants():
    return db.get_contestants()


@app.get("/data/tasks")
async def get_tasks():
    return db.get_tasks()


@app.get("/data/special_images")
async def get_special_images():
    return db.get_special_images()


@app.delete("/data/scores")
async def delete_scores():
    db.clear_scores()
    return Response(status_code=204)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_list = data.split("+++")
            if data_list[0] == "setScore":
                db.add_score(data_list[1], data_list[2], data_list[3])

            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def start_file_generation():
    generate_files()
    threading.Timer(1, start_file_generation).start()


def show_window():
    ctypes.windll.user32.MessageBoxW(
        0, "The Taskmaster Suite was succesfully launched!\n\nConnect to\n\nhttp://" + helper.get_ip() + ":8001/home/screen.html\n\nand\n\nhttp://" + helper.get_ip() + ":8001/home/assistant.html\n\non any computer in your network in order to use the application.\n\nNote that closing this window does not stop the application. Closing the command prompt window does.", "Successfully started", 0)


@app.on_event("startup")
async def startup_event():
    file_generation_thread = threading.Timer(0, start_file_generation)
    file_generation_thread.daemon = True
    file_generation_thread.start()

    file_generation_thread = threading.Timer(0, show_window)
    file_generation_thread.daemon = True
    file_generation_thread.start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8001, loop='asyncio')

import threading
from typing import List
from fastapi import FastAPI, WebSocket, Response
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
import uvicorn
import multiprocessing
from .loader import generate_files
from . import helper
from . import db
import easygui
import ujson
import asyncio

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
app.mount("/exp/", StaticFiles(directory=helper.find_root() +
          "/sources/frontend_vue"), name="static")


@app.get("/data/contestants")
async def get_contestants():
    return await db.get_contestants()


@app.get("/data/tasks")
async def get_tasks():
    return await db.get_tasks()


@app.get("/data/special_images")
async def get_special_images():
    return await db.get_special_images()


@app.delete("/data/scores")
async def delete_scores():
    await db.clear_scores()
    return Response(status_code=204)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_list = data.split("+++")
            if data_list[0] == "setScore":
                await db.add_score(data_list[1], data_list[2], data_list[3])

            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def start_file_generation():
    while True:
        await generate_files()
        await asyncio.sleep(1)


def show_window():
    easygui.msgbox("The Taskmaster Suite was succesfully launched!\n\nConnect to\n\nhttp://" + helper.get_ip() + ":8001/home/screen.html\n\nand\n\nhttp://" + helper.get_ip() +
                   ":8001/home/assistant.html\n\non any computer in your network in order to use the application.\n\nNote that closing this window does not stop the application. Closing the command prompt window does.", "Successfully started")


@app.on_event("startup")
async def startup_event():
    file_generation_thread = threading.Timer(0, show_window)
    file_generation_thread.daemon = True
    file_generation_thread.start()

    loop = asyncio.get_running_loop()
    loop.create_task(start_file_generation())


def start_server():
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8001, loop='asyncio')


if __name__ == "__main__":
    start_server()

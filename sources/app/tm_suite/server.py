import asyncio
import multiprocessing
import threading
from typing import List

import easygui
import ujson
import uvicorn
from fastapi import FastAPI
from fastapi import Response
from fastapi import WebSocket
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect
from tm_suite import db
from tm_suite import helper
from tm_suite.loader import generate_files

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
    return await db.get_contestants()


@app.get("/data/contestants_with_total_score")
async def get_contestants():
    return await db.get_contestants_with_total_score()


@app.get("/data/tasks")
async def get_tasks():
    return await db.get_tasks()


@app.get("/data/general_files")
async def get_general_files():
    return await db.get_general_files()


@app.get("/data/note")
async def get_note():
    return await db.get_note()


class Note(BaseModel):
    text: str


@app.post("/data/note")
async def set_note(note: Note):
    await db.update_note(note.text)
    return Response(status_code=200)


@app.get("/data/scores")
async def get_scores():
    return await db.get_scores()


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
            print("received msg: " + data)
            data_list = data.split("+++")
            if data_list[0] == "setScore":
                await db.add_score(data_list[1], data_list[2], data_list[3])

            if data_list[0] == "__ping__":
                await websocket.send_text("__pong__")
            else:
                await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def start_file_generation():
    while True:
        await generate_files()
        await asyncio.sleep(1)


def show_window():
    easygui.msgbox(
        "The Taskmaster Suite was succesfully launched!\n\nTo use the application, open a browser.\n\nFor the audience screen, open this website:\n\nhttp://"
        + helper.get_ip()
        + ":8001/home/screen.html\n\nFor the assistant screen, open this website:\n\nhttp://"
        + helper.get_ip()
        + ":8001/home/assistant.html\n\nYou can open the websites on any device (including Android/iOS) in your private WiFi network in order to use the application.\n\nNote that closing this window does not stop the application. Closing the black command prompt window does.",
        "Successfully started",
    )


@app.on_event("startup")
async def startup_event():
    file_generation_thread = threading.Timer(0, show_window)
    file_generation_thread.daemon = True
    file_generation_thread.start()

    loop = asyncio.get_running_loop()
    loop.create_task(start_file_generation())


def start_server():
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8001, loop="asyncio")


if __name__ == "__main__":
    start_server()

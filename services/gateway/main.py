import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

import broadcaster


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(broadcaster.poll_loop())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    broadcaster.register(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.unregister(websocket)

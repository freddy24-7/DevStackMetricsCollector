import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

import broadcaster

app = FastAPI()


@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcaster.poll_loop())


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    broadcaster.register(websocket)
    try:
        while True:
            # Keep connection alive; client sends pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.unregister(websocket)

from fastapi import APIRouter, Request
import socketio
from typing import Callable

streaming_socket_router = APIRouter()

class StreamingSocket:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

    async def handle_request(self, request: Request):
        return await self.sio.handle_request(request)

    async def emit_audio(self, audio_data: bytes):
        await self.sio.emit('audio_data', {'audio': audio_data.decode()})

    def on_connect(self, handler: Callable):
        self.sio.on('connect')(handler)

    def on_disconnect(self, handler: Callable):
        self.sio.on('disconnect')(handler)

streaming_socket = StreamingSocket()

@streaming_socket_router.get("/socket.io/")
@streaming_socket_router.post("/socket.io/")
async def socket_handler(request: Request):
    return await streaming_socket.handle_request(request)

@streaming_socket.on_connect
async def handle_connect(sid):
    print(f"Client connected: {sid}")

@streaming_socket.on_disconnect
async def handle_disconnect(sid):
    print(f"Client disconnected: {sid}")
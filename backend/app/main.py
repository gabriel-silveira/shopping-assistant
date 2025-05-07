from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from .core.chat_manager import ChatManager
from .models.chat import ChatMessage
from datetime import datetime

app = FastAPI(title="Shopping Assistant API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chat sessions
chat_sessions: Dict[str, ChatManager] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    if client_id not in chat_sessions:
        chat_sessions[client_id] = ChatManager()
    
    # Send initial greeting
    initial_message = None
    response = chat_sessions[client_id].process_message(initial_message)
    await websocket.send_text(response.model_dump_json())
    
    try:
        while True:
            # receive message from client
            data = await websocket.receive_text()
            message = ChatMessage.parse_raw(data)
            
            # Process message synchronously
            response = chat_sessions[client_id].process_message(message)
            
            # Send response back to client
            await websocket.send_text(response.model_dump_json())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client_id in chat_sessions:
            del chat_sessions[client_id]

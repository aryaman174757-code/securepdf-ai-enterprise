import json
from typing import Dict, List, Any
from fastapi import WebSocket

class WebSocketConnectionManager:
    """
    Real-Time WebSocket Hub for Live Progress Broadcasting.
    Manages active client connections per user and job ID.
    """

    def __init__(self):
        # Map user_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map job_id -> List[WebSocket]
        self.job_subscribers: Dict[str, List[WebSocket]] = {}

    async def connect_user(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect_user(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def subscribe_job(self, websocket: WebSocket, job_id: str):
        if job_id not in self.job_subscribers:
            self.job_subscribers[job_id] = []
        if websocket not in self.job_subscribers[job_id]:
            self.job_subscribers[job_id].append(websocket)

    async def broadcast_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Sends real-time event to all active sessions of a user."""
        message = json.dumps({"event": event_type, "data": data})
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass

    async def broadcast_job_progress(self, job_id: str, status: str, progress: float, details: Dict[str, Any] = None):
        """Sends job progress update to all subscribers."""
        payload = {
            "job_id": job_id,
            "status": status,
            "progress": progress,
            "details": details or {}
        }
        message = json.dumps({"event": "JOB_PROGRESS", "data": payload})
        if job_id in self.job_subscribers:
            for connection in self.job_subscribers[job_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass

ws_manager = WebSocketConnectionManager()

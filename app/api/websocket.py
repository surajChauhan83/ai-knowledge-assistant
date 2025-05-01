# app/api/websocket.py
from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
async def get_websocket_page():
    return HTMLResponse(content="""
        <html>
            <body>
                <h2>WebSocket Test</h2>
                <p>Open your WebSocket client (e.g., WebSocket King) and connect to:</p>
                <code>ws://localhost:8000/ws/</code>
            </body>
        </html>
    """)

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

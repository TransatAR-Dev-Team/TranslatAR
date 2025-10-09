from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Unity connected!")
    
    try:
        while True:
            # Receive the message
            data = await websocket.receive_text()
            print(f"Received from Unity: {data}")
            
            # Send a response back
            await websocket.send_text(f"FastAPI received: {data}")
                
    except Exception as e:
        print(f"Error: {e}")
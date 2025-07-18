from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.chat_service import handle_chat
from app.database import get_db, create_tables
from app.models import SchemaObject, SchemaWorkflow
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.post("/save-schema")
async def save_schema(schema_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        # Extract objects and workflows
        objects = schema_data.get("objects", {})
        workflows = schema_data.get("workflows", {})
        
        # Save objects to database
        for object_name, object_data in objects.items():
            db_object = SchemaObject(
                name=object_name,
                fields=object_data.get("fields", {})
            )
            db.add(db_object)
        
        # Save workflows to database
        for workflow_name, workflow_data in workflows.items():
            db_workflow = SchemaWorkflow(
                name=workflow_name,
                steps=workflow_data.get("steps", [])
            )
            db.add(db_workflow)
        
        # Commit all changes
        db.commit()
        
        return {
            "success": True,
            "message": "Schema saved successfully to database",
            "saved": {
                "objects": list(objects.keys()),
                "workflows": list(workflows.keys())
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save schema: {str(e)}")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse the message with context
            try:
                parsed_data = json.loads(data)
                messages = parsed_data.get("messages")
                context = parsed_data.get("context", {})
                session_id = context.get("session_id", "default")
            except json.JSONDecodeError:
                # Fallback for plain text messages
                messages = None
                session_id = "default"
            
            # Use the chat service to process the message and stream response
            if messages:
                async for chunk in handle_chat(messages=messages, session_id=session_id):
                    await websocket.send_text(chunk)
            else:
                # Fallback: treat as single message
                message = parsed_data.get("message", "") if 'parsed_data' in locals() else data
                async for chunk in handle_chat(messages=[{"role": "user", "content": message}], session_id=session_id):
                    await websocket.send_text(chunk)
    except WebSocketDisconnect:
        pass 
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.chat_service import handle_chat
from app.database import get_db, create_tables
from app.models import SchemaObject, SchemaWorkflow, SchemaApp, AppStatus, User, AppUser, UserRole, SchemaRecord, Metadata
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class AppCreate(BaseModel):
    name: str
    description: str = ""
    status: AppStatus = AppStatus.DRAFT
    app_metadata: Dict[str, Any] = {}

class AppResponse(BaseModel):
    id: int
    name: str
    description: str
    status: AppStatus
    app_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/apps", response_model=List[AppResponse])
async def get_apps(db: Session = Depends(get_db)):
    """Get all apps"""
    apps = db.query(SchemaApp).order_by(SchemaApp.created_at.desc()).all()
    return apps

@app.get("/apps/{app_id}/workflows")
async def get_app_workflows(app_id: int, db: Session = Depends(get_db)):
    """Get workflows for a specific app"""
    workflows = db.query(SchemaWorkflow).filter(SchemaWorkflow.app_id == app_id).all()
    return workflows

@app.post("/workflows")
async def create_workflow(workflow_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new workflow"""
    try:
        db_workflow = SchemaWorkflow(
            name=workflow_data.get("name", "Untitled Workflow"),
            steps=workflow_data.get("steps", []),
            app_id=workflow_data.get("app_id")
        )
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        return db_workflow
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@app.get("/apps/{app_id}/objects")
async def get_app_objects(app_id: int, db: Session = Depends(get_db)):
    """Get all objects (cross-app for now until proper object-app relationships are implemented)"""
    # TODO: In the future, implement proper app-object relationships
    # For now, show all objects to all apps so users can work with existing data
    objects = db.query(SchemaObject).all()
    return objects

@app.post("/objects")
async def create_object(object_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new object"""
    try:
        db_object = SchemaObject(
            name=object_data.get("name", "Untitled Object"),
            fields=object_data.get("fields", {}),
            app_id=object_data.get("app_id")
        )
        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create object: {str(e)}")

# Metadata endpoints
@app.get("/metadata")
async def get_metadata(key: str = None, app_id: int = None, db: Session = Depends(get_db)):
    """Get metadata by key, app_id, or all metadata"""
    try:
        query = db.query(Metadata)
        
        if key:
            query = query.filter(Metadata.key == key)
        if app_id is not None:
            query = query.filter(Metadata.app_id == app_id)
        
        metadata_list = query.all()
        
        # If looking for field_types with app_id but none found, include global ones
        if key == "field_types" and app_id is not None and not metadata_list:
            global_query = db.query(Metadata).filter(
                Metadata.key == key,
                Metadata.app_id.is_(None)
            )
            global_metadata = global_query.all()
            metadata_list.extend(global_metadata)
        
        if key and metadata_list:
            # If we have multiple entries (app-specific + global), return array
            if len(metadata_list) > 1:
                return metadata_list
            # Otherwise return single metadata value
            return metadata_list[0]
        else:
            # Return all matching metadata
            return metadata_list
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

@app.post("/metadata")
async def create_metadata(metadata_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create or update metadata"""
    try:
        key = metadata_data.get("key")
        if not key:
            raise HTTPException(status_code=400, detail="Key is required")
        
        # Check if metadata already exists
        existing = db.query(Metadata).filter(Metadata.key == key).first()
        
        if existing:
            # Update existing metadata
            existing.value = metadata_data.get("value")
            existing.description = metadata_data.get("description")
            existing.app_id = metadata_data.get("app_id")
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new metadata
            db_metadata = Metadata(
                key=key,
                value=metadata_data.get("value", {}),
                description=metadata_data.get("description"),
                app_id=metadata_data.get("app_id")
            )
            db.add(db_metadata)
            db.commit()
            db.refresh(db_metadata)
            return db_metadata
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create/update metadata: {str(e)}")

@app.delete("/metadata/{key}")
async def delete_metadata(key: str, db: Session = Depends(get_db)):
    """Delete metadata by key"""
    try:
        metadata = db.query(Metadata).filter(Metadata.key == key).first()
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        db.delete(metadata)
        db.commit()
        return {"message": "Metadata deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete metadata: {str(e)}")

@app.post("/apps", response_model=AppResponse)
async def create_app(app_data: AppCreate, db: Session = Depends(get_db)):
    """Create a new app"""
    try:
        db_app = SchemaApp(
            name=app_data.name,
            description=app_data.description,
            status=app_data.status,
            app_metadata=app_data.app_metadata
        )
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        return db_app
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create app: {str(e)}")

@app.post("/save-schema")
async def save_schema(schema_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        # Extract objects, workflows, and app_id
        objects = schema_data.get("objects", {})
        workflows = schema_data.get("workflows", {})
        app_id = schema_data.get("app_id")
        
        # Save objects to database
        for object_name, object_data in objects.items():
            db_object = SchemaObject(
                name=object_name,
                fields=object_data.get("fields", {})
            )
            db.add(db_object)
        
        # Save workflows to database with app_id reference
        for workflow_name, workflow_data in workflows.items():
            db_workflow = SchemaWorkflow(
                name=workflow_name,
                steps=workflow_data.get("steps", []),
                app_id=app_id
            )
            db.add(db_workflow)
        
        # Commit all changes
        db.commit()
        
        return {
            "success": True,
            "message": "Schema saved successfully to database",
            "saved": {
                "objects": list(objects.keys()),
                "workflows": list(workflows.keys()),
                "app_id": app_id
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save schema: {str(e)}")

@app.put("/workflows/{workflow_id}/layout")
async def update_workflow_layout(workflow_id: int, layout_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Update layout for a specific workflow"""
    try:
        workflow = db.query(SchemaWorkflow).filter(SchemaWorkflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update the workflow with the new layout
        workflow.layout = layout_data.get("layout", [])
        workflow.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(workflow)
        
        return {
            "success": True,
            "message": "Layout updated successfully",
            "workflow_id": workflow_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update layout: {str(e)}")

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

# User management endpoints
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{"id": user.id, "name": user.name, "email": user.email} for user in users]

@app.get("/users/{user_id}/apps")
async def get_user_apps(user_id: int, db: Session = Depends(get_db)):
    """Get apps available to a specific user"""
    try:
        # Get all app assignments for this user
        app_users = db.query(AppUser).filter(AppUser.user_id == user_id).all()
        
        # Get the actual app details for each assignment
        user_apps = []
        for app_user in app_users:
            app = db.query(SchemaApp).filter(SchemaApp.id == app_user.app_id).first()
            if app:
                user_apps.append({
                    "id": app.id,
                    "name": app.name,
                    "description": app.description,
                    "status": app.status.value,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                    "role": app_user.role.value
                })
        
        return user_apps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user apps: {str(e)}")

@app.get("/apps/{app_id}/users")
async def get_app_users(app_id: int, db: Session = Depends(get_db)):
    """Get users assigned to a specific app"""
    app_users = db.query(AppUser).filter(AppUser.app_id == app_id).all()
    
    # Get user details for each app user
    users_with_roles = []
    for app_user in app_users:
        user = db.query(User).filter(User.id == app_user.user_id).first()
        if user:
            users_with_roles.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": app_user.role.value
            })
    
    return users_with_roles

@app.post("/apps/{app_id}/users")
async def add_user_to_app(app_id: int, user_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Add a user to an app with a specific role"""
    try:
        user_id = user_data.get("user_id")
        role = user_data.get("role", "user")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if app exists
        app = db.query(SchemaApp).filter(SchemaApp.id == app_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Check if user is already assigned to this app
        existing_assignment = db.query(AppUser).filter(
            AppUser.app_id == app_id,
            AppUser.user_id == user_id
        ).first()
        
        if existing_assignment:
            raise HTTPException(status_code=400, detail="User is already assigned to this app")
        
        # Create app user assignment
        app_user = AppUser(
            app_id=app_id,
            user_id=user_id,
            role=UserRole(role)
        )
        
        db.add(app_user)
        db.commit()
        db.refresh(app_user)
        
        return {
            "success": True,
            "message": "User added to app successfully",
            "app_user_id": app_user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add user to app: {str(e)}")

@app.put("/apps/{app_id}/users/{user_id}")
async def update_user_role(app_id: int, user_id: int, role_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Update a user's role in an app"""
    try:
        new_role = role_data.get("role")
        
        # Find the app user assignment
        app_user = db.query(AppUser).filter(
            AppUser.app_id == app_id,
            AppUser.user_id == user_id
        ).first()
        
        if not app_user:
            raise HTTPException(status_code=404, detail="User is not assigned to this app")
        
        # Update the role
        app_user.role = UserRole(new_role)
        app_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(app_user)
        
        return {
            "success": True,
            "message": "User role updated successfully",
            "app_user_id": app_user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

@app.delete("/apps/{app_id}/users/{user_id}")
async def remove_user_from_app(app_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove a user from an app"""
    try:
        # Find the app user assignment
        app_user = db.query(AppUser).filter(
            AppUser.app_id == app_id,
            AppUser.user_id == user_id
        ).first()
        
        if not app_user:
            raise HTTPException(status_code=404, detail="User is not assigned to this app")
        
        # Delete the assignment
        db.delete(app_user)
        db.commit()
        
        return {
            "success": True,
            "message": "User removed from app successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove user from app: {str(e)}")

# Records endpoints
@app.get("/objects/{object_id}/records")
async def get_object_records(object_id: int, db: Session = Depends(get_db)):
    """Get all records for a specific object"""
    try:
        records = db.query(SchemaRecord).filter(SchemaRecord.object_id == object_id).all()
        return [{"id": record.id, "data": record.data, "created_at": record.created_at.isoformat(), "updated_at": record.updated_at.isoformat()} for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get records: {str(e)}")

@app.post("/objects/{object_id}/records")
async def create_record(object_id: int, record_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new record for an object"""
    try:
        # Check if object exists
        object_obj = db.query(SchemaObject).filter(SchemaObject.id == object_id).first()
        if not object_obj:
            raise HTTPException(status_code=404, detail="Object not found")
        
        record = SchemaRecord(
            object_id=object_id,
            data=record_data.get("data", {})
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return {
            "id": record.id,
            "data": record.data,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")

@app.put("/records/{record_id}")
async def update_record(record_id: int, record_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Update a record"""
    try:
        record = db.query(SchemaRecord).filter(SchemaRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        record.data = record_data.get("data", record.data)
        record.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(record)
        
        return {
            "id": record.id,
            "data": record.data,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update record: {str(e)}")

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: int, execution_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Execute a workflow with form data and record context"""
    try:
        # Get the workflow
        workflow = db.query(SchemaWorkflow).filter(SchemaWorkflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get form data, user ID, and record context
        form_data = execution_data.get("formData", {})
        user_id = execution_data.get("userId")
        record_id = execution_data.get("recordId")
        current_step = execution_data.get("currentStep", 0)
        
        # Get record context if provided
        record_context = {}
        if record_id:
            record = db.query(SchemaRecord).filter(SchemaRecord.id == record_id).first()
            if record:
                record_context = record.data
        
        # Process workflow step with layout if available
        workflow_layout = workflow.layout if workflow.layout else []
        
        # In a real application, you would:
        # 1. Validate user permissions for this workflow
        # 2. Process the workflow steps with the form data and record context
        # 3. Store execution results
        # 4. Handle any external integrations
        
        # For now, we'll return a success response with context
        return {
            "success": True,
            "message": "Workflow executed successfully",
            "workflow_id": workflow_id,
            "execution_id": f"exec_{workflow_id}_{int(datetime.utcnow().timestamp())}",
            "form_data": form_data,
            "record_context": record_context,
            "workflow_layout": workflow_layout,
            "current_step": current_step,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}") 
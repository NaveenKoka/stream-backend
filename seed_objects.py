#!/usr/bin/env python3
"""
Seed script to add sample objects to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SchemaObject, SchemaApp

def seed_objects():
    """Add sample objects to the database"""
    db = SessionLocal()
    
    try:
        # Get existing apps
        apps = db.query(SchemaApp).all()
        
        if not apps:
            print("No apps found. Please create some apps first.")
            return
        
        # Check if objects already exist
        existing_objects = db.query(SchemaObject).count()
        if existing_objects > 0:
            print(f"Database already has {existing_objects} objects. Skipping seed.")
            return
        
        # Sample objects for different apps
        sample_objects = [
            # Employee Management App (app_id: 1)
            {
                "name": "Employee",
                "fields": {
                    "name": {"type": "text", "required": True},
                    "email": {"type": "email", "required": True},
                    "department": {"type": "select", "required": True},
                    "position": {"type": "text", "required": True},
                    "salary": {"type": "number", "required": True},
                    "hire_date": {"type": "date", "required": True},
                    "status": {"type": "select", "required": True}
                },
                "app_id": 1
            },
            {
                "name": "Department",
                "fields": {
                    "name": {"type": "text", "required": True},
                    "manager": {"type": "text", "required": False},
                    "budget": {"type": "number", "required": False},
                    "location": {"type": "text", "required": False}
                },
                "app_id": 1
            },
            # Field Service App (app_id: 2)
            {
                "name": "WorkOrder",
                "fields": {
                    "title": {"type": "text", "required": True},
                    "description": {"type": "textarea", "required": True},
                    "priority": {"type": "select", "required": True},
                    "status": {"type": "select", "required": True},
                    "assigned_to": {"type": "text", "required": False},
                    "customer": {"type": "text", "required": True},
                    "due_date": {"type": "date", "required": True}
                },
                "app_id": 2
            },
            {
                "name": "Dispatcher",
                "fields": {
                    "name": {"type": "text", "required": True},
                    "email": {"type": "email", "required": True},
                    "phone": {"type": "text", "required": True},
                    "region": {"type": "text", "required": True},
                    "shift": {"type": "select", "required": True}
                },
                "app_id": 2
            },
            {
                "name": "Technician",
                "fields": {
                    "name": {"type": "text", "required": True},
                    "email": {"type": "email", "required": True},
                    "phone": {"type": "text", "required": True},
                    "skills": {"type": "textarea", "required": False},
                    "availability": {"type": "select", "required": True},
                    "rating": {"type": "number", "required": False}
                },
                "app_id": 2
            }
        ]
        
        # Add objects
        for object_data in sample_objects:
            object_obj = SchemaObject(**object_data)
            db.add(object_obj)
        
        db.commit()
        print(f"Successfully added {len(sample_objects)} sample objects")
        
        # Print the created objects
        objects = db.query(SchemaObject).all()
        print("\nCreated objects:")
        for obj in objects:
            app = db.query(SchemaApp).filter(SchemaApp.id == obj.app_id).first()
            app_name = app.name if app else "Unknown App"
            print(f"- {obj.name} (App: {app_name})")
            
    except Exception as e:
        print(f"Error seeding objects: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_objects() 
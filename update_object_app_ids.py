#!/usr/bin/env python3
"""
Script to update existing objects with app_id values
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SchemaObject, SchemaApp

def update_object_app_ids():
    """Update existing objects with app_id values"""
    db = SessionLocal()
    
    try:
        # Get all apps
        apps = db.query(SchemaApp).all()
        if not apps:
            print("No apps found. Please create some apps first.")
            return
        
        print(f"Found {len(apps)} apps:")
        for app in apps:
            print(f"- App {app.id}: {app.name}")
        
        # Get all objects without app_id
        objects = db.query(SchemaObject).filter(SchemaObject.app_id.is_(None)).all()
        print(f"\nFound {len(objects)} objects without app_id:")
        
        # Assign objects to apps based on their names
        object_assignments = {
            # Employee Management App (app_id: 1)
            "Employee": 1,
            "LeaveRequest": 1,
            "AttendanceRecord": 1,
            # Field Service App (app_id: 2)
            "WorkOrder": 2,
            "Dispatcher": 2,
            "Technician": 2,
            "Customer": 2,
        }
        
        updated_count = 0
        for obj in objects:
            if obj.name in object_assignments:
                obj.app_id = object_assignments[obj.name]
                updated_count += 1
                print(f"- Assigned {obj.name} to app {object_assignments[obj.name]}")
            else:
                print(f"- No assignment found for {obj.name}")
        
        if updated_count > 0:
            db.commit()
            print(f"\nSuccessfully updated {updated_count} objects with app_id values")
        else:
            print("\nNo objects were updated")
            
    except Exception as e:
        print(f"Error updating object app_ids: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_object_app_ids() 
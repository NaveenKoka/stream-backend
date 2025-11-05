#!/usr/bin/env python3
"""
Script to assign sample users to apps for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, AppUser, SchemaApp, UserRole

def assign_users_to_apps():
    """Assign sample users to apps"""
    db = SessionLocal()
    
    try:
        # Get all users and apps
        users = db.query(User).all()
        apps = db.query(SchemaApp).all()
        
        if not users:
            print("No users found. Please run seed_users.py first.")
            return
            
        if not apps:
            print("No apps found. Please create some apps first.")
            return
        
        # Assign users to apps with different roles
        assignments = [
            # User 1 (John Smith) - Admin on app 1, User on app 2
            {"user_id": 1, "app_id": 1, "role": "admin"},
            {"user_id": 1, "app_id": 2, "role": "user"},
            
            # User 2 (Sarah Johnson) - User on app 1, Viewer on app 3
            {"user_id": 2, "app_id": 1, "role": "user"},
            {"user_id": 2, "app_id": 3, "role": "viewer"},
            
            # User 3 (Michael Chen) - Admin on app 2, User on app 1
            {"user_id": 3, "app_id": 2, "role": "admin"},
            {"user_id": 3, "app_id": 1, "role": "user"},
            
            # User 4 (Emily Davis) - User on app 2, Viewer on app 1
            {"user_id": 4, "app_id": 2, "role": "user"},
            {"user_id": 4, "app_id": 1, "role": "viewer"},
            
            # User 5 (David Wilson) - Admin on app 3
            {"user_id": 5, "app_id": 3, "role": "admin"},
            
            # User 6 (Lisa Brown) - User on app 3
            {"user_id": 6, "app_id": 3, "role": "user"},
            
            # User 7 (Robert Taylor) - Viewer on app 2
            {"user_id": 7, "app_id": 2, "role": "viewer"},
            
            # User 8 (Jennifer Garcia) - User on app 1
            {"user_id": 8, "app_id": 1, "role": "user"},
        ]
        
        # Check existing assignments
        existing_assignments = db.query(AppUser).count()
        if existing_assignments > 0:
            print(f"Database already has {existing_assignments} user-app assignments. Skipping assignment.")
            return
        
        # Create assignments
        for assignment in assignments:
            app_user = AppUser(
                user_id=assignment["user_id"],
                app_id=assignment["app_id"],
                role=UserRole(assignment["role"])
            )
            db.add(app_user)
        
        db.commit()
        print(f"Successfully assigned users to apps")
        
        # Print the assignments
        print("\nUser-App Assignments:")
        app_users = db.query(AppUser).all()
        for app_user in app_users:
            user = db.query(User).filter(User.id == app_user.user_id).first()
            app = db.query(SchemaApp).filter(SchemaApp.id == app_user.app_id).first()
            if user and app:
                print(f"- {user.name} -> {app.name} ({app_user.role.value})")
            
    except Exception as e:
        print(f"Error assigning users to apps: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    assign_users_to_apps() 
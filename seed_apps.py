#!/usr/bin/env python3
"""
Script to seed the database with sample apps for testing.
Run this after setting up the database and installing dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, create_tables
from app.models import SchemaApp, AppStatus
from sqlalchemy.orm import Session

def seed_apps():
    """Add sample apps to the database"""
    # Create tables if they don't exist
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Sample apps data
        sample_apps = [
            {
                "name": "User Management",
                "description": "Admin panel for managing users and permissions",
                "status": AppStatus.ACTIVE,
                "app_metadata": {"category": "admin", "version": "1.0.0"}
            },
            {
                "name": "Inventory System", 
                "description": "Track products, stock levels, and orders",
                "status": AppStatus.ACTIVE,
                "app_metadata": {"category": "business", "version": "2.1.0"}
            },
            {
                "name": "Analytics Dashboard",
                "description": "Real-time analytics and reporting",
                "status": AppStatus.DRAFT,
                "app_metadata": {"category": "analytics", "version": "0.9.0"}
            },
            {
                "name": "Customer Support",
                "description": "Ticket management and customer communication",
                "status": AppStatus.ACTIVE,
                "app_metadata": {"category": "support", "version": "1.5.0"}
            }
        ]
        
        # Check if apps already exist
        existing_count = db.query(SchemaApp).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} apps. Skipping seed.")
            return
        
        # Add sample apps
        for app_data in sample_apps:
            app = SchemaApp(**app_data)
            db.add(app)
        
        db.commit()
        print(f"Successfully added {len(sample_apps)} sample apps to the database.")
        
        # Print the created apps
        apps = db.query(SchemaApp).all()
        print("\nCreated apps:")
        for app in apps:
            print(f"- {app.name} ({app.status.value})")
            
    except Exception as e:
        db.rollback()
        print(f"Error seeding apps: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding database with sample apps...")
    seed_apps()
    print("Done!") 
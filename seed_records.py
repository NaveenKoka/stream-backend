#!/usr/bin/env python3
"""
Seed script to add sample records for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SchemaRecord, SchemaObject

def seed_records():
    """Add sample records to the database"""
    db = SessionLocal()
    
    try:
        # Get existing objects
        objects = db.query(SchemaObject).all()
        
        if not objects:
            print("No objects found. Please create some objects first.")
            return
        
        # Check if records already exist
        existing_records = db.query(SchemaRecord).count()
        if existing_records > 0:
            print(f"Database already has {existing_records} records. Skipping seed.")
            return
        
        # Sample records for different objects
        sample_records = [
            # Employee records
            {
                "object_id": 1,  # Assuming Employee object
                "data": {
                    "name": "John Smith",
                    "email": "john.smith@company.com",
                    "department": "Engineering",
                    "position": "Senior Developer",
                    "salary": 85000,
                    "hire_date": "2023-01-15",
                    "status": "Active"
                }
            },
            {
                "object_id": 1,
                "data": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@company.com",
                    "department": "Marketing",
                    "position": "Marketing Manager",
                    "salary": 75000,
                    "hire_date": "2022-08-20",
                    "status": "Active"
                }
            },
            {
                "object_id": 1,
                "data": {
                    "name": "Michael Chen",
                    "email": "michael.chen@company.com",
                    "department": "Sales",
                    "position": "Sales Representative",
                    "salary": 65000,
                    "hire_date": "2023-03-10",
                    "status": "Active"
                }
            },
            # Customer records
            {
                "object_id": 2,  # Assuming Customer object
                "data": {
                    "name": "Acme Corporation",
                    "email": "contact@acme.com",
                    "phone": "+1-555-0123",
                    "address": "123 Business St, City, State 12345",
                    "industry": "Technology",
                    "status": "Active",
                    "created_date": "2023-01-10"
                }
            },
            {
                "object_id": 2,
                "data": {
                    "name": "Global Industries",
                    "email": "info@global.com",
                    "phone": "+1-555-0456",
                    "address": "456 Corporate Ave, City, State 67890",
                    "industry": "Manufacturing",
                    "status": "Active",
                    "created_date": "2023-02-15"
                }
            },
            # Product records
            {
                "object_id": 3,  # Assuming Product object
                "data": {
                    "name": "Premium Widget",
                    "sku": "PW-001",
                    "category": "Electronics",
                    "price": 299.99,
                    "stock": 150,
                    "description": "High-quality premium widget",
                    "status": "In Stock"
                }
            },
            {
                "object_id": 3,
                "data": {
                    "name": "Standard Widget",
                    "sku": "SW-002",
                    "category": "Electronics",
                    "price": 149.99,
                    "stock": 300,
                    "description": "Standard quality widget",
                    "status": "In Stock"
                }
            }
        ]
        
        # Add records
        for record_data in sample_records:
            record = SchemaRecord(**record_data)
            db.add(record)
        
        db.commit()
        print(f"Successfully added {len(sample_records)} sample records")
        
        # Print the created records
        records = db.query(SchemaRecord).all()
        print("\nCreated records:")
        for record in records:
            object_name = db.query(SchemaObject).filter(SchemaObject.id == record.object_id).first().name
            print(f"- {object_name}: {record.data.get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"Error seeding records: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_records() 
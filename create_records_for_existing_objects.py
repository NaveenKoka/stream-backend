#!/usr/bin/env python3
"""
Script to create records for existing objects
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SchemaRecord

def create_records_for_existing_objects():
    """Create records for existing objects"""
    db = SessionLocal()
    
    try:
        # Sample records for existing objects
        sample_records = [
            # Employee records (object_id: 18)
            {
                "object_id": 18,
                "data": {
                    "name": "John Smith",
                    "email": "john.smith@company.com",
                    "department": "Engineering",
                    "position": "Senior Developer",
                    "date_of_hire": "2023-01-15"
                }
            },
            {
                "object_id": 18,
                "data": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@company.com",
                    "department": "Marketing",
                    "position": "Marketing Manager",
                    "date_of_hire": "2022-08-20"
                }
            },
            {
                "object_id": 18,
                "data": {
                    "name": "Michael Chen",
                    "email": "michael.chen@company.com",
                    "department": "Sales",
                    "position": "Sales Representative",
                    "date_of_hire": "2023-03-10"
                }
            },
            # WorkOrder records (object_id: 1)
            {
                "object_id": 1,
                "data": {
                    "title": "AC Repair - Downtown Office",
                    "description": "Air conditioning unit not cooling properly",
                    "status": "In Progress",
                    "scheduled_date": "2024-01-15",
                    "technician": "Mike Johnson",
                    "customer": "Acme Corporation"
                }
            },
            {
                "object_id": 1,
                "data": {
                    "title": "Electrical Panel Upgrade",
                    "description": "Upgrade electrical panel to meet new safety standards",
                    "status": "New",
                    "scheduled_date": "2024-01-20",
                    "technician": "Sarah Wilson",
                    "customer": "Global Industries"
                }
            },
            # Dispatcher records (object_id: 2)
            {
                "object_id": 2,
                "data": {
                    "name": "Lisa Rodriguez",
                    "email": "lisa.rodriguez@fieldservice.com",
                    "phone": "+1-555-0123"
                }
            },
            {
                "object_id": 2,
                "data": {
                    "name": "David Thompson",
                    "email": "david.thompson@fieldservice.com",
                    "phone": "+1-555-0456"
                }
            },
            # Technician records (object_id: 3)
            {
                "object_id": 3,
                "data": {
                    "name": "Mike Johnson",
                    "email": "mike.johnson@fieldservice.com",
                    "phone": "+1-555-0789",
                    "skillset": ["HVAC", "Electrical", "Plumbing"]
                }
            },
            {
                "object_id": 3,
                "data": {
                    "name": "Sarah Wilson",
                    "email": "sarah.wilson@fieldservice.com",
                    "phone": "+1-555-0321",
                    "skillset": ["Electrical", "Security Systems"]
                }
            },
            # Customer records (object_id: 4)
            {
                "object_id": 4,
                "data": {
                    "name": "Acme Corporation",
                    "email": "contact@acme.com",
                    "phone": "+1-555-0123",
                    "address": "123 Business St, City, State 12345"
                }
            },
            {
                "object_id": 4,
                "data": {
                    "name": "Global Industries",
                    "email": "info@global.com",
                    "phone": "+1-555-0456",
                    "address": "456 Corporate Ave, City, State 67890"
                }
            }
        ]
        
        # Add records
        for record_data in sample_records:
            record = SchemaRecord(**record_data)
            db.add(record)
        
        db.commit()
        print(f"Successfully created {len(sample_records)} records")
        
        # Print summary
        print("\nCreated records:")
        records = db.query(SchemaRecord).all()
        for record in records:
            print(f"- Record {record.id} for object {record.object_id}")
            
    except Exception as e:
        print(f"Error creating records: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_records_for_existing_objects() 
#!/usr/bin/env python3
"""
Seed script to add sample users to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import User, AppUser, UserRole
from sqlalchemy import text

def seed_users():
    """Add sample users to the database"""
    db = SessionLocal()
    
    try:
        # Sample users data
        sample_users = [
            {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "password_hash": "hashed_password_123"  # In real app, this would be properly hashed
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com", 
                "password_hash": "hashed_password_456"
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@example.com",
                "password_hash": "hashed_password_789"
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@example.com",
                "password_hash": "hashed_password_101"
            },
            {
                "name": "David Wilson",
                "email": "david.wilson@example.com",
                "password_hash": "hashed_password_202"
            },
            {
                "name": "Lisa Brown",
                "email": "lisa.brown@example.com",
                "password_hash": "hashed_password_303"
            },
            {
                "name": "Robert Taylor",
                "email": "robert.taylor@example.com",
                "password_hash": "hashed_password_404"
            },
            {
                "name": "Jennifer Garcia",
                "email": "jennifer.garcia@example.com",
                "password_hash": "hashed_password_505"
            }
        ]
        
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping seed.")
            return
        
        # Add users
        for user_data in sample_users:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print(f"Successfully added {len(sample_users)} sample users")
        
        # Print the created users
        users = db.query(User).all()
        print("\nCreated users:")
        for user in users:
            print(f"- {user.name} ({user.email})")
            
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_users() 
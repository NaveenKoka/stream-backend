#!/usr/bin/env python3
"""
Migration script to add users and app_users tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, AppUser, UserRole
from sqlalchemy import text

def migrate_add_users():
    """Add users and app_users tables"""
    with engine.connect() as conn:
        try:
            # Check if users table already exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'users'
            """))
            
            if result.fetchone():
                print("Users table already exists")
            else:
                # Create users table
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        email VARCHAR NOT NULL UNIQUE,
                        password_hash VARCHAR NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("Successfully created users table")
            
            # Check if app_users table already exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'app_users'
            """))
            
            if result.fetchone():
                print("App_users table already exists")
            else:
                # Create app_users table
                conn.execute(text("""
                    CREATE TABLE app_users (
                        id SERIAL PRIMARY KEY,
                        app_id INTEGER NOT NULL REFERENCES apps(id),
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        role VARCHAR NOT NULL DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("Successfully created app_users table")
            
            conn.commit()
            print("Migration completed successfully")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_add_users() 
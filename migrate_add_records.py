#!/usr/bin/env python3
"""
Migration script to add records table and update objects table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import SchemaRecord
from sqlalchemy import text

def migrate_add_records():
    """Add records table and update objects table"""
    with engine.connect() as conn:
        try:
            # Check if records table already exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'records'
            """))
            
            if result.fetchone():
                print("Records table already exists")
            else:
                # Create records table
                conn.execute(text("""
                    CREATE TABLE records (
                        id SERIAL PRIMARY KEY,
                        object_id INTEGER NOT NULL REFERENCES objects(id),
                        data JSON NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("Successfully created records table")
            
            # Check if app_id column exists in objects table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'objects' AND column_name = 'app_id'
            """))
            
            if result.fetchone():
                print("App_id column already exists in objects table")
            else:
                # Add app_id column to objects table
                conn.execute(text("""
                    ALTER TABLE objects 
                    ADD COLUMN app_id INTEGER REFERENCES apps(id)
                """))
                print("Successfully added app_id column to objects table")
            
            conn.commit()
            print("Migration completed successfully")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_add_records() 
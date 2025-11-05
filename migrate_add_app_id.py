#!/usr/bin/env python3
"""
Migration script to add app_id column to workflows table.
Run this after updating the models but before using the new app_id functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def migrate_add_app_id():
    """Add app_id column to workflows table"""
    try:
        with engine.connect() as connection:
            # Check if app_id column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'workflows' AND column_name = 'app_id'
            """))
            
            if result.fetchone():
                print("app_id column already exists in workflows table.")
                return
            
            # Add app_id column
            connection.execute(text("""
                ALTER TABLE workflows 
                ADD COLUMN app_id INTEGER
            """))
            
            # Add index for better performance
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_workflows_app_id 
                ON workflows (app_id)
            """))
            
            connection.commit()
            print("Successfully added app_id column to workflows table.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    print("Running migration to add app_id column to workflows table...")
    migrate_add_app_id()
    print("Migration completed!") 
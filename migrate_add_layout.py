#!/usr/bin/env python3
"""
Migration script to add layout column to workflows table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from sqlalchemy import text

def migrate_add_layout():
    """Add layout column to workflows table"""
    with engine.connect() as conn:
        try:
            # Check if layout column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'workflows' AND column_name = 'layout'
            """))
            
            if result.fetchone():
                print("Layout column already exists in workflows table")
                return
            
            # Add layout column
            conn.execute(text("""
                ALTER TABLE workflows 
                ADD COLUMN layout JSON
            """))
            
            conn.commit()
            print("Successfully added layout column to workflows table")
            
        except Exception as e:
            print(f"Error adding layout column: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_add_layout() 
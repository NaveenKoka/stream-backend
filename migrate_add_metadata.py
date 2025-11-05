#!/usr/bin/env python3
"""
Migration script to add metadata table.
This creates the metadata table for storing configurable field types and other app metadata.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def migrate_add_metadata():
    """Add metadata table for storing configuration data"""
    try:
        with engine.connect() as connection:
            # Check if metadata table already exists
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'metadata'
            """))
            
            if result.fetchone():
                print("Metadata table already exists.")
                return
            
            # Create metadata table
            connection.execute(text("""
                CREATE TABLE metadata (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) NOT NULL UNIQUE,
                    value JSONB NOT NULL,
                    description TEXT,
                    app_id INTEGER REFERENCES apps(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Add indexes for better performance
            connection.execute(text("""
                CREATE INDEX idx_metadata_key ON metadata (key)
            """))
            
            connection.execute(text("""
                CREATE INDEX idx_metadata_app_id ON metadata (app_id)
            """))
            
            connection.execute(text("""
                CREATE INDEX idx_metadata_value_gin ON metadata USING GIN (value)
            """))
            
            connection.commit()
            print("Successfully created metadata table with indexes.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    print("Running migration to add metadata table...")
    migrate_add_metadata()
    print("Migration completed!")


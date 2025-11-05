#!/usr/bin/env python3
"""
Script to drop and recreate all database tables.
WARNING: This will delete all existing data!
Use only for development/testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, Base
from app.models import SchemaObject, SchemaWorkflow, SchemaApp

def recreate_tables():
    """Drop and recreate all tables"""
    try:
        with engine.connect() as connection:
            # Drop all tables
            connection.execute(text("DROP TABLE IF EXISTS workflows CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS objects CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS apps CASCADE"))
            connection.commit()
            print("Dropped existing tables.")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        print("Recreated all tables with latest schema.")
        
    except Exception as e:
        print(f"Error recreating tables: {e}")
        raise

if __name__ == "__main__":
    print("WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (y/N): ")
    
    if response.lower() == 'y':
        print("Recreating all database tables...")
        recreate_tables()
        print("Done!")
    else:
        print("Operation cancelled.") 
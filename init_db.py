#!/usr/bin/env python3
"""
Database initialization script for Payroll App
Run this script to create the database tables.
"""

import os
from app import app, db

def main():
    """Initialize the database"""
    print("Initializing Payroll App database...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Get database path for confirmation
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            db_path = db_uri.replace('sqlite:///', '')
            
            print(f"✓ Database initialized successfully!")
            print(f"✓ Database location: {db_path}")
            print(f"✓ Tables created: User, TimeEntry")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ Tables in database: {', '.join(tables)}")
            
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    print("\n🎉 Database setup complete! You can now run the app with: python3 app.py")
    return True

if __name__ == '__main__':
    main()
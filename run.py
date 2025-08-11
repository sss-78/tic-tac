#!/usr/bin/env python3
"""
Payroll App runner script
Automatically initializes database if needed and starts the Flask app.
"""

import os
import sys
from app import app, db, db_path

def check_database():
    """Check if database exists and has tables"""
    if not os.path.exists(db_path):
        return False
    
    try:
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            return 'user' in tables and 'time_entry' in tables
    except:
        return False

def init_database():
    """Initialize the database"""
    print("Database not found or incomplete. Initializing...")
    try:
        with app.app_context():
            db.create_all()
            print(f"✓ Database created at: {db_path}")
            return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def main():
    """Main runner function"""
    print("🚀 Starting Payroll App...")
    
    # Check and initialize database if needed
    if not check_database():
        if not init_database():
            print("Failed to initialize database. Exiting.")
            sys.exit(1)
    else:
        print(f"✓ Database ready at: {db_path}")
    
    # Set environment for development
    os.environ.setdefault('FLASK_ENV', 'development')
    
    print("✓ Starting Flask server...")
    print("✓ App will be available at: http://localhost:5000")
    print("✓ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the app
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Payroll App. Goodbye!")
    except Exception as e:
        print(f"\n✗ Error running app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
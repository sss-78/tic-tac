#!/usr/bin/env python3
"""
Create a demo user for testing the Payroll App
"""

from app import app, db, User

def create_demo_user():
    """Create a demo user for testing"""
    with app.app_context():
        # Check if demo user already exists
        existing_user = User.query.filter_by(email='demo@example.com').first()
        if existing_user:
            print("Demo user already exists!")
            print(f"Email: {existing_user.email}")
            print(f"Pay Type: {existing_user.pay_type}")
            if existing_user.pay_type == 'hourly':
                print(f"Hourly Rate: ${existing_user.hourly_rate:.2f}")
            else:
                print(f"Annual Salary: ${existing_user.annual_salary:,.2f}")
            return
        
        # Create demo user
        demo_user = User(
            email='demo@example.com',
            pay_type='hourly',
            hourly_rate=25.00
        )
        demo_user.set_password('password123')
        
        try:
            db.session.add(demo_user)
            db.session.commit()
            
            print("✅ Demo user created successfully!")
            print("Email: demo@example.com")
            print("Password: password123")
            print("Pay Type: Hourly")
            print("Hourly Rate: $25.00")
            print("\nYou can now login with these credentials at http://localhost:5000/login")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating demo user: {e}")

if __name__ == '__main__':
    create_demo_user()
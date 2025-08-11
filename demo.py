#!/usr/bin/env python3
"""
Payroll App Demo Script
Demonstrates the complete functionality of the payroll application.
"""

import os
import sys
from datetime import date, timedelta
from app import app, db, User, TimeEntry

def create_demo_data():
    """Create demo users and time entries"""
    with app.app_context():
        print("🎯 Creating demo data...")
        
        # Create demo users if they don't exist
        users_data = [
            {
                'email': 'hourly@example.com',
                'password': 'password123',
                'pay_type': 'hourly',
                'hourly_rate': 25.00,
                'annual_salary': None
            },
            {
                'email': 'salary@example.com', 
                'password': 'password123',
                'pay_type': 'salary',
                'hourly_rate': None,
                'annual_salary': 65000.00
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                user = User(
                    email=user_data['email'],
                    pay_type=user_data['pay_type'],
                    hourly_rate=user_data['hourly_rate'],
                    annual_salary=user_data['annual_salary']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_users.append(user_data['email'])
        
        if created_users:
            db.session.commit()
            print(f"✓ Created users: {', '.join(created_users)}")
        else:
            print("✓ Demo users already exist")
        
        # Create sample time entries for current week
        today = date.today()
        iso_year, iso_week, _ = today.isocalendar()
        
        # Get Monday of current week
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        # Sample hours for the week (Monday to Friday)
        sample_hours = [8.0, 7.5, 8.0, 8.5, 6.0, 0.0, 0.0]  # Mon-Sun
        
        for user_data in users_data:
            user = User.query.filter_by(email=user_data['email']).first()
            if user:
                # Clear existing entries for this week
                TimeEntry.query.filter_by(
                    user_id=user.id,
                    iso_year=iso_year,
                    iso_week=iso_week
                ).delete()
                
                # Add sample entries
                for i, hours in enumerate(sample_hours):
                    if hours > 0:
                        entry_date = monday + timedelta(days=i)
                        entry = TimeEntry(
                            user_id=user.id,
                            iso_year=iso_year,
                            iso_week=iso_week,
                            date=entry_date,
                            hours=hours
                        )
                        db.session.add(entry)
        
        db.session.commit()
        print(f"✓ Created sample time entries for week {iso_week}, {iso_year}")

def show_demo_info():
    """Show demo user information and instructions"""
    with app.app_context():
        print("\n" + "="*60)
        print("🎉 PAYROLL APP DEMO READY!")
        print("="*60)
        
        users = User.query.all()
        print(f"\n👥 Demo Users ({len(users)} total):")
        
        for user in users:
            print(f"\n📧 Email: {user.email}")
            print(f"🔑 Password: password123")
            print(f"💰 Pay Type: {user.pay_type.title()}")
            if user.pay_type == 'hourly':
                print(f"💵 Hourly Rate: ${user.hourly_rate:.2f}/hour")
            else:
                print(f"💵 Annual Salary: ${user.annual_salary:,.2f}/year")
            
            # Show current week hours
            today = date.today()
            iso_year, iso_week, _ = today.isocalendar()
            
            entries = TimeEntry.query.filter_by(
                user_id=user.id,
                iso_year=iso_year,
                iso_week=iso_week
            ).all()
            
            total_hours = sum(entry.hours for entry in entries)
            print(f"⏰ Hours this week: {total_hours:.2f}")
            
            if user.pay_type == 'hourly':
                weekly_pay = total_hours * user.hourly_rate
                print(f"💸 Weekly pay: ${weekly_pay:.2f}")
            else:
                weekly_pay = user.annual_salary / 52
                print(f"💸 Weekly pay: ${weekly_pay:.2f}")
        
        print(f"\n🌐 Application URLs:")
        print(f"   Home: http://localhost:5000/")
        print(f"   Login: http://localhost:5000/login")
        print(f"   Register: http://localhost:5000/register")
        print(f"   Dashboard: http://localhost:5000/dashboard")
        print(f"   Timesheet: http://localhost:5000/timesheet")
        
        print(f"\n📊 Current Week: {iso_week}, {iso_year}")
        print(f"📅 Database: {len(User.query.all())} users, {len(TimeEntry.query.all())} time entries")
        
        print("\n🚀 Ready to test! Login with any demo user above.")
        print("="*60)

def main():
    """Main demo setup function"""
    if not os.path.exists('instance/payroll.db'):
        print("Database not found. Please run the app first to initialize it.")
        print("Run: python3 app.py")
        sys.exit(1)
    
    try:
        create_demo_data()
        show_demo_info()
    except Exception as e:
        print(f"✗ Error setting up demo: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
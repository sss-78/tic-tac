import os
import secrets
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from functools import wraps
import re

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Ensure instance directory exists and use absolute path
instance_dir = os.path.join(os.getcwd(), 'instance')
os.makedirs(instance_dir, exist_ok=True)
db_path = os.path.join(instance_dir, 'payroll.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    pay_type = db.Column(db.String(10), nullable=False)  # 'hourly' or 'salary'
    hourly_rate = db.Column(db.Float, nullable=True)
    annual_salary = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password using bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    iso_year = db.Column(db.Integer, nullable=False)
    iso_week = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
        db.CheckConstraint('hours >= 0 AND hours <= 24', name='valid_hours'),
    )

# Security decorators and functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token():
    token = session.get('csrf_token')
    if not token or token != request.form.get('csrf_token'):
        return False
    return True

# Template context processor
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token())

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Utility functions
def get_current_iso_week():
    """Get current ISO year and week"""
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    return iso_year, iso_week

def get_week_dates(iso_year, iso_week):
    """Get the dates for a given ISO week (Monday to Sunday)"""
    # Find the first day of the ISO year
    jan_4 = date(iso_year, 1, 4)
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    
    # Calculate the Monday of the target week
    target_monday = week_1_monday + timedelta(weeks=iso_week - 1)
    
    # Generate all 7 days
    dates = []
    for i in range(7):
        dates.append(target_monday + timedelta(days=i))
    
    return dates

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_hours(hours_str):
    """Validate hours input"""
    try:
        hours = float(hours_str)
        return 0 <= hours <= 24
    except (ValueError, TypeError):
        return False

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('register'))
        
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        pay_type = request.form.get('pay_type', '')
        
        # Validation
        if not email or not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if pay_type not in ['hourly', 'salary']:
            flash('Please select a valid pay type.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Get pay rate/salary
        hourly_rate = None
        annual_salary = None
        
        if pay_type == 'hourly':
            try:
                hourly_rate = float(request.form.get('hourly_rate', 0))
                if hourly_rate <= 0:
                    flash('Please enter a valid hourly rate.', 'error')
                    return render_template('register.html')
            except (ValueError, TypeError):
                flash('Please enter a valid hourly rate.', 'error')
                return render_template('register.html')
        else:  # salary
            try:
                annual_salary = float(request.form.get('annual_salary', 0))
                if annual_salary <= 0:
                    flash('Please enter a valid annual salary.', 'error')
                    return render_template('register.html')
            except (ValueError, TypeError):
                flash('Please enter a valid annual salary.', 'error')
                return render_template('register.html')
        
        # Create user
        user = User(
            email=email,
            pay_type=pay_type,
            hourly_rate=hourly_rate,
            annual_salary=annual_salary
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('login'))
        
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    if not validate_csrf_token():
        flash('Invalid CSRF token.', 'error')
        return redirect(url_for('dashboard'))
    
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/timesheet', methods=['GET', 'POST'])
@login_required
def timesheet():
    # Get week parameters
    iso_year = request.args.get('iso_year', type=int)
    iso_week = request.args.get('iso_week', type=int)
    
    # Default to current week if not provided
    if not iso_year or not iso_week:
        iso_year, iso_week = get_current_iso_week()
    
    # Validate week parameters
    if not (1 <= iso_week <= 53) or not (2000 <= iso_year <= 2100):
        flash('Invalid week specified.', 'error')
        iso_year, iso_week = get_current_iso_week()
    
    # Get dates for the week
    week_dates = get_week_dates(iso_year, iso_week)
    
    # Get existing time entries for this week
    user_id = session['user_id']
    entries = {}
    time_entries = TimeEntry.query.filter_by(
        user_id=user_id,
        iso_year=iso_year,
        iso_week=iso_week
    ).all()
    
    for entry in time_entries:
        entries[entry.date] = entry.hours
    
    # Create timesheet data
    timesheet_data = []
    for i, date_obj in enumerate(week_dates):
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
        timesheet_data.append({
            'date': date_obj,
            'day_name': day_name,
            'hours': entries.get(date_obj, 0.0)
        })
    
    if request.method == 'POST':
        if not validate_csrf_token():
            flash('Invalid CSRF token. Please try again.', 'error')
            return redirect(url_for('timesheet', iso_year=iso_year, iso_week=iso_week))
        
        # Process form data
        errors = []
        entries_to_save = []
        
        for i, date_obj in enumerate(week_dates):
            hours_input = request.form.get(f'hours_{i}', '').strip()
            if hours_input:
                if not validate_hours(hours_input):
                    errors.append(f'Invalid hours for {date_obj.strftime("%A, %B %d")}: must be between 0 and 24')
                    continue
                
                hours = float(hours_input)
                if hours > 0:  # Only save non-zero entries
                    entries_to_save.append({
                        'date': date_obj,
                        'hours': hours
                    })
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('timesheet.html', 
                                 timesheet_data=timesheet_data,
                                 iso_year=iso_year,
                                 iso_week=iso_week)
        
        try:
            # Delete existing entries for this week
            TimeEntry.query.filter_by(
                user_id=user_id,
                iso_year=iso_year,
                iso_week=iso_week
            ).delete()
            
            # Add new entries
            for entry_data in entries_to_save:
                entry = TimeEntry(
                    user_id=user_id,
                    iso_year=iso_year,
                    iso_week=iso_week,
                    date=entry_data['date'],
                    hours=entry_data['hours']
                )
                db.session.add(entry)
            
            db.session.commit()
            flash('Timesheet saved successfully!', 'success')
            return redirect(url_for('timesheet', iso_year=iso_year, iso_week=iso_week))
            
        except Exception as e:
            db.session.rollback()
            flash('Error saving timesheet. Please try again.', 'error')
    
    return render_template('timesheet.html', 
                         timesheet_data=timesheet_data,
                         iso_year=iso_year,
                         iso_week=iso_week)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get week parameters
    iso_year = request.args.get('iso_year', type=int)
    iso_week = request.args.get('iso_week', type=int)
    
    # Default to current week if not provided
    if not iso_year or not iso_week:
        iso_year, iso_week = get_current_iso_week()
    
    # Validate week parameters
    if not (1 <= iso_week <= 53) or not (2000 <= iso_year <= 2100):
        flash('Invalid week specified.', 'error')
        iso_year, iso_week = get_current_iso_week()
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get dates for the week
    week_dates = get_week_dates(iso_year, iso_week)
    
    # Get time entries for this week
    time_entries = TimeEntry.query.filter_by(
        user_id=user_id,
        iso_year=iso_year,
        iso_week=iso_week
    ).all()
    
    # Create daily summary
    entries_dict = {entry.date: entry.hours for entry in time_entries}
    daily_summary = []
    total_hours = 0
    
    for i, date_obj in enumerate(week_dates):
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
        hours = entries_dict.get(date_obj, 0.0)
        total_hours += hours
        daily_summary.append({
            'date': date_obj,
            'day_name': day_name,
            'hours': hours
        })
    
    # Calculate pay
    if user.pay_type == 'hourly':
        total_pay = total_hours * user.hourly_rate
        pay_description = f"${user.hourly_rate:.2f}/hour × {total_hours} hours"
    else:  # salary
        weekly_salary = user.annual_salary / 52
        total_pay = weekly_salary
        pay_description = f"Weekly salary (${user.annual_salary:,.2f}/year ÷ 52 weeks)"
    
    return render_template('dashboard.html',
                         user=user,
                         daily_summary=daily_summary,
                         total_hours=total_hours,
                         total_pay=total_pay,
                         pay_description=pay_description,
                         iso_year=iso_year,
                         iso_week=iso_week,
                         week_start=week_dates[0],
                         week_end=week_dates[6])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html',
                         error_title='Internal Server Error',
                         error_message='An unexpected error occurred. Please try again later.'), 500

# Database initialization
def init_db():
    """Initialize the database"""
    try:
        with app.app_context():
            db.create_all()
            print(f"Database initialized at: {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
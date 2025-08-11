# Payroll Web App

A minimal, secure payroll web application for tracking daily hours and calculating weekly pay. Built with Flask, SQLite, and vanilla HTML/CSS/JS.

## Features

- **Secure Authentication**: User registration/login with bcrypt password hashing
- **Time Tracking**: Weekly timesheet with daily hours input (Monday-Sunday)
- **Pay Calculations**: Support for both hourly and salaried employees
- **Dashboard**: Weekly summary showing total hours and computed pay
- **Security**: CSRF protection, secure sessions, input validation, and security headers
- **Responsive Design**: Clean, mobile-friendly interface

## Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite
- **Frontend**: Vanilla HTML, CSS, JavaScript (no frameworks)
- **Security**: bcrypt for password hashing, CSRF tokens, secure sessions

## Quick Start

### Prerequisites

- Python 3.8+ 
- pip (Python package manager)

### Installation

1. **Clone or download the project files**
   ```bash
   cd /path/to/payroll-app
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Linux/Mac:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables (recommended)**
   ```bash
   # Create a .env file or export directly
   export SECRET_KEY="your-secret-key-here"
   
   # Or create .env file:
   echo "SECRET_KEY=your-secret-key-here" > .env
   ```

5. **Run the application**
   ```bash
   # Option 1: Use the runner script (recommended)
   python3 run.py
   
   # Option 2: Run directly
   python3 app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

### Database Initialization

The database is automatically created when you first run the app. The SQLite file will be located at `instance/payroll.db`.

## Usage Guide

### 1. User Registration

- Navigate to `/register`
- Provide email, password (min 8 characters), and pay information
- Choose between:
  - **Hourly**: Enter your hourly rate
  - **Salary**: Enter your annual salary

### 2. Time Entry

- Go to `/timesheet` or click "Timesheet" in navigation
- Select the desired week using Previous/Next Week buttons
- Enter hours for each day (Monday-Sunday)
- Supports decimal hours (e.g., 8.5 for 8 hours 30 minutes)
- Hours are automatically rounded to nearest 0.25 (15 minutes)
- Click "Save Timesheet" to persist your entries

### 3. Dashboard

- View `/dashboard` or click "Dashboard" in navigation  
- See weekly summary including:
  - Total hours worked
  - Computed pay based on your pay type
  - Daily breakdown with individual day hours
  - Pay calculation details

### 4. Week Navigation

Both timesheet and dashboard support week navigation:
- Use Previous/Next Week buttons
- URL parameters: `?iso_year=2024&iso_week=15`
- Defaults to current ISO week

## Pay Calculations

### Hourly Employees
- **Weekly Pay** = Total Hours × Hourly Rate
- Example: 40 hours × $25/hour = $1,000

### Salaried Employees  
- **Weekly Pay** = Annual Salary ÷ 52 weeks
- Example: $60,000/year ÷ 52 = $1,153.85/week
- Hours tracking is still maintained for record keeping

## Security Features

- **Password Security**: bcrypt hashing with salt
- **Session Security**: HttpOnly, SameSite cookies
- **CSRF Protection**: All POST forms include CSRF tokens
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- **Error Handling**: Friendly error pages without stack trace exposure

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| POST | `/logout` | User logout |
| GET/POST | `/timesheet` | Weekly timesheet entry |
| GET | `/dashboard` | Weekly summary dashboard |
| GET | `/` | Home page |

## Database Schema

### User Table
```sql
- id (Primary Key)
- email (Unique, Not Null)
- password_hash (Not Null) 
- pay_type ('hourly' or 'salary')
- hourly_rate (Float, nullable)
- annual_salary (Float, nullable)
- created_at (DateTime)
```

### TimeEntry Table
```sql
- id (Primary Key)
- user_id (Foreign Key to User)
- iso_year (Integer, Not Null)
- iso_week (Integer, Not Null)  
- date (Date, Not Null)
- hours (Float, 0-24 constraint)
- created_at (DateTime)
- UNIQUE(user_id, date)
```

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for sessions (auto-generated if not set)
- `FLASK_ENV`: Set to 'development' for debug mode

### Database Location

- SQLite file: `instance/payroll.db`
- Automatically created on first run

## Development

### File Structure
```
payroll-app/
├── app.py                 # Main Flask application
├── run.py                 # App runner with auto-init
├── init_db.py            # Database initialization script
├── create_demo_user.py   # Demo user creation script
├── demo.py               # Full demo setup with sample data
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── instance/             # Database directory (auto-created)
│   └── payroll.db        # SQLite database
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── register.html     # Registration form
│   ├── login.html        # Login form
│   ├── timesheet.html    # Timesheet entry
│   ├── dashboard.html    # Dashboard/summary
│   └── error.html        # Error pages
└── static/               # Static assets
    ├── css/
    │   └── style.css     # Main stylesheet
    └── js/
        └── app.js        # Client-side JavaScript
```

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

This enables:
- Debug mode with auto-reload
- Detailed error pages
- Debug toolbar (if installed)

## Demo User Creation

### Option 1: Use the Demo Script (Recommended)
```bash
python3 create_demo_user.py
```

This creates a demo user with:
- **Email**: demo@example.com
- **Password**: password123  
- **Pay Type**: Hourly
- **Rate**: $25.00/hour

### Option 2: Full Demo Setup
```bash
python3 demo.py
```

This creates multiple demo users with sample time entries:
- **hourly@example.com** - Hourly employee ($25/hour)
- **salary@example.com** - Salaried employee ($65,000/year)

### Option 3: Manual Registration

1. Go to `http://localhost:5000/register`
2. Enter email: `demo@example.com`
3. Password: `password123`
4. Pay Type: `hourly`
5. Hourly Rate: `25.00`
6. Click "Create Account"
7. Login with the same credentials

## Troubleshooting

### Common Issues

**Database Permission Error**
- Ensure the `instance/` directory is writable
- Check file permissions on `instance/payroll.db`

**Import Errors**
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again

**Session/CSRF Errors**
- Clear browser cookies for localhost:5000
- Restart the Flask application

**Week Navigation Issues**
- ISO weeks run Monday-Sunday
- Week 1 contains January 4th
- Some years have 53 weeks

### Logs and Debugging

- Flask debug mode shows detailed error pages
- Check terminal output for server logs
- Database queries are logged in debug mode

## Security Considerations

### Production Deployment

For production use, ensure:

1. **Set a strong SECRET_KEY**
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Use HTTPS**
   - Enables secure session cookies
   - Activates HSTS headers

3. **Database Security**
   - Move SQLite file outside web root
   - Consider PostgreSQL for multi-user scenarios
   - Regular backups

4. **Server Configuration**
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Configure reverse proxy (Nginx, Apache)
   - Set appropriate file permissions

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check this README for common solutions
2. Review the code comments for implementation details
3. Test with a fresh database by deleting `instance/payroll.db`

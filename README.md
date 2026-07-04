# MakElize

MakElize is a web-based maintenance management system designed to support emergency maintenance workflows across three user roles:

- Admin
- Maintenance Manager
- Accountable Party

The system allows administrators to register employees, managers to review emergency maintenance requests and assign assets, and accountable parties to manage assigned assets, submit received/completion forms, and track work progress.

## Features

- User authentication and role-based access
- Employee registration and account creation
- Emergency maintenance request tracking
- Asset assignment to accountable parties
- Work received and work completion form submissions
- Dashboard views for admin, manager, and accountable users

## Tech Stack

- Backend: Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQL Server via pyodbc
- Authentication: Flask sessions

## Project Structure

```text
backend/        # Flask API and route handlers
frontend/       # Static HTML/CSS/JS dashboards
database/       # SQL scripts and Python dependencies
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.9+
- SQL Server installed and running
- ODBC Driver 17 for SQL Server
- A configured database named `MakElize`

## Installation

1. Clone the repository
2. Go to the project folder
3. Install Python dependencies:

```bash
pip install -r database/requirements.txt
```

## Configuration

Update the database and email settings in [backend/config.py](backend/config.py) before starting the app.

Key settings to configure:

- `DB_CONFIG`: SQL Server server name, database name, and authentication details
- `EMAIL_CONFIG`: SMTP credentials for sending employee registration emails
- `SECRET_KEY`: a secure random secret key

## Running the Application

### Start the backend

```bash
cd backend
python app.py
```

This will start the Flask server on port `####`.

### Open the frontend

Open the HTML files in the [frontend](frontend) folder directly in your browser, or serve the folder using a local static server.

## Database Setup

A SQL setup script is available at [database/MakElize_setup.sql](database/MakElize_setup.sql). The file is currently empty, so you will need to create the required tables and seed data in your SQL Server database before using the system.

## Notes

- The backend uses Flask sessions for authentication.
- The default login flow expects valid employee records in the database.
- Email delivery depends on your SMTP configuration.

## License

This project is provided as-is for development purposes and skill improvement.

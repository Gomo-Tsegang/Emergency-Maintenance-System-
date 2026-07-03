# ============================================================
# config.py
# Database and email configuration settings
# ============================================================

# SQL Server connection settings
# Change SERVER to your actual SSMS server name or instance.
# Use Windows Authentication by setting TRUSTED_CONNECTION to "yes"
# and leaving USERNAME/PASSWORD empty.
DB_CONFIG = {
    "SERVER": "GOMOTSEGANG\SQLEXPRESS",
    "DATABASE": "MakElize",
    "USERNAME": "",
    "PASSWORD": "",
    "DRIVER": "ODBC Driver 17 for SQL Server",
    "TRUSTED_CONNECTION": "yes"
}

# Email settings
# Use your Gmail address and an App Password (not your normal password)
# To get an App Password: Google Account > Security > App Passwords
EMAIL_CONFIG = {
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "SENDER_EMAIL": "youremail@gmail.com",
    "SENDER_PASSWORD": "your_app_password_here",
    "SENDER_NAME": "MakElize System"
}

# Flask secret key - change this to something random and private
SECRET_KEY = "makelizesecretkey2024"
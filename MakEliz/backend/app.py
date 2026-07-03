# ============================================================
# app.py
# Main entry point for the MakElize backend server
# Run this file to start the backend: python app.py
# ============================================================

import os
import sys

from flask import Flask, redirect
from flask_cors import CORS
from config import SECRET_KEY

from routes.auth_routes import auth_bp
from routes.admin import admin_bp
from routes.manager import manager_bp
from routes.accountable import accountable_bp
from test_db_connection import test_connection
from database import ensure_employee_role_column

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app = Flask(__name__, static_folder=frontend_path, static_url_path="")
app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/api/*": {
            "origins": [
                "http://127.0.0.1:8000",
                "http://localhost:8000",
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "null"
            ]
        }
    }
)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(manager_bp, url_prefix="/api/manager")
app.register_blueprint(accountable_bp, url_prefix="/api/accountable")


@app.route("/")
def root():
    return redirect("/login.html")


def print_startup_help():
    print("MakElize backend server is starting...")
    print("Open your frontend HTML files in a browser to use the system.")
    print("To test the database connection without starting the server, run: python app.py test-db")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test-db":
        test_connection()
    else:
        ensure_employee_role_column()
        print_startup_help()
        app.run(debug=True, port=5000)
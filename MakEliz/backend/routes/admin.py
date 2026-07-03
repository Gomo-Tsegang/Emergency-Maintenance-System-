
from flask import Blueprint, request, jsonify, session
import sys
import os
import random
import string

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from email_service import send_credentials_email

admin_bp = Blueprint("admin", __name__)


def generate_password(length=10):
    characters = string.ascii_letters + string.digits + "!@#$"
    return "".join(random.choices(characters, k=length))


def require_admin():
    if "employee_id" not in session or not session.get("is_admin"):
        return False
    return True


@admin_bp.route("/register", methods=["POST"])
def register_employee():
    if not require_admin():
        return jsonify({"success": False, "message": "Admin access required."}), 403

    data = request.get_json()
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    role = data.get("role", "").strip()
    username = data.get("username", "").strip()

    if not all([first_name, last_name, email, role, username]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if role not in ["Maintenance Manager", "Accountable Party"]:
        return jsonify({"success": False, "message": "Role must be Maintenance Manager or Accountable Party."}), 400

    is_admin = 1 if role == "Maintenance Manager" else 0
    generated_password = generate_password()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ID FROM Employees WHERE Username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Username already exists."}), 409

        cursor.execute("SELECT ID FROM Employees WHERE Email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Email already exists."}), 409

        cursor.execute(
            """
            INSERT INTO Employees (FirstName, LastName, Phone, isAdmin, Username, Password, Email, Role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (first_name, last_name, phone, is_admin, username, generated_password, email, role)
        )
        conn.commit()
        conn.close()

        full_name = first_name + " " + last_name
        email_sent, email_error = send_credentials_email(email, full_name, username, generated_password, role)

        message = "Employee registered successfully."
        if email_sent:
            message += " Email sent."
        else:
            message += " Email delivery failed: " + email_error

        return jsonify({
            "success": True,
            "message": message,
            "username": username
        })

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


@admin_bp.route("/employees", methods=["GET"])
def get_all_employees():
    if not require_admin():
        return jsonify({"success": False, "message": "Admin access required."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, FirstName, LastName, Phone, Email, Username, Role, isAdmin FROM Employees ORDER BY ID"
        )
        rows = cursor.fetchall()
        conn.close()

        employees = []
        for row in rows:
            employees.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "phone": row[3],
                "email": row[4],
                "username": row[5],
                "role": row[6],
                "is_admin": bool(row[7])
            })

        return jsonify({"success": True, "employees": employees})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


@admin_bp.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    if not require_admin():
        return jsonify({"success": False, "message": "Admin access required."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Employees WHERE ID = ?", (employee_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Employee removed."})
    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500
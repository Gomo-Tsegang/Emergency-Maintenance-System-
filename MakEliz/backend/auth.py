# ============================================================
# auth_routes.py
# Handles login and logout
# ============================================================

from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, FirstName, LastName, isAdmin, Role, Username FROM Employees WHERE Username = ? AND Password = ?",
            (username, password)
        )
        employee = cursor.fetchone()
        conn.close()

        if employee:
            session["employee_id"] = employee[0]
            session["name"] = employee[1] + " " + employee[2]
            session["is_admin"] = bool(employee[3])
            session["role"] = employee[4]
            session["username"] = employee[5]

            return jsonify({
                "success": True,
                "role": employee[4],
                "name": employee[1] + " " + employee[2],
                "is_admin": bool(employee[3])
            })
        else:
            return jsonify({"success": False, "message": "Invalid username or password."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@auth_bp.route("/session", methods=["GET"])
def get_session():
    if "employee_id" in session:
        return jsonify({
            "logged_in": True,
            "role": session.get("role"),
            "name": session.get("name"),
            "is_admin": session.get("is_admin")
        })
    return jsonify({"logged_in": False})
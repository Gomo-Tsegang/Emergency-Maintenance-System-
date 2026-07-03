# ============================================================
# manager.py
# Maintenance Manager routes
# - View EM requests sorted by priority
# - View all Accountable Parties
# - Assign assets to Accountable Parties
# - View work received forms
# - View work completion forms submitted by Accountable Parties
# ============================================================

from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

manager_bp = Blueprint("manager", __name__)


def require_manager():
    if "employee_id" not in session:
        return False
    if session.get("role") not in ["Maintenance Manager", "Admin"]:
        return False
    return True


# ============================================================
# GET: All open EM requests sorted by priority
# ============================================================

@manager_bp.route("/em-requests", methods=["GET"])
def get_em_requests():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.AssetSN,
                a.AssetName,
                em.EMReportDate,
                e.FirstName + ' ' + e.LastName AS EmployeeFullName,
                d.Name AS Department,
                p.Name AS Priority,
                em.ID AS EmergencyID
            FROM EmergencyMaintenances em
            JOIN Assets a ON em.AssetID = a.ID
            JOIN Employees e ON a.EmployeeID = e.ID
            JOIN DepartmentLocations dl ON a.DepartmentLocationID = dl.ID
            JOIN Departments d ON dl.DepartmentID = d.ID
            JOIN Priorities p ON em.PriorityID = p.ID
            WHERE em.EMEndDate IS NULL
            ORDER BY
                CASE p.Name
                    WHEN 'Very High' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Normal' THEN 3
                    ELSE 4
                END
            """
        )
        rows = cursor.fetchall()
        conn.close()

        requests = []
        for row in rows:
            requests.append({
                "asset_sn": row[0],
                "asset_name": row[1],
                "request_date": str(row[2]) if row[2] else "",
                "employee_full_name": row[3],
                "department": row[4],
                "priority": row[5],
                "emergency_id": row[6]
            })

        return jsonify({"success": True, "requests": requests})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# GET: All assets in the system (for the assign form dropdown)
# ============================================================

@manager_bp.route("/all-assets", methods=["GET"])
def get_all_assets():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.ID,
                a.AssetSN,
                a.AssetName,
                d.Name AS Department
            FROM Assets a
            LEFT JOIN DepartmentLocations dl ON a.DepartmentLocationID = dl.ID
            LEFT JOIN Departments d ON dl.DepartmentID = d.ID
            ORDER BY a.AssetName
            """
        )
        rows = cursor.fetchall()
        conn.close()

        assets = []
        for row in rows:
            assets.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "department": row[3] or ""
            })

        return jsonify({"success": True, "assets": assets})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# GET: All registered Accountable Parties
# ============================================================

@manager_bp.route("/accountable-parties", methods=["GET"])
def get_accountable_parties():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ID, FirstName, LastName, Email, Phone
            FROM Employees
            WHERE Role = 'Accountable Party'
            ORDER BY FirstName
            """
        )
        rows = cursor.fetchall()
        conn.close()

        parties = []
        for row in rows:
            parties.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4] or ""
            })

        return jsonify({"success": True, "parties": parties})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# POST: Assign an asset to an Accountable Party
# ============================================================

@manager_bp.route("/assign-asset", methods=["POST"])
def assign_asset():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    data = request.get_json()
    asset_id = data.get("asset_id")
    assigned_to = data.get("assigned_to_employee_id")
    assigned_date = data.get("assigned_date")
    notes = data.get("notes", "")

    if not asset_id or not assigned_to or not assigned_date:
        return jsonify({"success": False, "message": "Asset, employee, and date are required."}), 400

    manager_id = session.get("employee_id")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO AssetAssignments (AssetID, AssignedToEmployeeID, AssignedByEmployeeID, AssignedDate, Notes, Status)
            VALUES (?, ?, ?, ?, ?, 'Assigned')
            """,
            (asset_id, assigned_to, manager_id, assigned_date, notes)
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Asset assigned successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# GET: All assignments made by this manager
# ============================================================

@manager_bp.route("/assignments", methods=["GET"])
def get_assignments():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                aa.ID,
                a.AssetSN,
                a.AssetName,
                emp.FirstName + ' ' + emp.LastName AS AssignedTo,
                emp.Email AS AssignedToEmail,
                aa.AssignedDate,
                aa.Notes,
                aa.Status
            FROM AssetAssignments aa
            JOIN Assets a ON aa.AssetID = a.ID
            JOIN Employees emp ON aa.AssignedToEmployeeID = emp.ID
            ORDER BY aa.AssignedDate DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        assignments = []
        for row in rows:
            assignments.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "assigned_to": row[3],
                "assigned_to_email": row[4],
                "assigned_date": str(row[5]) if row[5] else "",
                "notes": row[6] or "",
                "status": row[7]
            })

        return jsonify({"success": True, "assignments": assignments})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# GET: All work completion forms submitted to this manager
# ============================================================

@manager_bp.route("/completion-forms", methods=["GET"])
def get_completion_forms():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                wc.ID,
                a.AssetSN,
                a.AssetName,
                emp.FirstName + ' ' + emp.LastName AS SubmittedBy,
                wc.CompletionDate,
                wc.WorkDoneDescription,
                wc.ProblemsEncountered,
                wc.RecommendedActions,
                wc.FinalCondition,
                aa.Status
            FROM WorkCompletionForms wc
            JOIN AssetAssignments aa ON wc.AssignmentID = aa.ID
            JOIN Assets a ON aa.AssetID = a.ID
            JOIN Employees emp ON wc.SubmittedByEmployeeID = emp.ID
            ORDER BY wc.CompletionDate DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        forms = []
        for row in rows:
            forms.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "submitted_by": row[3],
                "completion_date": str(row[4]) if row[4] else "",
                "work_done": row[5] or "",
                "problems": row[6] or "",
                "recommended_actions": row[7] or "",
                "final_condition": row[8] or "",
                "status": row[9]
            })

        return jsonify({"success": True, "forms": forms})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500


# ============================================================
# GET: Work received forms submitted by Accountable Parties
# ============================================================

@manager_bp.route("/received-forms", methods=["GET"])
def get_received_forms():
    if not require_manager():
        return jsonify({"success": False, "message": "Access denied."}), 403

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                wr.ID,
                a.AssetSN,
                a.AssetName,
                emp.FirstName + ' ' + emp.LastName AS ReceivedBy,
                wr.ReceivedDate,
                wr.ConditionOnReceiving,
                wr.CommentsOnReceiving
            FROM WorkReceivedForms wr
            JOIN AssetAssignments aa ON wr.AssignmentID = aa.ID
            JOIN Assets a ON aa.AssetID = a.ID
            JOIN Employees emp ON wr.ReceivedByEmployeeID = emp.ID
            ORDER BY wr.ReceivedDate DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        forms = []
        for row in rows:
            forms.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "received_by": row[3],
                "received_date": str(row[4]) if row[4] else "",
                "condition": row[5] or "",
                "comments": row[6] or ""
            })

        return jsonify({"success": True, "forms": forms})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500
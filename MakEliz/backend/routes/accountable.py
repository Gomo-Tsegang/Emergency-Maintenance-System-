from flask import Blueprint, request, jsonify, session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

accountable_bp = Blueprint("accountable", __name__)

def require_accountable():
    if "employee_id" not in session:
        return False
    return True

# GET: Assets assigned to this Accountable Party
@accountable_bp.route("/my-assets", methods=["GET"])
def get_my_assets():
    if not require_accountable():
        return jsonify({"success": False, "message": "Access denied."}), 403

    employee_id = session.get("employee_id")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.ID,
                a.AssetSN,
                a.AssetName,
                d.Name AS Department,
                l.Name AS Location,
                ag.Name AS AssetGroup,
                a.Description,
                a.WarrantyDate
            FROM Assets a
            LEFT JOIN DepartmentLocations dl ON a.DepartmentLocationID = dl.ID
            LEFT JOIN Departments d ON dl.DepartmentID = d.ID
            LEFT JOIN Locations l ON dl.LocationID = l.ID
            LEFT JOIN AssetGroups ag ON a.AssetGroupID = ag.ID
            WHERE a.EmployeeID = ?
            ORDER BY a.AssetName
            """,
            (employee_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        assets = []
        for row in rows:
            assets.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "department": row[3] or "",
                "location": row[4] or "",
                "asset_group": row[5] or "",
                "description": row[6] or "",
                "warranty_date": str(row[7]) if row[7] else ""
            })

        return jsonify({"success": True, "assets": assets})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500

# GET All assignments for this Accountable Party
@accountable_bp.route("/my-assignments", methods=["GET"])
def get_my_assignments():
    if not require_accountable():
        return jsonify({"success": False, "message": "Access denied."}), 403

    employee_id = session.get("employee_id")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                aa.ID,
                a.AssetSN,
                a.AssetName,
                mgr.FirstName + ' ' + mgr.LastName AS AssignedBy,
                aa.AssignedDate,
                aa.Notes,
                aa.Status,
                CASE WHEN wr.ID IS NOT NULL THEN 1 ELSE 0 END AS ReceivedFormFilled,
                CASE WHEN wc.ID IS NOT NULL THEN 1 ELSE 0 END AS CompletionFormFilled
            FROM AssetAssignments aa
            JOIN Assets a ON aa.AssetID = a.ID
            JOIN Employees mgr ON aa.AssignedByEmployeeID = mgr.ID
            LEFT JOIN WorkReceivedForms wr ON wr.AssignmentID = aa.ID
            LEFT JOIN WorkCompletionForms wc ON wc.AssignmentID = aa.ID
            WHERE aa.AssignedToEmployeeID = ?
            ORDER BY aa.AssignedDate DESC
            """,
            (employee_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        assignments = []
        for row in rows:
            assignments.append({
                "id": row[0],
                "asset_sn": row[1],
                "asset_name": row[2],
                "assigned_by": row[3],
                "assigned_date": str(row[4]) if row[4] else "",
                "notes": row[5] or "",
                "status": row[6],
                "received_form_filled": bool(row[7]),
                "completion_form_filled": bool(row[8])
            })

        return jsonify({"success": True, "assignments": assignments})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500

# POST: Submit work received form
@accountable_bp.route("/submit-received", methods=["POST"])
def submit_received():
    if not require_accountable():
        return jsonify({"success": False, "message": "Access denied."}), 403

    employee_id = session.get("employee_id")
    data = request.get_json()

    assignment_id = data.get("assignment_id")
    received_date = data.get("received_date")
    condition = data.get("condition_on_receiving", "")
    comments = data.get("comments_on_receiving", "")

    if not assignment_id or not received_date:
        return jsonify({"success": False, "message": "Assignment and received date are required."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID FROM WorkReceivedForms WHERE AssignmentID = ?",
            (assignment_id,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "You have already submitted a received form for this assignment."}), 409

        cursor.execute(
            """
            INSERT INTO WorkReceivedForms (AssignmentID, ReceivedDate, ReceivedByEmployeeID, ConditionOnReceiving, CommentsOnReceiving)
            VALUES (?, ?, ?, ?, ?)
            """,
            (assignment_id, received_date, employee_id, condition, comments)
        )

        cursor.execute(
            "UPDATE AssetAssignments SET Status = 'In Progress' WHERE ID = ?",
            (assignment_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Work received form submitted successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500



# POST: Submit work completion form
@accountable_bp.route("/submit-completion", methods=["POST"])
def submit_completion():
    if not require_accountable():
        return jsonify({"success": False, "message": "Access denied."}), 403

    employee_id = session.get("employee_id")
    data = request.get_json()

    assignment_id = data.get("assignment_id")
    completion_date = data.get("completion_date")
    work_done = data.get("work_done_description", "")
    problems = data.get("problems_encountered", "")
    recommended = data.get("recommended_actions", "")
    final_condition = data.get("final_condition", "")

    if not assignment_id or not completion_date or not work_done:
        return jsonify({"success": False, "message": "Assignment, completion date, and work description are required."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID FROM WorkReceivedForms WHERE AssignmentID = ?",
            (assignment_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "You must submit the work received form before submitting the completion form."}), 400

        cursor.execute(
            "SELECT ID FROM WorkCompletionForms WHERE AssignmentID = ?",
            (assignment_id,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "You have already submitted a completion form for this assignment."}), 409

        cursor.execute(
            """
            INSERT INTO WorkCompletionForms
                (AssignmentID, CompletionDate, SubmittedByEmployeeID, WorkDoneDescription, ProblemsEncountered, RecommendedActions, FinalCondition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (assignment_id, completion_date, employee_id, work_done, problems, recommended, final_condition)
        )

        cursor.execute(
            "UPDATE AssetAssignments SET Status = 'Completed' WHERE ID = ?",
            (assignment_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Completion form submitted to the Manager successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500
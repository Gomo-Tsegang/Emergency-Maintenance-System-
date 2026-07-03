# ============================================================
# database.py
# Handles the connection to SSMS (SQL Server)
# ============================================================

import pyodbc
from config import DB_CONFIG


def get_connection():
    connection_parts = [
        f"DRIVER={{{DB_CONFIG['DRIVER']}}}",
        f"SERVER={DB_CONFIG['SERVER']}",
        f"DATABASE={DB_CONFIG['DATABASE']}"
    ]

    if str(DB_CONFIG.get("TRUSTED_CONNECTION", "")).strip().lower() in ["yes", "true", "sspi"]:
        connection_parts.append("Trusted_Connection=yes")
    else:
        connection_parts.append(f"UID={DB_CONFIG['USERNAME']}")
        connection_parts.append(f"PWD={DB_CONFIG['PASSWORD']}")

    connection_string = ";".join(connection_parts) + ";"
    connection = pyodbc.connect(connection_string)
    return connection


def ensure_employee_role_column():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Employees' AND COLUMN_NAME = 'Role'"
    )
    has_role_column = cursor.fetchone()[0] > 0

    if not has_role_column:
        cursor.execute("ALTER TABLE Employees ADD Role NVARCHAR(100) NULL")
        cursor.execute(
            "UPDATE Employees SET Role = CASE WHEN IsAdmin = 1 THEN 'Admin' ELSE 'Accountable Party' END"
        )
        conn.commit()

    conn.close()

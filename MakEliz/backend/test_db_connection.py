from database import get_connection


def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == 1:
            print("Database connection successful.")
        else:
            print("Database connection established, but query returned unexpected result:", result)
    except Exception as exc:
        print("Database connection failed:", str(exc))


if __name__ == "__main__":
    test_connection()

import sqlite3

def login_user(username, password):
    """
    Authenticate user against database
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ❌ SECURITY ISSUE: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if user:
        return True
    return False


def calculate_discount(price, user_type):
    """
    Calculate discount based on user type
    """
    if user_type == "vip":
        return price * 0.8
    elif user_type == "employee":
        return price * 0.7
    else:
        return price * 0.95

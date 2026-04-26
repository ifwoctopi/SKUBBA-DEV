# K'von Gates
# COMP267
# April 29, 2025

import mysql

def execute_query(connection, query, params=()):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchone()  # Change to cursor.fetchall() if multiple results are expected
        cursor.close()
        return results
    except mysql.connector.Error as e:
        raise ValueError(f"Database operation failed: {e}")

def execute_query_ALL(connection, query, params=()):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall()  # Change to cursor.fetchall() if multiple results are expected
        cursor.close()
        return results
    except mysql.connector.Error as e:
        raise ValueError(f"Database operation failed: {e}")
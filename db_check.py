import sqlite3
import os

def check_database_path():
    db_path = "C:/Users\anush\Downloads\sql-query-generator-main\sql-query-generator-main\src\my_database.db"  # Change this to the path you're using
    
    # Check if file exists
    print(f"Database path: {os.path.abspath(db_path)}")
    print(f"Database file exists: {os.path.exists(db_path)}")
    
    # Connect and list all tables with exact case
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables in database (with exact case):")
    for table in tables:
        print(f"  '{table[0]}'")
    
    conn.close()

if __name__ == "__main__":
    check_database_path()
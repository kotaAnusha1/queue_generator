import sqlparse
import sqlite3

# Validate SQL query syntax
def validate_sql(query):
    try:
        parsed  = sqlparse.parse(query)
        if not parsed:
            return False, "Invalid SQL syntax"
        return True, "SQL is valid"
    except Exception as e:
        return False, str(e)

def execute_test_query(query, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(query)

         # If the query is a SELECT, fetch results
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            result = "Query executed successfully."

        conn.commit()
        conn.close()
        return True, result  # Return success and results
    except Exception as e:
        return False, str(e)
    
if __name__ == "__main__":
    sample_sql = "SELECT * FROM director"
    valid, msg = validate_sql(sample_sql)
    print("Validation:",msg)

    if valid:
        executed, exec_msg = execute_test_query(sample_sql)
        print("Execution:", exec_msg)
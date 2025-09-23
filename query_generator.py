import os
import re
from dotenv import load_dotenv
import sqlite3
import google.generativeai as genai

# Load API key from .env
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # make sure to have your GEMINI API key saved in the .env file

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-1.5-flash"  # Using the recommended model from the error message

def clean_sql_output(sql_text):
    """Remove markdown formatting and other artifacts from the generated SQL"""
    # Remove SQL code blocks with triple backticks
    sql_text = re.sub(r'```sql\s*(.*?)```', r'\1', sql_text, flags=re.DOTALL)
    # Remove generic code blocks
    sql_text = re.sub(r'```\s*(.*?)```', r'\1', sql_text, flags=re.DOTALL)
    # Remove single backticks
    sql_text = re.sub(r'`(.*?)`', r'\1', sql_text, flags=re.DOTALL)
    # Strip extra whitespace
    sql_text = sql_text.strip()
    return sql_text

def generate_sql(db_schema, nlp_query):
    """Generates an SQL query from natural language input using Gemini model"""
    # Create prompt that includes database schema and query
    prompt = f"""
    You are an assistant which takes an input a query written in natural language
    and converts this into a well structured SQL query in sqlite.
    The schema of the database is: {db_schema}
    Do not provide an explanation of the query, just the query.
    Return ONLY the raw SQL without any markdown formatting, code blocks, or backticks.
    
    Convert the following request into an SQL query: {nlp_query}
    """
    
    try:
        # Call Gemini API with the specified model
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract and clean the SQL query
        sql_query = clean_sql_output(response.text.strip())
        return sql_query
    except Exception as e:
        # If there's an error with the specified model, try to use any available Gemini model
        try:
            models = genai.list_models()
            available_models = [model.name for model in models if "gemini" in model.name.lower()]
            
            if not available_models:
                return f"Error: No Gemini models available. Please check your API key and access. Original error: {str(e)}"
            
            # Try with the first available model
            model = genai.GenerativeModel(available_models[0])
            response = model.generate_content(prompt)
            sql_query = clean_sql_output(response.text.strip())
            return sql_query
        except Exception as fallback_error:
            return f"Error generating SQL query: {str(fallback_error)}"

def load_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = "\n".join(row[0] for row in cursor.fetchall() if row[0])
    
    conn.close()
    return schema

if __name__ == "__main__":
    user_query = "Select all directors born before 1980."
    db_path = "C:\Users\anush\Downloads\sql-query-generator-main\sql-query-generator-main\src\my_database.db"
    sql_query = generate_sql(load_db_schema(db_path), user_query)
    print(sql_query)
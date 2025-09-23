import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from query_generator import generate_sql, load_db_schema
from sql_validator import validate_sql, execute_test_query
import pandas as pd

# Load API key from .env
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="SQL Query Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern & attractive CSS
st.markdown("""
<style>
    .main-header {
        color: #1E88E5;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
        background: linear-gradient(90deg, #1E88E5, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
    }
    .section-header {
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #90CAF9;
        padding-bottom: 0.5rem;
    }
    .sidebar-header {
        color: #1565C0;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 10px;
        border-radius: 5px;
    }
    .info-box {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton button {
        background-color: #1976D2;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 15px;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #1565C0;
    }
    .stTextInput, .stTextArea {
        border-radius: 5px;
    }
    .stDataFrame {
        border-radius: 5px;
        border: 1px solid #BBDEFB;
    }
    div[data-testid="stSidebar"] {
        background-color: #F5F9FF;
        padding: 2rem 1rem;
    }
    div[data-testid="stSidebar"] hr {
        margin: 15px 0;
        border-color: #BBDEFB;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">SQL Query Assistant</h1>', unsafe_allow_html=True)

# Custom sidebar
with st.sidebar:
    st.markdown('<h2 class="sidebar-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
    
    api_key = st.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.markdown('<div class="success-box">✅ API Key Configured</div>', unsafe_allow_html=True)
    else:
        st.warning("Please enter your Gemini API Key.")
    
    st.divider()
    st.markdown('<h3 class="sidebar-header">📁 Database</h3>', unsafe_allow_html=True)
    db_path = st.text_input("Database Path", "C:/Users\anush\Downloads\sql-query-generator-main\sql-query-generator-main\src\my_database.db")
    
    # Add some additional sidebar info/options
    st.divider()

# Main layout - two tabs instead of columns for better organization
tab1, tab2 = st.tabs(["📝 Generate Query", "📊 View Results"])

with tab1:
    st.markdown('<h2 class="section-header">Natural Language Input</h2>', unsafe_allow_html=True)
    
    natural_language_query = st.text_area(
        "What would you like to query from your database?",
        placeholder="Example: Show me all customers who spent more than $500 last month, sorted by total amount",
        height=120
    )
    
    # Initialize session state for sql_query if not set
    if "sql_query" not in st.session_state:
        st.session_state["sql_query"] = ""
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔮 Generate SQL", use_container_width=True):
            if natural_language_query.strip():
                with st.spinner("AI is crafting your query..."):
                    st.session_state["sql_query"] = generate_sql(load_db_schema(db_path), natural_language_query)
            else:
                st.warning("Please enter a query.")
    
    st.markdown('<h2 class="section-header">Generated SQL Query</h2>', unsafe_allow_html=True)
    
    # Always display the stored SQL query
    if st.session_state["sql_query"]:
        st.code(st.session_state["sql_query"], language="sql")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("▶️ Run Query", use_container_width=True):
                with st.spinner("Executing query..."):
                    if st.session_state["sql_query"]:
                        is_valid, validation_msg = validate_sql(st.session_state["sql_query"])
                        if is_valid:
                            st.success("SQL is valid!")
                            success, result = execute_test_query(st.session_state["sql_query"], db_path)
                            if success:
                                # Convert to pandas DataFrame if it's a list
                                if isinstance(result, list):
                                    if result and isinstance(result[0], dict):
                                        # If list of dictionaries
                                        result = pd.DataFrame(result)
                                    else:
                                        # If simple list
                                        result = pd.DataFrame(result)
                                
                                st.session_state["query_result"] = result
                                st.info("✅ Query executed successfully! Go to the 'View Results' tab to see the data.")
                            else:
                                st.error(f"Execution Error: {result}")
                        else:
                            st.error(f"Invalid SQL: {validation_msg}")
    else:
        st.markdown('<div class="info-box">Your SQL query will appear here after generation</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<h2 class="section-header">Query Results</h2>', unsafe_allow_html=True)
    
    if "query_result" in st.session_state:
        result = st.session_state["query_result"]
        
        # Add summary statistics
        if isinstance(result, pd.DataFrame) and not result.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", result.shape[0])
            with col2:
                st.metric("Columns", result.shape[1])
            with col3:
                st.metric("Data Size", f"{result.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Display results with enhanced styling
            st.dataframe(
                result,
                use_container_width=True
            )
            
            # Download options
            col1, col2 = st.columns([1, 3])
            with col1:
                csv = result.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "💾 Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("Query returned no results")
    else:
        st.markdown('<div class="info-box">Execute a query first to see results here</div>', unsafe_allow_html=True)
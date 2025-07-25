
import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="SQL Coder", page_icon="🤖")

# --- UI Configuration ---
st.markdown("""
<style>
    .stApp { 
        background-color: #f0f2f6;
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 100%;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a;
    }
    .st-emotion-cache-1avcm0n {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)



# --- Main App ---
st.title("🤖 SQL Coder: Natural Language to SQL")
st.write("Powered by `defog/sqlcoder-7b-2`. Ask a question in plain English, and get a SQL query.")

# --- Sidebar for Schema ---
with st.sidebar:
    st.header("API Configuration")
    api_url = st.text_input("API URL", value="http://127.0.0.1:8000")
    st.header("Database Schema")
    st.info("Provide the `CREATE TABLE` statements for your database schema below.")
    default_schema = """CREATE TABLE users (\n    user_id SERIAL PRIMARY KEY,\n    username VARCHAR(50) NOT NULL,\n    email VARCHAR(100) NOT NULL,\n    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE TABLE products (\n    product_id SERIAL PRIMARY KEY,\n    name VARCHAR(100) NOT NULL,\n    price DECIMAL(10, 2) NOT NULL\n);"""
    schema = st.text_area("Schema", value=default_schema, height=300)

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL..."):
            try:
                response = requests.post(f"{api_url}/generate-sql", json={"question": prompt, "schema": schema})
                response.raise_for_status()  # Raise an exception for bad status codes
                sql_query = response.json()["sql"]
                st.code(sql_query, language='sql')
                st.session_state.messages.append({"role": "assistant", "content": sql_query})
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {e}")

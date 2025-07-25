
import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="SQL Coder", page_icon="🤖")





# --- Main App ---
st.title("🤖 SQL Coder: Natural Language to SQL")
st.write("Powered by `defog/sqlcoder-7b-2`. Ask a question in plain English, and get a SQL query.")

# --- Sidebar for Schema ---
with st.sidebar:
    st.header("API Configuration")
    api_url = st.text_input("API URL", value="", placeholder="Paste the ngrok URL here")
    st.info("The database schema is now managed by the API.")

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
        if not api_url:
            st.warning("Please enter the API URL in the sidebar to connect to the backend.")
            st.stop()

        with st.spinner("Generating SQL..."):
            try:
                response = requests.post(f"{api_url}/generate-sql", json={"question": prompt})
                response.raise_for_status()  # Raise an exception for bad status codes
                sql_query = response.json()["sql"]
                st.code(sql_query, language='sql')
                st.session_state.messages.append({"role": "assistant", "content": sql_query})
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {e}")

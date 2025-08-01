
import streamlit as st
import requests
import pandas as pd
import sqlparse
from db_utils import create_db_engine, DB_NAME

st.set_page_config(layout="wide", page_title="SQL Coder", page_icon="🤖")


# --- Main App ---
st.title("🤖 SQL Coder: Natural Language to SQL")
st.write("Powered by `defog/sqlcoder-7b-2`. Ask a question in plain English, and get a SQL query.")

# --- Sidebar for Schema ---
with st.sidebar:
    st.header("API Configuration")
    api_url = st.text_input("API URL", value="", placeholder="Paste the ngrok URL here")
    st.info("The database being used is the Kaggle Bike Store Relational Database")

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
                formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                st.code(formatted_sql, language='sql')
                st.session_state.messages.append({"role": "assistant", "content": formatted_sql})
                st.session_state.last_query = sql_query

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {e}")

if "last_query" in st.session_state and st.session_state.last_query:
    try:
        engine = create_db_engine()
        if engine:
            with engine.connect() as connection:
                df = pd.read_sql(st.session_state.last_query, connection)
                st.dataframe(df)

                # Add a section for data analysis
                with st.expander("View Analysis"):
                    with st.spinner("Generating analysis..."):
                        try:
                            analysis_response = requests.post(f"{api_url}/analyze", json={
                                "question": st.session_state.messages[-2]['content'],
                                "sql_query": st.session_state.last_query,
                                "table_data": df.to_string()
                            })
                            analysis_response.raise_for_status()
                            analysis = analysis_response.json()["analysis"]
                            st.markdown(analysis)
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error connecting to the analysis API: {e}")
                        except Exception as e:
                            st.error(f"Error during analysis: {e}")

        else:
            st.error("Could not connect to the database.")
    except Exception as e:
        st.error(f"Error executing query: {e}")

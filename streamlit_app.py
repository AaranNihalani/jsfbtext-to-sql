
import streamlit as st

# Show title and description.


# Sidebar with model info, instructions, and editable schema
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=120)
    st.markdown("## Natural Text to SQL Chatbot (Lightweight)")
    st.markdown(
        "This chatbot uses the [cssupport/t5-small-awesome-text-to-sql](https://huggingface.co/cssupport/t5-small-awesome-text-to-sql) model to generate SQL queries from natural language.\n"
        "\n**Instructions:**\n"
        "- Ask a clear question about your database.\n"
        "- The model will generate a SQL query as a response.\n"
        "- For best results, specify table and column names as they appear in the schema.\n"
        "\n**Model:** cssupport/t5-small-awesome-text-to-sql (lightweight, runs anywhere)\n"
        "\n**Powered by:** [Hugging Face Transformers](https://huggingface.co/docs/transformers)"
    )
    st.markdown("---")
    st.markdown("### Database Schema (editable)")
    default_schema = '''
CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    owner_id INTEGER REFERENCES users(user_id)
);
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50),
    project_id INTEGER REFERENCES projects(project_id)
);
CREATE TABLE taskassignments (
    assignment_id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(task_id),
    user_id INTEGER REFERENCES users(user_id),
    assigned_date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    task_id INTEGER REFERENCES tasks(task_id),
    user_id INTEGER REFERENCES users(user_id)
);
'''
    schema = st.text_area("Edit the schema as needed:", value=default_schema, height=300)

st.title("🗃️ Natural Language to SQL Chatbot")
st.caption("Type your question about your database and get a SQL query suggestion.")






# Use transformers to run the model locally (flan-t5-base is encoder-decoder)
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import re
from typing import List
from sql_formatter.core import format_sql

@st.cache_resource(show_spinner=True)
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("cssupport/t5-small-awesome-text-to-sql")
    return tokenizer, model

tokenizer, model = load_model()

def query_hf_api(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat history with better formatting
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"<div style='color:#1a73e8;font-weight:bold;'>You:</div> {message['content']}", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(f"<div style='color:#e37400;font-weight:bold;'>SQLBot:</div> {message['content']}", unsafe_allow_html=True)



# Chat input at the bottom
prompt = st.chat_input("Ask a question about your database (e.g. 'Show me all users who signed up in July')...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div style='color:#1a73e8;font-weight:bold;'>You:</div> {prompt}", unsafe_allow_html=True)

    # Improved prompt with more context and instructions for joins
    formatted_prompt = f"Translate the following natural language question into a SQL query. Be sure to use the correct table and column names provided in the schema. When joining tables, use the foreign key relationships defined in the schema.\n\nSchema:\n{schema}\n\nQuestion: {prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL query..."):
            try:
                raw_sql = query_hf_api(formatted_prompt)
                formatted_sql = format_sql(raw_sql)
                # Manually uppercase keywords as a workaround
                keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "LIMIT", "AS", "ON", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "JOIN"]
                formatted_sql_parts = formatted_sql.split()
                for i, part in enumerate(formatted_sql_parts):
                    if part.upper() in keywords:
                        formatted_sql_parts[i] = part.upper()
                formatted_sql = ' '.join(formatted_sql_parts)
                st.markdown("**Generated SQL Query:**")
                st.code(formatted_sql, language='sql')
                sql_to_save = formatted_sql
            except Exception as e:
                st.error(f"An error occurred: {e}")
                sql_to_save = ""
                
    st.session_state.messages.append({"role": "assistant", "content": sql_to_save})

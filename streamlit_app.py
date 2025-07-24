
import streamlit as st


# Use huggingface_hub for direct inference
from huggingface_hub import InferenceClient

# Show title and description.


# Sidebar with model info, instructions, and editable schema
with st.sidebar:
    st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=120)
    st.markdown("## Natural SQL Chatbot")
    st.markdown(
        "This chatbot uses the [Qwen/Qwen1.5-0.5B-Chat](https://huggingface.co/Qwen/Qwen1.5-0.5B-Chat) model to generate SQL queries from natural language.\n"
        "\n**Instructions:**\n"
        "- Ask a question in natural language about your database.\n"
        "- The model will generate a SQL query as a response.\n"
        "\n**Model:** Qwen1.5-0.5B-Chat\n"
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





# Use huggingface_hub InferenceClient for model inference

# Use the original NaturalSQL model (chatdb/natural-sql-7b)
HF_API_KEY = st.secrets["HF_API_KEY"]
MODEL_ID = "chatdb/natural-sql-7b"
client = InferenceClient(model=MODEL_ID, token=HF_API_KEY)

def query_hf_api(prompt, api_key=HF_API_KEY):
    # The InferenceClient returns a string output directly
    return client.text_generation(prompt, max_new_tokens=256, temperature=0.2)


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

    # Format the prompt as in your Colab testing
    formatted_prompt = f'''
# Task
Generate a SQL query to answer the following question: `{prompt}`

### PostgreSQL Database Schema
The query will run on a database with the following schema:

`{schema}`

# SQL
Here is the SQL query that answers the question: `{prompt}`
```sql'''

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL query via Hugging Face API..."):
            try:
                output = query_hf_api(formatted_prompt)
                # Extract SQL from output
                sql = output.split("```sql")[-1].strip()
                st.markdown(f"<div style='color:#e37400;font-weight:bold;'>SQLBot:</div> <pre>{sql}</pre>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error from Hugging Face API: {e}")
                sql = ""
    st.session_state.messages.append({"role": "assistant", "content": sql})

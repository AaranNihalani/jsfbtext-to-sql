from flask import Flask, request
from llama_cpp import Llama

app = Flask(__name__)

# Load model at startup
llm = Llama.from_pretrained(
    repo_id="TheBloke/sqlcoder-7B-GGUF",
    filename="sqlcoder-7b.Q4_K_M.gguf",
    verbose=False
)

def generate_prompt(question, schema):
    prompt = f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
{schema}

### SQL
Given the database schema, here is the SQL query that answers `{question}`:
```sql
"""
    return prompt

@app.route("/generate-sql", methods=["POST"])
def generate_sql():
    data = request.get_json()
    question = data.get("question")
    schema = data.get("schema")
    if not question:
        return {"error": "Question not provided"}

    prompt = generate_prompt(question, schema)
    
    output = llm(prompt, max_tokens=400, stop=["```"], echo=False)
    
    sql_query = output["choices"][0]["text"]
    
    return {"sql": sql_query}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
from flask import Flask, request, jsonify
from llama_cpp import Llama
import os
from pyngrok import ngrok
import toml

app = Flask(__name__)

# Get the home directory
home = os.path.expanduser("~")

# Correctly join the path to the model
model_path = os.path.join(home, ".cache", "huggingface", "hub", "models--TheBloke--sqlcoder-7B-GGUF", "snapshots", "144bf062e825baf76764546718f940f70b1a0302", "sqlcoder-7b.Q4_K_M.gguf")

# Load the Llama model
llm = Llama(
  model_path=model_path,
  n_ctx=2048,  # The max sequence length to use - note that longer sequence lengths require more RAM
  n_threads=8,            # The number of CPU threads to use, tailor to your system and workload
  n_gpu_layers=35         # The number of layers to offload to GPU, if you have GPU acceleration
)

def generate_prompt(question, prompt_file="prompt.md", metadata_file="metadata.sql"):
    with open(prompt_file, "r") as f:
        prompt = f.read()
    with open(metadata_file, "r") as f:
        table_metadata_string = f.read()
    prompt = prompt.format(
        user_question=question, table_metadata_string=table_metadata_string
    )
    return prompt



@app.route('/generate-sql', methods=['POST'])
def generate_sql():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'Question is required.'}), 400

    prompt = generate_prompt(question)

    output = llm(
      prompt,
      max_tokens=1024, # Generate up to 1024 tokens
      stop=["[/SQL]"], # Stop generating just before the model would generate a new question
      echo=False # Echo the prompt back in the output
    )

    sql_query = output["choices"][0]["text"].strip()
    # The model sometimes includes the stop token in the output, so we remove it
    if sql_query.endswith("[/SQL]"):
        sql_query = sql_query[:-6].strip()
    if sql_query.endswith("[SQL]"):
        sql_query = sql_query[:-5].strip()

    return jsonify({'sql': sql_query})

if __name__ == '__main__':
    # Get the authtoken from the secrets file
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        authtoken = secrets["NGROK_AUTHTOKEN"]
        ngrok.set_auth_token(authtoken)
        # Open a http tunnel on the default port 80
        public_url = ngrok.connect(8000)
        print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:8000\"")
        app.run(host="0.0.0.0", port=8000)
    except FileNotFoundError:
        print("Could not find .streamlit/secrets.toml. Please create this file and add your NGROK_AUTHTOKEN.")
    except KeyError:
        print("NGROK_AUTHTOKEN not found in .streamlit/secrets.toml. Please add it to the file.")
    except Exception as e:
        print(f"An error occurred: {e}")
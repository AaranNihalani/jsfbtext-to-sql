# SQL Coder: Natural Language to SQL Query

This project provides a powerful and intuitive interface for converting natural language questions into SQL queries. It leverages the `defog/sqlcoder-7b-2` model to understand user questions and generate accurate SQL code, which can then be executed against a `bike_store` database. The application is composed of a Flask backend that serves the model and a Streamlit frontend for a user-friendly chat interface.

## Features

- **Natural Language to SQL**: Ask questions in plain English and receive a SQL query as a response.
- **Interactive Chat Interface**: A Streamlit-based chat interface for a seamless user experience.
- **Database Interaction**: Run the generated SQL query directly from the interface and view the results in a table.
- **Local Model Serving**: The `sqlcoder-7b-2` model is served locally using `llama-cpp-python`, allowing for offline use and greater privacy.
- **Easy Setup**: A simple setup process to get the database and application running.

## Project Structure

```
.
├── .streamlit/             # Streamlit configuration, including secrets for ngrok
├── api.py                  # Flask API to serve the SQL generation model
├── bike_store/             # Directory containing the CSV data for the database
├── db_utils.py             # Utilities for database connection and data loading
├── load_data.py            # Script to initialize the database and load data
├── metadata.sql            # SQL schema for the bike_store database
├── prompt.md               # The prompt template for the language model
├── requirements.txt        # Python dependencies
└── streamlit_app.py        # The main Streamlit application
```

## How It Works

1.  **Database Setup**: The `load_data.py` script, using `db_utils.py`, sets up a local MySQL database named `bike_store`. It creates the necessary tables based on `metadata.sql` and populates them with data from the CSV files in the `bike_store` directory.
2.  **Backend API**: The `api.py` script starts a Flask server that exposes a `/generate-sql` endpoint. This endpoint takes a natural language question, formats it using the `prompt.md` template, and sends it to the `sqlcoder-7b-2` model. The generated SQL query is then returned.
3.  **Frontend Application**: The `streamlit_app.py` script provides a user-friendly chat interface. Users can enter their questions, which are sent to the Flask API. The returned SQL query is displayed, and the user has the option to execute it against the database.

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server
- An `ngrok` account and authtoken for exposing the local Flask server to the internet.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/jsfbtext-to-sql.git
    cd jsfbtext-to-sql
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up the database:**

    -   Make sure your MySQL server is running.
    -   Update the database credentials in `db_utils.py`:

        ```python
        DB_USER = "your_mysql_username"
        DB_PASSWORD = "your_mysql_password"
        ```

    -   Run the data loader script:

        ```bash
        python load_data.py
        ```

4.  **Configure ngrok:**

    -   Create a file named `secrets.toml` in the `.streamlit` directory.
    -   Add your `ngrok` authtoken to this file:

        ```toml
        NGROK_AUTHTOKEN = "your_ngrok_authtoken"
        ```

### Running the Application

1.  **Start the Flask API:**

    ```bash
    python api.py
    ```

    This will start the Flask server and create an `ngrok` tunnel. Copy the public URL provided by `ngrok`.

2.  **Run the Streamlit app:**

    ```bash
    streamlit run streamlit_app.py
    ```

3.  **Connect the frontend to the backend:**

    -   Open the Streamlit app in your browser.
    -   In the sidebar, paste the `ngrok` URL from the previous step into the "API URL" field.

4.  **Start asking questions!**

    You can now ask questions in the chat interface, and the application will generate and execute the corresponding SQL queries.

## Example Questions

-   "What are the top 5 most expensive products?"
-   "How many orders were placed in New York?"
-   "Show me all the customers from California."

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
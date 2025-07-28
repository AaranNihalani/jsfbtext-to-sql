import os
import pandas as pd
from sqlalchemy import create_engine, text

# --- Database Configuration ---
# IMPORTANT: Replace with your MySQL credentials
DB_USER = "root"  # Or your MySQL username
DB_PASSWORD = "" # Replace with your password
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "bike_store"

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "bike_store")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.sql")

def create_db_engine():
    """Creates a SQLAlchemy database engine."""
    try:
        # Ensure the database exists, create if not
        conn_str_no_db = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
        engine_no_db = create_engine(conn_str_no_db)
        with engine_no_db.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            print(f"Database '{DB_NAME}' is ready.")

        # Connect to the specific database
        conn_str = f"{conn_str_no_db}/{DB_NAME}"
        engine = create_engine(conn_str)
        with engine.connect():
            print("Successfully connected to the MySQL database.")
        return engine
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        print("\nPlease ensure:")
        print("1. Your MySQL server is running.")
        print("2. You have updated DB_USER and DB_PASSWORD in this script with your correct credentials.")
        return None

def execute_sql_from_file(engine, filepath):
    """Reads and executes SQL statements from a file to create tables if they don't exist."""
    try:
        with engine.connect() as connection:
            with open(filepath, 'r') as f:
                sql_script = f.read()
                for statement in sql_script.split(';'):
                    if statement.strip():
                        connection.execute(text(statement))
            print(f"Successfully created tables from {os.path.basename(filepath)}")
    except Exception as e:
        print(f"Error executing SQL from {filepath}: {e}")

def load_csv_to_table(engine, table_name, csv_path):
    """Loads data from a CSV file into a database table if the table is empty."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one_or_none()
            if result == 0:
                df = pd.read_csv(csv_path)
                df.to_sql(table_name, con=engine, if_exists='append', index=False)
                print(f"Successfully loaded data into '{table_name}' from {os.path.basename(csv_path)}.")
            else:
                print(f"Table '{table_name}' already contains data. Skipping CSV load.")
    except Exception as e:
        print(f"Error loading data into '{table_name}': {e}")

def load_data():
    """Main function to create tables and load data."""
    engine = create_db_engine()
    if not engine:
        return

    print("\n--- Step 1: Creating tables ---")
    execute_sql_from_file(engine, METADATA_FILE)

    print("\n--- Step 2: Loading data from CSV files ---")
    # Order of loading matters due to foreign key constraints.
    # This is a simple alphabetical sort, might need adjustment for complex schemas.
    csv_files = sorted([f for f in os.listdir(CSV_DIR) if f.endswith('.csv')])

    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0]
        csv_path = os.path.join(CSV_DIR, csv_file)
        load_csv_to_table(engine, table_name, csv_path)

    print("\nData loading process finished.")
Task
Generate a SQL query to answer [QUESTION]{user_question}[/QUESTION]

Instructions
- Generate a single, syntactically correct MySQL query.
- The query must start with `SELECT`.
- Round any numerical results to 2 decimal places.
- Use descriptive and human-readable column aliases.
- `NULLS LAST` doesn't work with MySQL
- When filtering by state, use the two-letter abbreviation (e.g., 'New York' should be 'NY', 'California' should be 'CA', 'Texas' should be 'TX').
- Do not add any markdown formatting (e.g., ```sql) to the query.
- Check that all columns queried are in the right tables in the schema
- If you cannot answer the question with the available database schema, return 'I do not know'.

Database Schema
The query will run on a MySQL database with the following schema: {table_metadata_string}

Answer
[SQL]
import sqlite3

# Define the schema creation SQL queries
create_user_table = """
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY,
    nickname TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    birth_date DATE NOT NULL,
    password TEXT NOT NULL
)
"""

create_post_table = """
CREATE TABLE IF NOT EXISTS Post (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id)
)
"""

create_like_table = """
CREATE TABLE IF NOT EXISTS Like (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Post (id),
    FOREIGN KEY (user_id) REFERENCES User (id)
)
"""

# Function to create the database schema
def create_schema():
    # Connect to the SQLite database
    conn = sqlite3.connect('flaskbook.db')
    cursor = conn.cursor()

    # Execute the schema creation SQL queries
    cursor.execute(create_user_table)
    cursor.execute(create_post_table)
    cursor.execute(create_like_table)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print("Schema created successfully.")

if __name__ == "__main__":
    create_schema()

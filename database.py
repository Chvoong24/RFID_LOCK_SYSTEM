import sqlite3

# Connect to the database
connection = sqlite3.connect("tags.db")
cursor = connection.cursor()

# Create the table if it doesn't already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id TEXT UNIQUE NOT NULL
)
""")

# List of tag IDs to add to the database
tag_ids = [
    "688b61af6"
]

# Insert tag IDs into the table
for tag_id in tag_ids:
    try:
        cursor.execute("INSERT INTO tags (tag_id) VALUES (?)", (tag_id,))
    except sqlite3.IntegrityError:
        print(f"Tag ID {tag_id} already exists in the database.")

# Commit changes and close the connection
connection.commit()
connection.close()

print("Tag IDs added to the database.")
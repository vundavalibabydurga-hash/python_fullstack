import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
    ("Durga", "durga@gmail.com", "12345678")
)

conn.commit()
conn.close()

print("User added successfully")
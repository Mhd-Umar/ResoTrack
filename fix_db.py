import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

commands = [
    "UPDATE django_migrations SET app = 'Reso_Track' WHERE app = 'core';",
    "ALTER TABLE core_user RENAME TO Reso_Track_user;",
    "ALTER TABLE core_user_groups RENAME TO Reso_Track_user_groups;",
    "ALTER TABLE core_user_user_permissions RENAME TO Reso_Track_user_user_permissions;",
    "ALTER TABLE core_lab RENAME TO Reso_Track_lab;",
    "ALTER TABLE core_complaint RENAME TO Reso_Track_complaint;",
    "ALTER TABLE core_resource RENAME TO Reso_Track_resource;",
    "ALTER TABLE core_suggestion RENAME TO Reso_Track_suggestion;",
    "ALTER TABLE core_stock RENAME TO Reso_Track_stock;"
]

for cmd in commands:
    try:
        print(f"Executing: {cmd}")
        cursor.execute(cmd)
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

conn.commit()
conn.close()
print("Migration completed.")

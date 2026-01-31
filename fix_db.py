import sqlite3
import os

# 1. Connect to the database
db_path = 'tailor.db'

if not os.path.exists(db_path):
    print("❌ Error: tailor.db not found! Make sure this script is in the same folder as app.py")
    exit()

print(f"🔧 Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Define the new columns we need to add
new_columns = [
    ("price_per_suit", "INTEGER DEFAULT 0"),
    ("total_amount", "INTEGER DEFAULT 0"),
    ("advance_payment", "INTEGER DEFAULT 0"),
    ("remaining_balance", "INTEGER DEFAULT 0"),
    ("kaj_count", "VARCHAR(50)"),
    ("pocket_size", "VARCHAR(50)"),
    ("style_patti", "VARCHAR(50)"),
    ("design_button", "VARCHAR(50)"),
    ("salai", "VARCHAR(50)")
]

# 3. Check and Add Columns
print("------------------------------------------------")
cursor.execute("PRAGMA table_info(user)")
existing_columns = [row[1] for row in cursor.fetchall()]

for col_name, col_type in new_columns:
    if col_name not in existing_columns:
        print(f"⚠️  Column '{col_name}' is missing. Adding it now...")
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            print(f"✅  Successfully added '{col_name}'")
        except Exception as e:
            print(f"❌  Failed to add '{col_name}': {e}")
    else:
        print(f"✔️  Column '{col_name}' already exists.")

# 4. Save and Close
conn.commit()
conn.close()
print("------------------------------------------------")
print("🎉 Database Repair Complete! You can now run app.py")
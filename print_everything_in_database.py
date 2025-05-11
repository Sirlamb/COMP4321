import sqlite3

def write_all_tables_contents(db_file, output_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Open text file for writing
    with open(output_file, 'w', encoding='utf-8') as f:
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Write data from each table to file
        for table in tables:
            table_name = table[0]
            f.write(f"\nContents of table: {table_name}\n")
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                f.write(f"{row}\n")

    conn.close()

# Usage
db_file = 'database.db'  # Replace with your database file
output_file = 'database_contents.txt'  # Output file name
write_all_tables_contents(db_file, output_file)

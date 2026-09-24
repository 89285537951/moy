import sqlite3
import os
print("Рабочая директория check_db:", os.getcwd())
DB_PATH = r"C:\Programss\proekt\proekt-mebel-fixed\proekt-mebel-fixed\database.db"

print("Путь к БД:", DB_PATH)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()]
print("Tables:", tables)
print("Categories:", cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0])
print("Furniture:", cur.execute("SELECT COUNT(*) FROM furniture").fetchone()[0])
print("Photos:", cur.execute("SELECT COUNT(*) FROM furniture_photos").fetchone()[0])
print("Countries:", cur.execute("SELECT COUNT(*) FROM countries").fetchone()[0])

con.close()
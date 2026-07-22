import sqlite3
from datetime import datetime

DB_NAME = "civic_reports.db"

def init_db():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            location TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'Pending',
            reported_by TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_report(category, description, location, image_path, reported_by):
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (category, description, location, image_path, reported_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category, description, location, image_path, reported_by, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_all_reports():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_reports_by_user(reported_by):
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE reported_by = ? ORDER BY created_at DESC", (reported_by,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_status(report_id, new_status):
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()
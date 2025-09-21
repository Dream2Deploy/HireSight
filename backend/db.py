# db.py
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "results.db")

def init_db():
    """Initialize database and create table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        candidate_name TEXT,
        resume_file TEXT,
        jd_file TEXT,
        final_score REAL,
        hard_score REAL,
        soft_score REAL,
        verdict TEXT,
        missing_skills TEXT,
        feedback TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_evaluation(candidate_name, resume_file, jd_file, result: dict, feedback: str):
    """Save evaluation result to DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO evaluations (
        timestamp, candidate_name, resume_file, jd_file,
        final_score, hard_score, soft_score, verdict, missing_skills, feedback
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.utcnow().isoformat(),
        candidate_name,
        resume_file,
        jd_file,
        result["final_score"],
        result["hard_score"],
        result["soft_score"],
        result["verdict"],
        json.dumps(result.get("missing_must", []) + result.get("missing_good", [])),
        feedback
    ))
    conn.commit()
    conn.close()

def fetch_all():
    """Fetch all evaluations from DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM evaluations ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

"""Phase 10: SQLite Database Layer for Asynchronous Court Summarization Jobs.

Manages persistent job records, execution states (queued, processing, completed, failed),
and result payloads.
"""

import os
import sys
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("data/court_jobs.db")


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables with schema migrations."""
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                language TEXT,
                method TEXT,
                summary_ratio REAL,
                duration_sec REAL,
                error_message TEXT,
                result_json TEXT
            )
        """)
    conn.close()


def create_job(job_id: str, filename: str, file_path: str, method: str, summary_ratio: float) -> Dict[str, Any]:
    """Insert a new queued job."""
    now = datetime.datetime.utcnow().isoformat()
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT INTO jobs (job_id, filename, file_path, status, created_at, method, summary_ratio)
            VALUES (?, ?, ?, 'queued', ?, ?, ?)
        """, (job_id, filename, file_path, now, method, summary_ratio))
    conn.close()
    return {
        "job_id": job_id,
        "filename": filename,
        "status": "queued",
        "created_at": now,
        "method": method,
        "summary_ratio": summary_ratio
    }


def update_job_status(
    job_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """Transition job status and store execution output."""
    now = datetime.datetime.utcnow().isoformat()
    conn = get_db_connection()
    result_str = json.dumps(result, ensure_ascii=False) if result else None
    lang = result.get("detected_language") if result else None
    dur = result.get("audio_duration_sec") if result else None

    with conn:
        conn.execute("""
            UPDATE jobs
            SET status = ?, completed_at = ?, language = ?, duration_sec = ?, error_message = ?, result_json = ?
            WHERE job_id = ?
        """, (status, now if status in ("completed", "failed") else None, lang, dur, error, result_str, job_id))
    conn.close()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve single job record by ID."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    if data.get("result_json"):
        data["result"] = json.loads(data["result_json"])
    else:
        data["result"] = None
    return data


def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent jobs ordered by submission time."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    jobs = []
    for r in rows:
        d = dict(r)
        d["has_result"] = bool(d.get("result_json"))
        d.pop("result_json", None)
        jobs.append(d)
    return jobs


if __name__ == "__main__":
    init_db()
    print("Initialized SQLite database at", DB_PATH)

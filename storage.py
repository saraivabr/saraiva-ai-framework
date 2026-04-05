from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                source_filename TEXT NOT NULL,
                source_path TEXT NOT NULL,
                selected_presets TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'in_progress',
                approved_attempt_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                attempt_index INTEGER NOT NULL,
                preset_id TEXT NOT NULL,
                output_filename TEXT NOT NULL,
                output_path TEXT NOT NULL,
                params_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE INDEX IF NOT EXISTS idx_attempts_job_id ON attempts(job_id);
            """
        )


def create_job(db_path: Path, job_id: str, source_filename: str, source_path: str, selected_presets: list[str]) -> None:
    with connect_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO jobs (id, source_filename, source_path, selected_presets)
            VALUES (?, ?, ?, ?)
            """,
            (job_id, source_filename, source_path, json.dumps(selected_presets)),
        )


def get_job(db_path: Path, job_id: str) -> dict[str, Any] | None:
    with connect_db(db_path) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        job = dict(row)
        job["selected_presets"] = json.loads(job["selected_presets"])
        return job


def list_attempts(db_path: Path, job_id: str) -> list[dict[str, Any]]:
    with connect_db(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM attempts WHERE job_id = ? ORDER BY attempt_index ASC", (job_id,)
        ).fetchall()
        attempts: list[dict[str, Any]] = []
        for row in rows:
            attempt = dict(row)
            attempt["params"] = json.loads(attempt["params_json"])
            attempts.append(attempt)
        return attempts


def next_attempt_index(db_path: Path, job_id: str) -> int:
    with connect_db(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(attempt_index), 0) AS last_idx FROM attempts WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        return int(row["last_idx"]) + 1


def create_attempt(
    db_path: Path,
    job_id: str,
    attempt_index: int,
    preset_id: str,
    output_filename: str,
    output_path: str,
    params: dict[str, Any],
) -> int:
    with connect_db(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO attempts (
                job_id, attempt_index, preset_id, output_filename, output_path, params_json, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                job_id,
                attempt_index,
                preset_id,
                output_filename,
                output_path,
                json.dumps(params),
            ),
        )
        conn.execute("UPDATE jobs SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (job_id,))
        return int(cur.lastrowid)


def get_attempt(db_path: Path, attempt_id: int) -> dict[str, Any] | None:
    with connect_db(db_path) as conn:
        row = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()
        if row is None:
            return None
        attempt = dict(row)
        attempt["params"] = json.loads(attempt["params_json"])
        return attempt


def set_attempt_status(db_path: Path, attempt_id: int, status: str) -> None:
    with connect_db(db_path) as conn:
        conn.execute("UPDATE attempts SET status = ? WHERE id = ?", (status, attempt_id))
        conn.execute(
            """
            UPDATE jobs
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT job_id FROM attempts WHERE id = ?)
            """,
            (attempt_id,),
        )


def approve_job(db_path: Path, job_id: str, attempt_id: int) -> None:
    with connect_db(db_path) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = 'approved', approved_attempt_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (attempt_id, job_id),
        )


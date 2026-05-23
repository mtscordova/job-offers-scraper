import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                company     TEXT,
                location    TEXT,
                url         TEXT UNIQUE,
                source      TEXT,
                remote      INTEGER DEFAULT 0,
                description TEXT,
                posted_at   TEXT,
                scraped_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_job(job: dict) -> bool:
    """Insert job, return True if new, False if duplicate URL."""
    with get_conn() as conn:
        try:
            conn.execute(
                """
                INSERT INTO jobs (title, company, location, url, source, remote, description, posted_at)
                VALUES (:title, :company, :location, :url, :source, :remote, :description, :posted_at)
                """,
                job,
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def fetch_jobs(source: str = None, limit: int = 50, days: int = None) -> list:
    with get_conn() as conn:
        conditions = []
        params = []

        if source:
            conditions.append("source = ?")
            params.append(source)

        if days:
            conditions.append("scraped_at >= datetime('now', ?)")
            params.append(f"-{days} days")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        rows = conn.execute(
            f"SELECT * FROM jobs {where} ORDER BY COALESCE(posted_at, scraped_at) DESC LIMIT ?",
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def purge_old_jobs(days: int) -> int:
    """Delete jobs older than N days. Returns number of rows deleted."""
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM jobs WHERE posted_at IS NOT NULL AND posted_at < datetime('now', ?)",
            (f"-{days} days",),
        )
        conn.commit()
        return cur.rowcount


def fetch_stats() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT source, COUNT(*) as total FROM jobs GROUP BY source ORDER BY total DESC"
        ).fetchall()
        return [dict(r) for r in rows]

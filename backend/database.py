"""
database.py — state only. The DB never stores content and never foreign-keys to content
(Atlas invariants 1–2). Rows reference content by key; unresolvable keys are skipped, not
errored. One SQLite file, one process, one writer — no ORM, no pool.

Tables (README §7):
    attempts      append-only ledger of every retrieval attempt (THE source of truth)
    skill_state   per-skill successive-relearning state (granular demotion only)
    card_state    per-card FSRS-lite schedule
    error_log     misses classified + scheduled re-tests
    mocks         mock-quiz results
    hint_events   hint-ladder velocity audit
    activity      one row per day -> streak (1-day grace) + heatmap
    notes         freeform
"""
from __future__ import annotations

import contextlib
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "tuulai.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_key  TEXT NOT NULL,
    mode         TEXT NOT NULL,            -- 'paper' | 'typed'
    result       TEXT NOT NULL,            -- 'correct' | 'partial' | 'wrong'
    confidence   TEXT NOT NULL,            -- 'sure' | 'shaky' | 'guess'
    hints_used   INTEGER NOT NULL DEFAULT 0,
    seconds      INTEGER NOT NULL DEFAULT 0,
    quiz_target  TEXT,                     -- which quiz this was aimed at
    cold         INTEGER NOT NULL DEFAULT 1,  -- 1 if no hints/lookups (counts for mastery)
    at           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_problem ON attempts(problem_key);

CREATE TABLE IF NOT EXISTS skill_state (
    skill_key    TEXT PRIMARY KEY,
    touches      REAL NOT NULL DEFAULT 0,  -- successful cold retrievals (fractional via FIRe)
    distinct_days INTEGER NOT NULL DEFAULT 0,
    last_touch   TEXT,
    due          TEXT,
    strength     REAL NOT NULL DEFAULT 0,
    demoted_at   TEXT
);

CREATE TABLE IF NOT EXISTS card_state (
    card_key  TEXT PRIMARY KEY,
    ease      REAL NOT NULL DEFAULT 2.5,
    interval  INTEGER NOT NULL DEFAULT 0,
    due       TEXT,
    reps      INTEGER NOT NULL DEFAULT 0,
    lapses    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS error_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id  INTEGER,
    problem_key TEXT,
    taxonomy    TEXT NOT NULL,             -- concept | procedure | misread | slip
    note        TEXT,
    retest_key  TEXT,                      -- problem key of the re-test variant
    retest_due  TEXT,
    cleared_at  TEXT,
    at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assembled_mocks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_target   TEXT,
    problem_keys  TEXT NOT NULL,     -- JSON array
    points        REAL,
    duration_min  INTEGER,
    photo_paths   TEXT,             -- JSON array of stored upload paths
    transcripts   TEXT,             -- JSON {key: transcription}
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mocks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_target TEXT,
    quiz_key    TEXT,
    score       REAL,
    total       REAL,
    minutes     INTEGER,
    photo_path  TEXT,
    graded_json TEXT,
    at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hint_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_key TEXT,
    rung        INTEGER NOT NULL,
    at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity (
    day             TEXT PRIMARY KEY,
    retrieval_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    body TEXT NOT NULL,
    at   TEXT NOT NULL
);
"""


@contextlib.contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db() -> None:
    with connect() as c:
        c.executescript(_SCHEMA)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _today() -> str:
    return date.today().isoformat()


# ── attempts (the ledger) ────────────────────────────────────────────────────

def record_attempt(
    problem_key: str, mode: str, result: str, confidence: str,
    hints_used: int = 0, seconds: int = 0, quiz_target: str | None = None,
) -> int:
    """result may be 'pending' at reveal time; grade_attempt() finalizes it."""
    cold = 1 if hints_used == 0 else 0
    with connect() as c:
        cur = c.execute(
            "INSERT INTO attempts (problem_key, mode, result, confidence, hints_used, "
            "seconds, quiz_target, cold, at) VALUES (?,?,?,?,?,?,?,?,?)",
            (problem_key, mode, result, confidence, hints_used, seconds, quiz_target, cold, _now()),
        )
        # activity: one row per day, accumulate
        c.execute(
            "INSERT INTO activity (day, retrieval_count) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET retrieval_count = retrieval_count + 1",
            (_today(),),
        )
        return cur.lastrowid


def get_attempt(aid: int) -> sqlite3.Row | None:
    with connect() as c:
        return c.execute("SELECT * FROM attempts WHERE id=?", (aid,)).fetchone()


def grade_attempt(aid: int, result: str) -> None:
    with connect() as c:
        c.execute("UPDATE attempts SET result=? WHERE id=?", (result, aid))


def attempts_for(problem_key: str) -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute(
            "SELECT * FROM attempts WHERE problem_key=? ORDER BY at", (problem_key,)))


def recent_attempts(limit: int = 50) -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT ?", (limit,)))


def graded_attempts(since_iso: str | None = None) -> list[sqlite3.Row]:
    """Attempts that have a real self-grade (not 'pending') — the calibration/coach dataset."""
    q = "SELECT * FROM attempts WHERE result IN ('correct','partial','wrong')"
    args: tuple = ()
    if since_iso:
        q += " AND at >= ?"
        args = (since_iso,)
    with connect() as c:
        return list(c.execute(q + " ORDER BY at", args))


# ── skill state ──────────────────────────────────────────────────────────────

def get_skill_state(skill_key: str) -> sqlite3.Row | None:
    with connect() as c:
        return c.execute("SELECT * FROM skill_state WHERE skill_key=?", (skill_key,)).fetchone()


def all_skill_state() -> dict[str, sqlite3.Row]:
    with connect() as c:
        return {r["skill_key"]: r for r in c.execute("SELECT * FROM skill_state")}


def upsert_skill_state(
    skill_key: str, add_touches: float, on_day: str, due: str | None,
    strength: float, demote: bool = False,
) -> None:
    with connect() as c:
        row = c.execute("SELECT * FROM skill_state WHERE skill_key=?", (skill_key,)).fetchone()
        prev_day = row["last_touch"][:10] if row and row["last_touch"] else None
        distinct_inc = 1 if (add_touches > 0 and prev_day != on_day) else 0
        if row is None:
            c.execute(
                "INSERT INTO skill_state (skill_key, touches, distinct_days, last_touch, "
                "due, strength, demoted_at) VALUES (?,?,?,?,?,?,?)",
                (skill_key, max(0.0, add_touches), distinct_inc, _now(), due, strength,
                 _now() if demote else None),
            )
        else:
            c.execute(
                "UPDATE skill_state SET touches = MAX(0, touches + ?), "
                "distinct_days = distinct_days + ?, last_touch = ?, due = ?, strength = ?, "
                "demoted_at = ? WHERE skill_key = ?",
                (add_touches, distinct_inc, _now(), due, strength,
                 _now() if demote else row["demoted_at"], skill_key),
            )


# ── card state (FSRS-lite / SM-2-lite) ───────────────────────────────────────

def due_cards(today: str | None = None) -> list[sqlite3.Row]:
    today = today or _today()
    with connect() as c:
        return list(c.execute(
            "SELECT * FROM card_state WHERE due IS NULL OR due <= ? ORDER BY due", (today,)))


def review_card(card_key: str, grade: str) -> None:
    """grade in {'again','good','easy'}. SM-2 lite (Atlas §7.1)."""
    with connect() as c:
        row = c.execute("SELECT * FROM card_state WHERE card_key=?", (card_key,)).fetchone()
        ease = row["ease"] if row else 2.5
        interval = row["interval"] if row else 0
        reps = row["reps"] if row else 0
        lapses = row["lapses"] if row else 0
        if grade == "again":
            interval, lapses, ease = 1, lapses + 1, max(1.3, ease - 0.2)
        else:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 3
            else:
                interval = max(1, round(interval * ease))
            if grade == "easy":
                ease += 0.15
            reps += 1
        due = (date.today() + timedelta(days=interval)).isoformat()
        c.execute(
            "INSERT INTO card_state (card_key, ease, interval, due, reps, lapses) "
            "VALUES (?,?,?,?,?,?) ON CONFLICT(card_key) DO UPDATE SET "
            "ease=excluded.ease, interval=excluded.interval, due=excluded.due, "
            "reps=excluded.reps, lapses=excluded.lapses",
            (card_key, ease, interval, due, reps, lapses),
        )


def activate_cards(card_keys: list[str]) -> None:
    """Lazily enter cards into the schedule when first seen (Atlas §7.1). INSERT OR IGNORE."""
    with connect() as c:
        for k in card_keys:
            c.execute(
                "INSERT OR IGNORE INTO card_state (card_key, due) VALUES (?, ?)",
                (k, _today()))


# ── error log ────────────────────────────────────────────────────────────────

def add_error(problem_key: str, taxonomy: str, note: str, attempt_id: int | None = None,
              retest_key: str | None = None, retest_due: str | None = None) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO error_log (attempt_id, problem_key, taxonomy, note, retest_key, "
            "retest_due, at) VALUES (?,?,?,?,?,?,?)",
            (attempt_id, problem_key, taxonomy, note, retest_key, retest_due, _now()))
        return cur.lastrowid


def open_errors() -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute("SELECT * FROM error_log WHERE cleared_at IS NULL ORDER BY at"))


def clear_error(error_id: int) -> None:
    with connect() as c:
        c.execute("UPDATE error_log SET cleared_at=? WHERE id=?", (_now(), error_id))


# ── hint events ──────────────────────────────────────────────────────────────

def record_hint(problem_key: str, rung: int) -> None:
    with connect() as c:
        c.execute("INSERT INTO hint_events (problem_key, rung, at) VALUES (?,?,?)",
                  (problem_key, rung, _now()))


# ── mocks ────────────────────────────────────────────────────────────────────

def record_mock(quiz_target: str | None, quiz_key: str | None, score: float, total: float,
                minutes: int, photo_path: str | None, graded_json: str | None) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO mocks (quiz_target, quiz_key, score, total, minutes, photo_path, "
            "graded_json, at) VALUES (?,?,?,?,?,?,?,?)",
            (quiz_target, quiz_key, score, total, minutes, photo_path, graded_json, _now()))
        return cur.lastrowid


def mock_history(limit: int = 20) -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute("SELECT * FROM mocks ORDER BY id DESC LIMIT ?", (limit,)))


# ── assembled mocks (the quiz definition being taken) ────────────────────────

def create_assembled_mock(quiz_target: str, problem_keys: list[str], points: float,
                          duration_min: int) -> int:
    import json as _json
    with connect() as c:
        cur = c.execute(
            "INSERT INTO assembled_mocks (quiz_target, problem_keys, points, duration_min, "
            "created_at) VALUES (?,?,?,?,?)",
            (quiz_target, _json.dumps(problem_keys), points, duration_min, _now()))
        return cur.lastrowid


def get_assembled_mock(mock_id: int) -> sqlite3.Row | None:
    with connect() as c:
        return c.execute("SELECT * FROM assembled_mocks WHERE id=?", (mock_id,)).fetchone()


def set_mock_photos_transcripts(mock_id: int, photo_paths: list[str] | None,
                                transcripts: dict | None) -> None:
    import json as _json
    with connect() as c:
        row = c.execute("SELECT photo_paths, transcripts FROM assembled_mocks WHERE id=?",
                        (mock_id,)).fetchone()
        pp = _json.dumps(photo_paths) if photo_paths is not None else (row["photo_paths"] if row else None)
        tr = _json.dumps(transcripts) if transcripts is not None else (row["transcripts"] if row else None)
        c.execute("UPDATE assembled_mocks SET photo_paths=?, transcripts=? WHERE id=?",
                  (pp, tr, mock_id))


# ── activity / streak ────────────────────────────────────────────────────────

def streak() -> int:
    """A streak is alive today OR yesterday (Atlas §7.1 grace day)."""
    with connect() as c:
        days = {r["day"] for r in c.execute(
            "SELECT day FROM activity WHERE retrieval_count > 0")}
    today = date.today()
    cursor = today if today.isoformat() in days else today - timedelta(days=1)
    if cursor.isoformat() not in days:
        return 0
    n = 0
    while cursor.isoformat() in days:
        n += 1
        cursor -= timedelta(days=1)
    return n


def heatmap(days_back: int = 84) -> dict[str, int]:
    since = (date.today() - timedelta(days=days_back)).isoformat()
    with connect() as c:
        return {r["day"]: r["retrieval_count"] for r in c.execute(
            "SELECT day, retrieval_count FROM activity WHERE day >= ?", (since,))}


# ── notes ────────────────────────────────────────────────────────────────────

def add_note(body: str) -> int:
    with connect() as c:
        cur = c.execute("INSERT INTO notes (body, at) VALUES (?,?)", (body, _now()))
        return cur.lastrowid


def list_notes() -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute("SELECT * FROM notes ORDER BY id DESC"))

"""Decision logging facade with SQLite primary storage and JSON fallback."""

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from filelock import FileLock

from app.config import DECISION_LOG_FILE, DECISION_LOG_LOCK_FILE
from storage import database

logger = logging.getLogger(__name__)
_DECISION_LOG_LOCK = FileLock(DECISION_LOG_LOCK_FILE)

try:
    database.init_database()
except Exception:
    logger.exception("Database init failed in decision_log module")


def _load_decision_log_json() -> List[dict]:
    """Load debug fallback log from JSON."""
    if not os.path.exists(DECISION_LOG_FILE):
        return []
    try:
        with open(DECISION_LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        logger.exception("Decision JSON load failed")
        return []


def _save_decision_log_json(log_entries: List[dict]) -> None:
    """Save debug fallback log to JSON."""
    try:
        with open(DECISION_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
    except Exception:
        logger.exception("Decision JSON save failed")


def _append_decision_log_json(log_entry: Dict[str, Any]) -> None:
    """Append one record to debug JSON file."""
    with _DECISION_LOG_LOCK:
        log_entries = _load_decision_log_json()
        log_entries.append(log_entry)
        _save_decision_log_json(log_entries)


def _row_to_legacy_entry(row: Any) -> Dict[str, Any]:
    """Map SQLite row shape to legacy JSON entry shape used by UI."""
    file_name = (
        row["file_name"] if isinstance(row, sqlite3.Row) else row.get("file_name")
    )
    entry = {
        "timestamp": row["timestamp"],
        "file": file_name,
        "file_name": file_name,
        "category": row["category"],
        "subject": row["subject"],
        "confidence": row["confidence"],
        "extraction_status": row["extraction_status"],
        "reason": row["reason"],
        "action": row["action"],
        "destination": row["destination"],
        "file_path": None,
        "file_size_bytes": None,
        "details": {"storage": "sqlite"},
    }
    return entry


def _get_decision_log_from_db() -> List[dict]:
    conn = None
    try:
        conn = database.get_connection()
        rows = conn.execute(
            """
            SELECT
                timestamp,
                file_name,
                category,
                subject,
                confidence,
                action,
                destination,
                extraction_status,
                reason
            FROM decisions
            ORDER BY id ASC
            """
        ).fetchall()
        return [_row_to_legacy_entry(row) for row in rows]
    finally:
        if conn is not None:
            conn.close()


def log_decision(*args, **kwargs) -> None:
    """
    Log a file processing decision with full details.

    Supported call patterns:
    1) Legacy style used by existing modules:
       log_decision(file_path=..., action=..., reason=..., category=..., ...)
    2) New compact style:
       log_decision(file_name, category, subject, confidence, action,
                    destination, extraction_status, reason)
    """
    if len(args) == 8 and not kwargs:
        (
            file_name,
            category,
            subject,
            confidence,
            action,
            destination,
            extraction_status,
            reason,
        ) = args
        file_path = str(file_name or "")
        details = {"api": "compact"}
    else:
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else "")
        action = kwargs.get("action", args[1] if len(args) > 1 else "")
        reason = kwargs.get("reason", args[2] if len(args) > 2 else "")
        category = kwargs.get("category", args[3] if len(args) > 3 else None)
        subject = kwargs.get("subject", args[4] if len(args) > 4 else None)
        destination = kwargs.get("destination", args[5] if len(args) > 5 else None)
        confidence = kwargs.get("confidence", args[6] if len(args) > 6 else None)
        details = kwargs.get("details", args[7] if len(args) > 7 else None)

        extraction_status = "unknown"
        if details and isinstance(details, dict):
            extraction_status = details.get("extraction_status", "unknown")

        file_name = os.path.basename(file_path) if file_path else ""

    file_size = 0
    if os.path.exists(file_path):
        try:
            file_size = os.path.getsize(file_path)
        except Exception:
            pass

    if len(args) == 8 and not kwargs:
        file_name = str(file_name or "")

    timestamp = datetime.utcnow().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "file": file_name,
        "file_name": file_name,
        "category": category,
        "subject": subject,
        "confidence": confidence,
        "extraction_status": extraction_status,
        "reason": reason,
        "action": action,
        "file_path": file_path,
        "file_size_bytes": file_size,
        "destination": destination,
        "details": details or {},
    }
    decision = {
        "timestamp": timestamp,
        "file_name": file_name,
        "category": category,
        "subject": subject,
        "confidence": confidence,
        "action": action,
        "destination": destination,
        "extraction_status": extraction_status,
        "reason": reason,
    }

    try:
        database.insert_decision(decision)
    except Exception:
        logger.exception("SQLite decision insert failed, falling back to JSON")
        _append_decision_log_json(log_entry)


def get_decision_log() -> list:
    """Retrieve all decisions (SQLite primary, JSON fallback)."""
    try:
        return _get_decision_log_from_db()
    except Exception:
        logger.exception("SQLite decision read failed, using JSON fallback")
        with _DECISION_LOG_LOCK:
            return _load_decision_log_json()


def get_decisions_by_action(action: str) -> list:
    """Get all decisions of a specific action type."""
    log = get_decision_log()
    return [entry for entry in log if entry.get("action") == action]


def get_decisions_by_file(file_name: str) -> list:
    """Get all decisions related to a specific file."""
    log = get_decision_log()
    return [
        entry
        for entry in log
        if file_name.lower() in (entry.get("file") or entry.get("file_name") or "").lower()
    ]


def clear_decision_log() -> None:
    """Clear the decision log (for testing/reset)."""
    conn = None
    try:
        conn = database.get_connection()
        conn.execute("DELETE FROM decisions")
        conn.commit()
    except Exception:
        logger.exception("Failed to clear SQLite decisions table")
    finally:
        if conn is not None:
            conn.close()

    with _DECISION_LOG_LOCK:
        _save_decision_log_json([])


def print_log_summary() -> None:
    """Print a summary of the decision log."""
    log = get_decision_log()
    if not log:
        print("📋 Decision log is empty.")
        return

    moved = len([e for e in log if e.get("action") == "moved"])
    skipped = len([e for e in log if e.get("action") == "skipped"])
    duplicates = len([e for e in log if e.get("action") == "duplicate"])
    errors = len([e for e in log if e.get("action") == "error"])

    print("\n" + "=" * 60)
    print("📊 DECISION LOG SUMMARY")
    print("=" * 60)
    print(f"Files Moved:      {moved}")
    print(f"Files Skipped:    {skipped}")
    print(f"Duplicates Found: {duplicates}")
    print(f"Processing Errors: {errors}")
    print(f"Total Entries:    {len(log)}")
    print(f"Log File:         {DECISION_LOG_FILE}")
    print("=" * 60 + "\n")

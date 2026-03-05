"""Centralized configuration constants for organizer runtime."""

from pathlib import Path


# Project root.
BASE_DIR = Path(__file__).resolve().parent.parent

# Keep existing default source folder behavior.
INPUT_FOLDERS = ["D:/TEST_AI/input"]

# Organizer data/log paths.
DECISION_LOG_FILE = str(BASE_DIR / "decision_log.json")
DECISION_LOG_LOCK_FILE = str(BASE_DIR / "decision_log.lock")
FILE_LOG_CSV = str(BASE_DIR / "file_logs.csv")
MOVE_HISTORY_FILE = str(BASE_DIR / "move_history.json")

# Semantic memory/vector storage paths.
MODEL_CACHE_DIR = str(BASE_DIR / "model_cache")
SEMANTIC_MEMORY_INDEX = str(BASE_DIR / "semantic_memory.index")
SEMANTIC_MEMORY_META = str(BASE_DIR / "semantic_memory_meta.pkl")
VECTOR_STORE_FILE = str(BASE_DIR / "vector_store.pkl")

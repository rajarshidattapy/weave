"""
SQLite database models and CRUD operations for Weave component storage.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "weave.db")


def _get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS components (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_library TEXT,
            source_url TEXT,
            component_type TEXT,
            description TEXT,
            tags TEXT,
            styles TEXT,
            dependencies TEXT,
            install_command TEXT,
            tsx_code TEXT,
            screenshot_path TEXT,
            embedding_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS compatibility (
            component_id TEXT NOT NULL,
            compatible_component_id TEXT NOT NULL,
            score REAL DEFAULT 0.0,
            PRIMARY KEY (component_id, compatible_component_id),
            FOREIGN KEY (component_id) REFERENCES components(id),
            FOREIGN KEY (compatible_component_id) REFERENCES components(id)
        );

        CREATE INDEX IF NOT EXISTS idx_components_library ON components(source_library);
        CREATE INDEX IF NOT EXISTS idx_components_type ON components(component_type);
    """)
    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a Row to a dict, parsing JSON fields."""
    d = dict(row)
    for field in ("tags", "styles", "dependencies"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


# ---------------------------------------------------------------------------
# Components CRUD
# ---------------------------------------------------------------------------

def insert_component(component: dict) -> str:
    """Insert a component. Returns the component id."""
    conn = _get_connection()
    # Serialize list fields to JSON
    data = dict(component)
    for field in ("tags", "styles", "dependencies"):
        if isinstance(data.get(field), (list, dict)):
            data[field] = json.dumps(data[field])

    conn.execute("""
        INSERT OR REPLACE INTO components
        (id, name, source_library, source_url, component_type, description,
         tags, styles, dependencies, install_command, tsx_code,
         screenshot_path, embedding_text, created_at)
        VALUES (:id, :name, :source_library, :source_url, :component_type,
                :description, :tags, :styles, :dependencies, :install_command,
                :tsx_code, :screenshot_path, :embedding_text, :created_at)
    """, {
        "id": data.get("id"),
        "name": data.get("name"),
        "source_library": data.get("source_library"),
        "source_url": data.get("source_url"),
        "component_type": data.get("component_type"),
        "description": data.get("description"),
        "tags": data.get("tags"),
        "styles": data.get("styles"),
        "dependencies": data.get("dependencies"),
        "install_command": data.get("install_command"),
        "tsx_code": data.get("tsx_code"),
        "screenshot_path": data.get("screenshot_path"),
        "embedding_text": data.get("embedding_text"),
        "created_at": data.get("created_at", datetime.utcnow().isoformat()),
    })
    conn.commit()
    conn.close()
    return data["id"]


def get_component(component_id: str) -> Optional[dict]:
    """Get a single component by id."""
    conn = _get_connection()
    row = conn.execute("SELECT * FROM components WHERE id = ?", (component_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_all_components(limit: int = 100, offset: int = 0) -> list[dict]:
    """List all components with pagination."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM components ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_components_by_tags(tags: list[str], limit: int = 20) -> list[dict]:
    """Search components whose tags overlap with the given tag list."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM components").fetchall()
    conn.close()

    results = []
    search_tags = {t.lower() for t in tags}
    for row in rows:
        d = _row_to_dict(row)
        component_tags = set()
        if isinstance(d.get("tags"), list):
            component_tags = {t.lower() for t in d["tags"]}
        if isinstance(d.get("styles"), list):
            component_tags |= {t.lower() for t in d["styles"]}

        overlap = len(search_tags & component_tags)
        if overlap > 0:
            results.append({"component": d, "score": overlap})

    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["component"] for r in results[:limit]]


def get_components_by_library(library: str) -> list[dict]:
    """Get all components from a specific library."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM components WHERE source_library = ?", (library,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def delete_component(component_id: str) -> bool:
    """Delete a component and its compatibility entries."""
    conn = _get_connection()
    conn.execute("DELETE FROM compatibility WHERE component_id = ? OR compatible_component_id = ?",
                 (component_id, component_id))
    cursor = conn.execute("DELETE FROM components WHERE id = ?", (component_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ---------------------------------------------------------------------------
# Compatibility CRUD
# ---------------------------------------------------------------------------

def insert_compatibility(component_id: str, compatible_id: str, score: float):
    """Insert a compatibility relationship."""
    conn = _get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO compatibility (component_id, compatible_component_id, score)
        VALUES (?, ?, ?)
    """, (component_id, compatible_id, score))
    conn.commit()
    conn.close()


def get_compatible_components(component_id: str, min_score: float = 0.5) -> list[dict]:
    """Get components compatible with a given component."""
    conn = _get_connection()
    rows = conn.execute("""
        SELECT c.*, comp.score
        FROM compatibility comp
        JOIN components c ON c.id = comp.compatible_component_id
        WHERE comp.component_id = ? AND comp.score >= ?
        ORDER BY comp.score DESC
    """, (component_id, min_score)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

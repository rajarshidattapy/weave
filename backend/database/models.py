"""
SQLite database models and CRUD operations for Weave component storage.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "weave.db")

# JSON fields that must be serialized/deserialized
JSON_FIELDS = (
    "tags", "styles", "dependencies", "imports", "props", "variants",
    "examples", "code_blocks", "preview_images", "accessibility",
    "styling", "composition", "related_components", "framework_compatibility",
    "animation_libs", "installation",
)


def _get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist, then migrate for new columns."""
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
    _migrate_db()


def _migrate_db():
    """Add new columns to existing database without dropping data."""
    new_columns = [
        ("slug", "TEXT"),
        ("category", "TEXT"),
        ("installation", "TEXT"),
        ("imports", "TEXT"),
        ("props", "TEXT"),
        ("variants", "TEXT"),
        ("examples", "TEXT"),
        ("code_blocks", "TEXT"),
        ("preview_images", "TEXT"),
        ("accessibility", "TEXT"),
        ("styling", "TEXT"),
        ("composition", "TEXT"),
        ("related_components", "TEXT"),
        ("framework_compatibility", "TEXT"),
        ("animation_libs", "TEXT"),
    ]
    conn = _get_connection()
    for col_name, col_type in new_columns:
        try:
            conn.execute(f"ALTER TABLE components ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a Row to a dict, deserializing all JSON fields."""
    d = dict(row)
    for field in JSON_FIELDS:
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
    """Insert or replace a component. Returns the component id."""
    conn = _get_connection()
    data = dict(component)
    for field in JSON_FIELDS:
        if isinstance(data.get(field), (list, dict)):
            data[field] = json.dumps(data[field])

    conn.execute("""
        INSERT OR REPLACE INTO components
        (id, name, source_library, source_url, component_type, description,
         tags, styles, dependencies, install_command, tsx_code,
         screenshot_path, embedding_text, created_at,
         slug, category, installation, imports, props, variants, examples,
         code_blocks, preview_images, accessibility, styling, composition,
         related_components, framework_compatibility, animation_libs)
        VALUES
        (:id, :name, :source_library, :source_url, :component_type, :description,
         :tags, :styles, :dependencies, :install_command, :tsx_code,
         :screenshot_path, :embedding_text, :created_at,
         :slug, :category, :installation, :imports, :props, :variants, :examples,
         :code_blocks, :preview_images, :accessibility, :styling, :composition,
         :related_components, :framework_compatibility, :animation_libs)
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
        "slug": data.get("slug"),
        "category": data.get("category"),
        "installation": data.get("installation"),
        "imports": data.get("imports"),
        "props": data.get("props"),
        "variants": data.get("variants"),
        "examples": data.get("examples"),
        "code_blocks": data.get("code_blocks"),
        "preview_images": data.get("preview_images"),
        "accessibility": data.get("accessibility"),
        "styling": data.get("styling"),
        "composition": data.get("composition"),
        "related_components": data.get("related_components"),
        "framework_compatibility": data.get("framework_compatibility"),
        "animation_libs": data.get("animation_libs"),
    })
    conn.commit()
    conn.close()
    return data["id"]


def component_exists_by_url(url: str) -> bool:
    """Check if a component with this source_url is already in the DB."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT id FROM components WHERE source_url = ?", (url,)
    ).fetchone()
    conn.close()
    return row is not None


def get_component(component_id: str) -> Optional[dict]:
    conn = _get_connection()
    row = conn.execute("SELECT * FROM components WHERE id = ?", (component_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_all_components(limit: int = 100, offset: int = 0) -> list[dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM components ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_components_by_tags(tags: list[str], limit: int = 20) -> list[dict]:
    """Search components by tag overlap across tags, styles, and category."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM components").fetchall()
    conn.close()

    search_tags = {t.lower() for t in tags}
    results = []
    for row in rows:
        d = _row_to_dict(row)
        component_tags: set[str] = set()
        for field in ("tags", "styles"):
            val = d.get(field)
            if isinstance(val, list):
                component_tags |= {t.lower() for t in val}
        if d.get("category"):
            component_tags.add(d["category"].lower())
        if d.get("component_type"):
            component_tags.add(d["component_type"].lower())

        overlap = len(search_tags & component_tags)
        if overlap > 0:
            results.append({"component": d, "score": overlap})

    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["component"] for r in results[:limit]]


def search_components_by_text(query: str, limit: int = 20) -> list[dict]:
    """Full-text search across name, description, category, slug, source_library."""
    conn = _get_connection()
    like = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM components
        WHERE name LIKE ?
           OR description LIKE ?
           OR category LIKE ?
           OR slug LIKE ?
           OR source_library LIKE ?
           OR component_type LIKE ?
        ORDER BY
            CASE WHEN name LIKE ? THEN 0 ELSE 1 END,
            created_at DESC
        LIMIT ?
    """, (like, like, like, like, like, like, like, limit)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_components_by_library(library: str) -> list[dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM components WHERE source_library = ?", (library,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def delete_component(component_id: str) -> bool:
    conn = _get_connection()
    conn.execute(
        "DELETE FROM compatibility WHERE component_id = ? OR compatible_component_id = ?",
        (component_id, component_id),
    )
    cursor = conn.execute("DELETE FROM components WHERE id = ?", (component_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ---------------------------------------------------------------------------
# Compatibility CRUD
# ---------------------------------------------------------------------------

def insert_compatibility(component_id: str, compatible_id: str, score: float):
    conn = _get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO compatibility (component_id, compatible_component_id, score)
        VALUES (?, ?, ?)
    """, (component_id, compatible_id, score))
    conn.commit()
    conn.close()


def get_compatible_components(component_id: str, min_score: float = 0.5) -> list[dict]:
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

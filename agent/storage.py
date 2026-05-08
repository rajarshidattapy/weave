"""
Local storage utilities for component data.
"""

import json
import os
from pathlib import Path
from typing import List
from models import Component


def ensure_data_dirs():
    """Create necessary data directories if they don't exist."""
    Path("data/screenshots").mkdir(parents=True, exist_ok=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)


def load_components() -> List[Component]:
    """Load existing components from storage."""
    ensure_data_dirs()
    
    db_path = "data/components.json"
    
    if not os.path.exists(db_path):
        return []
    
    try:
        with open(db_path, "r") as f:
            data = json.load(f)
            return [Component(**item) for item in data]
    except Exception as e:
        print(f"Warning: Could not load components database: {e}")
        return []


def save_components(components: List[Component]):
    """
    Save components to local JSON database.
    
    Args:
        components: List of Component objects to save
    """
    ensure_data_dirs()
    
    db_path = "data/components.json"
    
    try:
        with open(db_path, "w") as f:
            json.dump(
                [c.model_dump() for c in components],
                f,
                indent=2
            )
        print(f"✓ Saved {len(components)} components to {db_path}")
    except Exception as e:
        print(f"✗ Error saving components: {e}")


def save_component(component: Component):
    """
    Append a single component to the database.
    
    Args:
        component: Component object to save
    """
    components = load_components()
    
    # Avoid duplicates
    existing_ids = {c.id for c in components}
    
    if component.id not in existing_ids:
        components.append(component)
        save_components(components)
    else:
        print(f"⊘ Component {component.id} already exists, skipping")


def save_raw_html(component_name: str, html: str):
    """Save raw HTML for debugging."""
    ensure_data_dirs()
    
    path = f"data/raw/{component_name}.html"
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"Warning: Could not save raw HTML for {component_name}: {e}")

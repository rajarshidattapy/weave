"""
Pydantic models for component data structures.
"""

from pydantic import BaseModel
from typing import Optional, List


class ComponentMetadata(BaseModel):
    component_type: str
    style: List[str]
    complexity: int  # 0=simple, 1=medium, 2=complex
    description: str


class Component(BaseModel):
    id: str
    name: str
    source: str
    url: str
    code: List[str]
    screenshot: Optional[str] = None
    metadata: Optional[ComponentMetadata] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "button",
                "name": "Button",
                "source": "shadcn",
                "url": "https://ui.shadcn.com/docs/components/button",
                "code": ["<Button>Click me</Button>"],
                "screenshot": "data/screenshots/button.png",
                "metadata": {
                    "component_type": "primitive",
                    "style": ["unstyled"],
                    "complexity": 0,
                    "description": "A button component"
                }
            }
        }

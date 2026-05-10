"""
Pydantic models for Weave API request/response bodies.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class RetrieveRequest(BaseModel):
    """POST /retrieve — semantic component search."""
    prompt: str = Field(..., description="Natural language prompt, e.g. 'beautiful AI hero section'")


class InjectRequest(BaseModel):
    """POST /inject — inject a component into the sandbox."""
    component_id: str = Field(..., description="ID of the component to inject")
    target_file: str = Field(
        default="app/page.tsx",
        description="Relative path inside test-next/ to inject into",
    )


class IndexLibraryRequest(BaseModel):
    """POST /index-library — crawl and index a component library."""
    url: str = Field(..., description="Base URL of the component library")
    library_name: Optional[str] = Field(None, description="Human-friendly name for the library")


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class ComponentResponse(BaseModel):
    """A single component in API responses."""
    id: str
    name: str
    source_library: Optional[str] = None
    source_url: Optional[str] = None
    component_type: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    styles: Optional[list[str]] = None
    dependencies: Optional[list[str]] = None
    install_command: Optional[str] = None
    tsx_code: Optional[str] = None
    screenshot_path: Optional[str] = None
    created_at: Optional[str] = None


class RetrieveResponse(BaseModel):
    """POST /retrieve response."""
    prompt: str
    components: list[ComponentResponse] = []
    expanded_tags: list[str] = []


class InjectResponse(BaseModel):
    """POST /inject response."""
    success: bool
    component_id: str
    modified_files: list[str] = []
    installed_deps: list[str] = []
    error: Optional[str] = None


class IndexLibraryResponse(BaseModel):
    """POST /index-library response."""
    library: str
    discovered_urls: int = 0
    indexed_components: int = 0
    errors: list[str] = []

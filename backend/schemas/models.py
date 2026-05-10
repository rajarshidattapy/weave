"""
Pydantic models for Weave API request/response bodies.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class RetrieveRequest(BaseModel):
    prompt: str = Field(..., description="Natural language prompt, e.g. 'beautiful AI hero section'")
    context: Optional[str] = Field(None, description="Sandbox context: components already in use")


class InjectRequest(BaseModel):
    component_id: str = Field(..., description="ID of the component to inject")
    target_file: str = Field(
        default="app/page.tsx",
        description="Relative path inside test-next/ to inject into",
    )


class IndexLibraryRequest(BaseModel):
    url: str = Field(..., description="Base URL of the component library")
    library_name: Optional[str] = Field(None, description="Human-friendly name for the library")


# ---------------------------------------------------------------------------
# Sub-models for the rich component schema
# ---------------------------------------------------------------------------

class InstallationInfo(BaseModel):
    cli: list[str] = []
    npm: list[str] = []
    registry: list[str] = []


class StylingInfo(BaseModel):
    tailwind: bool = False
    css_in_js: bool = False
    radix: bool = False
    motion: bool = False


class CompositionInfo(BaseModel):
    primitive: bool = False
    composite: bool = False
    wrapper: bool = False


class PropDefinition(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    default: Optional[str] = None
    required: Optional[bool] = None
    description: Optional[str] = None


class VariantDefinition(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CodeExample(BaseModel):
    label: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None


class CodeBlock(BaseModel):
    type: Optional[str] = None   # component|demo|install|config|import|utility
    language: Optional[str] = None
    content: Optional[str] = None
    label: Optional[str] = None


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class ComponentResponse(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    category: Optional[str] = None
    source_library: Optional[str] = None
    source_url: Optional[str] = None
    component_type: Optional[str] = None
    description: Optional[str] = None
    # Installation
    installation: Optional[Any] = None
    install_command: Optional[str] = None
    # Code
    dependencies: Optional[list[str]] = None
    imports: Optional[list[str]] = None
    tsx_code: Optional[str] = None
    code_blocks: Optional[list[Any]] = None
    # API
    props: Optional[list[Any]] = None
    variants: Optional[list[Any]] = None
    examples: Optional[list[Any]] = None
    # Docs
    accessibility: Optional[list[str]] = None
    preview_images: Optional[list[str]] = None
    related_components: Optional[list[str]] = None
    framework_compatibility: Optional[list[str]] = None
    animation_libs: Optional[list[str]] = None
    # Classification
    styling: Optional[Any] = None
    composition: Optional[Any] = None
    # Legacy
    tags: Optional[list[str]] = None
    styles: Optional[list[str]] = None
    screenshot_path: Optional[str] = None
    created_at: Optional[str] = None


class RetrieveResponse(BaseModel):
    prompt: str
    components: list[ComponentResponse] = []
    expanded_tags: list[str] = []


class InjectResponse(BaseModel):
    success: bool
    component_id: str
    modified_files: list[str] = []
    installed_deps: list[str] = []
    error: Optional[str] = None


class IndexLibraryResponse(BaseModel):
    library: str
    discovered_urls: int = 0
    indexed_components: int = 0
    errors: list[str] = []


class GraphResponse(BaseModel):
    generated_at: str
    component_count: int
    dependency_graph: dict = {}
    composition_graph: dict = {}
    wrapper_graph: dict = {}
    library_lineage: dict = {}


class IntegrateRequest(BaseModel):
    component_id: str = Field(..., description="ID of the component to integrate")
    target_file: str = Field(default="app/page.tsx")


class IntegrateResponse(BaseModel):
    success: bool
    component_id: str
    files_created: list[str] = []
    imports_added: list[str] = []
    jsx_injected: list[str] = []
    dependencies_installed: list[str] = []
    build_errors: list[Any] = []
    fixes_applied: int = 0
    error: Optional[str] = None


class FixErrorRequest(BaseModel):
    error: str = Field(..., description="Pasted error text / stack trace to fix")


class FixErrorResponse(BaseModel):
    success: bool
    patches: list[Any] = []
    error: Optional[str] = None


class SuggestRequest(BaseModel):
    context: str = Field(..., description="Sandbox context string from getSandboxContext()")
    limit: int = Field(default=5, ge=1, le=10)


class SuggestionItem(BaseModel):
    title: str
    description: str
    search_query: str
    top_component: Optional[Any] = None


class SuggestResponse(BaseModel):
    suggestions: list[SuggestionItem] = []

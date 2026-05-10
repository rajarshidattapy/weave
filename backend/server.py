"""
Weave Backend Server — FastAPI + WebSocket.

REST Endpoints:
  POST /retrieve         — semantic component search
  POST /inject           — inject component into test-next
  POST /index-library    — crawl + index a component library
  GET  /components       — list all indexed components
  GET  /components/{id}  — get single component

WebSocket:
  ws://localhost:8000/ws  — bidirectional real-time events
"""
import asyncio
import json
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from database.models import init_db, get_all_components, get_component
from schemas.models import (
    RetrieveRequest, RetrieveResponse,
    InjectRequest, InjectResponse,
    IndexLibraryRequest, IndexLibraryResponse,
    ComponentResponse, GraphResponse,
)
from agents.retrieval import retrieve_components
from agents.injection import inject_component
from agents.discovery import discover_components
from agents.extraction import extract_component
from agents.metadata import generate_metadata
from agents.compatibility import compute_compatibility
from agents.graph import generate_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

app = FastAPI(
    title="Weave Agent System",
    description="Agentic frontend retrieval + composition engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# WebSocket connection manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"service": "Weave Agent System", "status": "running"}


@app.post("/retrieve", response_model=RetrieveResponse)
async def api_retrieve(req: RetrieveRequest):
    """Semantic component retrieval."""
    result = await asyncio.to_thread(retrieve_components, req.prompt, context=req.context)
    components = [ComponentResponse(**c) for c in result["components"]]
    return RetrieveResponse(
        prompt=req.prompt,
        components=components,
        expanded_tags=result["expanded_tags"],
    )


@app.post("/inject", response_model=InjectResponse)
async def api_inject(req: InjectRequest):
    """Inject a component into the sandbox."""
    result = await asyncio.to_thread(inject_component, req.component_id, req.target_file)
    resp = InjectResponse(component_id=req.component_id, **result)
    await manager.broadcast({"type": "injection_complete", "data": resp.model_dump()})
    return resp


@app.post("/index-library", response_model=IndexLibraryResponse)
async def api_index_library(req: IndexLibraryRequest):
    """Crawl and index a component library."""
    library_name = req.library_name or _extract_library_name(req.url)
    errors = []

    # Step 1: Discover component URLs
    urls = await asyncio.to_thread(discover_components, library_name, req.url)
    await manager.broadcast({"type": "indexing_progress", "phase": "discovery", "count": len(urls)})

    # Step 2: Extract and store each component
    indexed = 0
    for url in urls:
        try:
            component_data = await asyncio.to_thread(extract_component, url, library_name)
            if not component_data:
                continue

            # Generate metadata tags
            meta = await asyncio.to_thread(
                generate_metadata,
                component_data.get("name", ""),
                component_data.get("tsx_code", ""),
                component_data.get("description", ""),
            )
            component_data.update({
                "tags": meta.get("tags", []),
                "styles": meta.get("styles", []),
                "embedding_text": meta.get("embedding_text", ""),
            })

            # Store in DB
            from database.models import insert_component
            insert_component(component_data)
            indexed += 1

            await manager.broadcast({
                "type": "indexing_progress",
                "phase": "extraction",
                "current": indexed,
                "total": len(urls),
                "component": component_data.get("name"),
            })

        except Exception as e:
            errors.append(f"{url}: {str(e)}")

    # Step 3: Compute compatibility (background)
    if indexed > 0:
        all_comps = get_all_components(limit=50)
        for comp in all_comps[-indexed:]:
            try:
                await asyncio.to_thread(compute_compatibility, comp)
            except Exception:
                pass

    return IndexLibraryResponse(
        library=library_name,
        discovered_urls=len(urls),
        indexed_components=indexed,
        errors=errors,
    )


@app.get("/components")
async def api_list_components(limit: int = 100, offset: int = 0):
    """List all indexed components."""
    components = get_all_components(limit=limit, offset=offset)
    return {"components": components, "count": len(components)}


@app.get("/graph")
async def api_graph(library: str = None):
    """Generate and return the component relationship graph."""
    graph = await asyncio.to_thread(generate_graph, library)
    return graph


@app.get("/components/{component_id}")
async def api_get_component(component_id: str):
    """Get a single component by ID."""
    component = get_component(component_id)
    if not component:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Component not found")
    return component


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "retrieve_components":
                result = await asyncio.to_thread(retrieve_components, data.get("prompt", ""))
                await ws.send_json({"type": "retrieval_results", "components": result["components"], "tags": result["expanded_tags"]})

            elif msg_type == "inject_component":
                result = await asyncio.to_thread(inject_component, data.get("component_id", ""), data.get("target_file", "app/page.tsx"))
                await ws.send_json({"type": "injection_complete", "data": result})

            else:
                await ws.send_json({"type": "error", "message": f"Unknown event: {msg_type}"})

    except WebSocketDisconnect:
        manager.disconnect(ws)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_library_name(url: str) -> str:
    """Extract a friendly library name from a URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    parts = parsed.netloc.replace("www.", "").split(".")
    return parts[-2].capitalize() if len(parts) >= 2 else parts[0].capitalize()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

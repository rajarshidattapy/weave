# Weave Agent System PRD

## Repository Structure

Current structure:

```txt id="7m0v4n"
weave/
│
├── backend/        → Google ADK agents + scraping + retrieval
├── ui/             → Main frontend IDE
├── test-next/      → Next.js sandbox runtime
│
├── README.md
└── .gitignore
```

---

# System Objective

The backend agent system is responsible for:

1. scraping component libraries
2. extracting usable frontend components
3. classifying and tagging components
4. storing components in SQLite
5. retrieving compatible components
6. injecting components into the live sandbox
7. modifying the running Next.js project safely

The backend is NOT:

* a generic AI backend
* a chatbot
* a workflow engine
* a website generator

It is specifically:

```txt id="t1x7j5"
an agentic frontend retrieval + composition engine
```

---

# Backend Responsibilities

The backend must handle:

```txt id="4n1q9k"
component discovery
component extraction
metadata enrichment
semantic tagging
compatibility classification
retrieval
runtime injection
sandbox communication
```

---

# Core Backend Stack

## AI Orchestration

```txt id="5y6v3c"
Google ADK
Open AI API
```

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o"),
    name="weave_agent",
    instruction="You are a frontend retrieval agent."
)

---

## Scraping

```txt id="z9j8r2"
Anakin SDK
Anakin ADK toolkit
Playwright
```

---

## Runtime Modification

```txt id="8d4m0s"
AST transforms
ts-morph
babel/parser
```

---

## Database

```txt id="6u7p2w"
SQLite
```

---

## Communication

```txt id="3b8n1x"
WebSocket
```

Frontend ↔ backend live communication.

---

# Backend Folder Structure

## Final Recommended Structure

```txt id="0x3v7l"
backend/
│
├── agents/
│   ├── discovery/
│   ├── extraction/
│   ├── metadata/
│   ├── retrieval/
│   ├── injection/
│   └── compatibility/
│
├── runtime/
│   ├── sandbox/
│   ├── websocket/
│   └── ast/
│
├── database/
│   ├── sqlite/
│   └── migrations/
│
├── storage/
│   ├── screenshots/
│   ├── raw/
│   └── embeddings/
│
├── prompts/
├── tools/
├── schemas/
├── utils/
│
├── adk.py
├── requirements.txt
└── .env
```

---

# Agent Architecture

You should NOT create:

```txt id="7v2k6m"
50 autonomous agents
```

You need:

```txt id="m9q4e1"
small specialized deterministic agents
```

---

# Required Agents

---

# 1. Discovery Agent

## Responsibilities

Discover:

* component pages
* category pages
* installation pages
* example pages

---

## Inputs

```json id="3j5x8d"
{
  "library": "Aceternity UI",
  "url": "https://ui.aceternity.com"
}
```

---

## Outputs

```json id="0k9t2w"
{
  "component_urls": []
}
```

---

## Internal Logic

Use:

```python id="y7n4f1"
client.map()
```

OR:

```txt id="j5w2u8"
llms-full.txt
```

first before crawling.

---

## Important

Discovery agent should:

* normalize URLs
* remove duplicates
* remove invalid routes
* remove docs-only pages

---

# 2. Extraction Agent

## Responsibilities

Extract:

* component code
* dependencies
* install instructions
* preview screenshots
* markdown/docs

---

## Tools

Use:

```txt id="5f0n2m"
Anakin scrape API
```

with:

```python id="7h2v1z"
use_browser=True
```

for JS-heavy sites.

---

## Extraction Output

```json id="x1v4e9"
{
  "name": "Animated Hero",
  "tsx": "...",
  "dependencies": [],
  "install": "...",
  "raw_docs": "..."
}
```

---

# 3. Metadata Agent

## Responsibilities

Generate:

* semantic tags
* design tags
* style tags
* usage tags
* compatibility hints

---

## Required Tags

### Semantic

```txt id="7x6f0j"
hero
pricing
footer
cta
navbar
dashboard
```

---

### Visual

```txt id="0c4k8m"
glassmorphism
bento
minimal
animated
dark
gradient
retro
modern
```

---

### Usage

```txt id="8w2y6n"
ai-startup
portfolio
landing-page
saas
dashboard
```

---

### Technical

```txt id="1e9q7r"
framer-motion
threejs
tailwind
shadcn
radix
```

---

# 4. Compatibility Agent

## Responsibilities

Generate:

```txt id="4f8j2u"
component compatibility intelligence
```

---

## Example

```json id="2n5v7s"
{
  "component": "animated-hero",
  "compatible_with": [
    "bento-grid",
    "glass-footer"
  ]
}
```

---

## Compatibility Logic

Use:

* style overlap
* animation overlap
* spacing density
* theme compatibility
* semantic pairing

---

# 5. Storage Agent

## Responsibilities

Store:

* component metadata
* screenshots
* embeddings
* raw code
* compatibility graph

---

# SQLite Schema

## components

```sql id="5m0v9q"
CREATE TABLE components (
    id TEXT PRIMARY KEY,
    name TEXT,
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
```

---

## compatibility

```sql id="8p1z6t"
CREATE TABLE compatibility (
    component_id TEXT,
    compatible_component_id TEXT,
    score REAL
);
```

---

# 6. Retrieval Agent

## Responsibilities

Convert prompts like:

```txt id="6v4k0x"
add shiny AI pricing section
```

into:

```txt id="9x1r3w"
semantic component retrieval
```

---

## Retrieval Pipeline

```txt id="4d7j2m"
prompt
↓
prompt analysis
↓
tag expansion
↓
embedding retrieval
↓
compatibility ranking
↓
final component list
```

---

## Retrieval Filters

### Semantic

```txt id="2m8c5v"
hero
pricing
cta
```

---

### Visual

```txt id="1j4z7n"
dark
minimal
animated
```

---

### Technical

```txt id="6f2x8k"
tailwind
framer-motion
```

---

# Runtime Integration System

This is the MOST IMPORTANT PART.

---

# Runtime Target

The runtime target is:

```txt id="9q5v3f"
test-next/
```

This is the active editable sandbox.

---

# Injection Agent

## Responsibilities

Modify:

```txt id="7b1m8z"
test-next/
```

in real-time.

---

## Required Actions

### 1. Create component file

Example:

```txt id="5x2f7j"
components/hero.tsx
```

---

### 2. Install dependencies

Example:

```bash id="8m6t1q"
npm install framer-motion
```

---

### 3. Inject imports

Modify:

```txt id="4r9v2k"
app/page.tsx
```

---

### 4. Inject JSX safely

DO NOT:

```txt id="0n6w3p"
string replace blindly
```

Use:

```txt id="1c7z4m"
AST transforms
```

---

# AST System

Use:

```txt id="3j0v8n"
ts-morph
```

for:

* import injection
* JSX insertion
* component replacement

---

# Runtime Communication

## Frontend ↔ Backend

Use:

```txt id="8u2f5d"
WebSocket
```

---

## Events

### Frontend → Backend

```json id="5n4z9j"
{
  "type": "retrieve_components",
  "prompt": "beautify hero section"
}
```

---

### Backend → Frontend

```json id="2r8v6m"
{
  "type": "retrieval_results",
  "components": []
}
```

---

### Injection Event

```json id="0w3x7q"
{
  "type": "inject_component",
  "component_id": "hero_001"
}
```

---

# WebContainer Integration

Frontend handles:

* runtime rendering
* iframe
* terminal
* live preview

Backend handles:

* filesystem modifications
* injection instructions
* dependency management

---

# Backend Runtime APIs

Required APIs:

---

## Retrieval API

```txt id="5t1n8x"
POST /retrieve
```

Input:

```json id="6v7m0k"
{
  "prompt": "beautiful AI hero section"
}
```

---

## Injection API

```txt id="9p2w5r"
POST /inject
```

Input:

```json id="1m4k7z"
{
  "component_id": "hero_001"
}
```

---

## Index API

```txt id="0r8f2v"
POST /index-library
```

Input:

```json id="7y3x1n"
{
  "url": "https://ui.aceternity.com"
}
```

---

# Prompt Handling

The agent should NEVER:

```txt id="5f8m2v"
generate raw UI from scratch first
```

Always:

```txt id="4w9z7q"
retrieve existing curated components first
```

Generation only adapts retrieved code.

---

# Important Engineering Rules

---

# DO NOT

```txt id="6n3v1k"
build fully autonomous loops
```

---

# DO NOT

```txt id="2j8m4f"
let agents edit arbitrary files
```

Restrict to:

```txt id="9x7q1v"
test-next/app/
test-next/components/
```

---

# DO NOT

```txt id="1v5m8r"
trust LLM-generated imports blindly
```

Validate:

* dependencies
* imports
* paths

---

# DO

```txt id="8q4n2w"
store raw extraction data
```

Always.

---

# DO

```txt id="3m7k1x"
keep agent outputs deterministic
```

---

# DO

```txt id="6z0f9v"
separate retrieval from injection
```

Very important.

---

# Initial Milestones

---

# Milestone 1

## Goal

Index:

* shadcn
* Aceternity
* Magic UI

Store:

* metadata
* code
* screenshots

---

# Milestone 2

## Goal

Semantic retrieval working.

Example:

```txt id="2x6j0m"
beautiful AI pricing section
```

returns useful results.

---

# Milestone 3

## Goal

Inject retrieved component into:

```txt id="5v1n7k"
test-next
```

live.

---

# Milestone 4

## Goal

Compatibility-aware retrieval.

Example:

```txt id="0m8z2q"
find pricing section matching existing hero
```

---

# Final System Definition

The backend is:

```txt id="4k7x9m"
a deterministic frontend composition runtime
```

NOT:

```txt id="8f1v6n"
a generic AI app builder
```

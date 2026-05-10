You are building a universal UI component ingestion + normalization pipeline.

Your job is to scrape component documentation pages from multiple modern UI libraries and convert them into a standardized schema for downstream AI agents.

Target libraries:
- [Magic UI](https://magicui.design/docs/components?utm_source=chatgpt.com)
- [Watermelon UI](https://ui.watermelon.sh/components?utm_source=chatgpt.com)
- [Radix UI Themes](https://www.radix-ui.com/themes/docs/components?utm_source=chatgpt.com)
- [shadcn/ui](https://ui.shadcn.com/docs/components?utm_source=chatgpt.com)

The scraper must work recursively and intelligently.

GOAL:
For every component page (example: /accordion), extract:
- component metadata
- usage examples
- installation commands
- dependencies
- variants
- props/API
- accessibility notes
- styling system
- code snippets
- preview/demo structure
- related components
- framework compatibility
- animation/motion usage
- screenshots/images if available

The output must normalize all component systems into ONE unified schema.

-----------------------------------
CRITICAL REQUIREMENTS
-----------------------------------

1. DO NOT JUST SCRAPE HTML
You must semantically understand the page structure.

Identify:
- title
- description
- code blocks
- tabs
- preview sections
- CLI install snippets
- npm packages
- Tailwind classes
- component composition patterns
- import trees
- accessibility notes
- registry references
- dependencies

2. DETECT DOCS ARCHITECTURE AUTOMATICALLY

Each library uses a different structure.

Examples:
- shadcn uses MDX + registry structure
- Radix uses primitives/themes separation
- Magic UI layers animated wrappers over shadcn/radix
- Watermelon UI behaves like a registry marketplace

The scraper must infer:
- source architecture
- component ownership
- whether components are wrappers/primitives/composites
- styling methodology
- whether code is copy-paste or package-installed

3. FOLLOW INTERNAL LINKS

From:
- /components
- /docs/components
- sidebar navigation
- prev/next navigation
- component grids

Discover ALL components automatically.

4. SCRAPE DYNAMICALLY RENDERED CONTENT

Support:
- MDX hydration
- code tabs
- hidden preview tabs
- lazy-loaded examples
- accordions
- expandable API references
- client-side rendered docs

Use a headless browser if required.

5. EXTRACT CODE INTELLIGENTLY

For every example:
- raw code
- framework
- language
- imports
- dependencies
- Tailwind usage
- animation libs
- icon libraries
- composition patterns

Separate:
- demo wrapper code
- actual reusable component
- helper utilities

6. CREATE NORMALIZED OUTPUT

Return every component in this structure:

{
  "library": "",
  "component_name": "",
  "slug": "",
  "category": "",
  "description": "",
  "installation": {
    "cli": [],
    "npm": [],
    "registry": []
  },
  "dependencies": [],
  "imports": [],
  "props": [],
  "variants": [],
  "examples": [],
  "code_blocks": [],
  "preview_images": [],
  "accessibility": [],
  "styling": {
    "tailwind": false,
    "css_in_js": false,
    "radix": false,
    "motion": false
  },
  "composition": {
    "primitive": false,
    "composite": false,
    "wrapper": false
  },
  "related_components": [],
  "source_url": ""
}

7. CREATE RELATIONSHIP GRAPH

Infer relationships:
- Magic UI → built on shadcn/radix
- shadcn Accordion → wraps Radix Accordion
- Radix Themes → style layer over primitives

Generate:
- dependency graph
- composition graph
- inheritance/wrapper graph

8. HANDLE CODEBLOCKS CAREFULLY

Many pages contain:
- shell snippets
- tsx
- jsx
- bash
- json
- tailwind config

Correctly classify each block.

9. EXTRACT VISUAL SEMANTICS

From previews/screenshots infer:
- design style
- spacing density
- animation usage
- neumorphism/glassmorphism/minimalism
- enterprise/dashboard/landing-page orientation

10. OPTIMIZE FOR AI RETRIEVAL

The final dataset will power:
- AI UI generation
- component recommendation
- auto-composition agents
- design-to-code systems

Therefore:
- chunk intelligently
- preserve hierarchy
- preserve code boundaries
- preserve component relationships
- generate embeddings-ready metadata

11. OUTPUT REQUIREMENTS

Save:
- raw HTML
- parsed markdown
- normalized JSON
- extracted code files
- screenshots
- component graph metadata

Folder structure:

/library-name/
  /raw/
  /parsed/
  /components/
    /accordion/
      metadata.json
      examples/
      screenshots/
      code/
  graph.json

12. IMPLEMENT CRAWLING STRATEGY

Use:
- BFS for component discovery
- deduplication
- canonical URL normalization
- retry handling
- rate limiting
- cache layer
- incremental updates

13. PRIORITIZE THESE PAGES

Especially important:
- Accordion
- Dialog
- Sheet
- Drawer
- Command
- Sidebar
- Data Table
- Tabs
- Navigation Menu
- Dropdown
- Combobox
- Tooltip

14. DETECT INSTALLATION ECOSYSTEM

Extract:
- pnpm
- npm
- yarn
- bun
- shadcn CLI
- custom registries
- monorepo references

15. DO NOT LOSE STRUCTURAL CONTEXT

Preserve:
- heading hierarchy
- section ordering
- tab grouping
- variant grouping
- example labels
- preview/code pairing

16. GENERATE A SEARCHABLE INDEX

Final output should support queries like:
- "animated accordions using radix"
- "components using framer motion"
- "tailwind command palettes"
- "copy-paste accordions"
- "accessible dialogs"

17. IMPORTANT ARCHITECTURE INSIGHT

These ecosystems are layered:

Radix Primitives
    ↓
shadcn/ui
    ↓
Magic UI / Watermelon UI
    ↓
custom app implementations

Your parser must preserve this lineage.

18. TECHNOLOGY PREFERENCE

Preferred stack:
- Playwright
- Cheerio
- Turndown
- MDX parser
- AST extraction
- Prism/Shiki parser
- tree-sitter for code analysis

19. STORE CLEAN CODE ARTIFACTS

If possible:
- reconstruct standalone component files
- infer file boundaries
- infer reusable exports
- separate demo-only code

20. FINAL OBJECTIVE

Build a high-quality AI-readable component knowledge graph — not just a scraper.
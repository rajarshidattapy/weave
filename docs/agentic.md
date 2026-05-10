The current injection system is wrong.

Right now components are only injected into `page.tsx`, but real UI integrations are multi-step and require:

* creating files inside `/components`
* installing dependencies
* fixing imports
* updating Tailwind config
* handling utility files/hooks
* validating builds

Refactor the integration system into an agentic pipeline.

Current structure:

```txt id="k8gjlwm"
ui/
test-next/
backend/
```

Runtime target:

```txt id="fhb7i4"
test-next/
```

New flow:

```txt id="cjlwm0"
retrieve component
→ generate integration plan
→ create files
→ install dependencies
→ inject imports via AST
→ inject JSX safely
→ run build validation
→ auto-fix errors if build fails
```

Create:

```txt id="jlwm11"
backend/runtime/integration/
```

Modules:

```txt id="jlwm12"
planner.py
injector.py
validator.py
fixer.py
dependency_manager.py
ast_manager.py
```

IMPORTANT:

* do NOT use string replace for JSX/imports
* use ts-morph or AST transforms
* support nested component files
* support utility/hooks/lib folders
* support dependency installation automatically
* support self-healing integrations

If runtime/build errors occur:

* analyze stack trace
* patch imports/dependencies/files
* retry automatically

The composition bar should support:

* component retrieval
* UI replacement
* runtime fixing
* pasted error fixing

Examples:

```txt id="jlwm13"
add modern AI hero section
fix this hydration error
replace navbar with glass navbar
```

The system should behave like:
an AI frontend engineer safely modifying a real Next.js codebase.

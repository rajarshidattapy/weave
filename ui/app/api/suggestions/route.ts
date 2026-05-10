import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const BACKEND = process.env.BACKEND_URL || 'http://localhost:8000';

// ---------------------------------------------------------------------------
// FS helpers (same logic as /api/fs but returns flat file map)
// ---------------------------------------------------------------------------

interface FsNode {
  [name: string]: { directory: FsNode } | { file: { contents: string } };
}

async function buildTree(dirPath: string): Promise<FsNode> {
  const tree: FsNode = {};
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      if (['node_modules', '.next', '.git'].includes(entry.name)) continue;
      const full = path.join(dirPath, entry.name);
      if (entry.isDirectory()) {
        tree[entry.name] = { directory: await buildTree(full) };
      } else {
        try {
          tree[entry.name] = { file: { contents: await fs.readFile(full, 'utf-8') } };
        } catch { /* binary – skip */ }
      }
    }
  } catch { /* dir unreadable */ }
  return tree;
}

function flatFiles(tree: FsNode, prefix = ''): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [name, node] of Object.entries(tree)) {
    const p = prefix ? `${prefix}/${name}` : name;
    if ('directory' in node) Object.assign(out, flatFiles(node.directory, p));
    else out[p] = node.file.contents;
  }
  return out;
}

function buildContext(files: Record<string, string>): string {
  const components = new Set<string>();
  const libMap: Record<string, Set<string>> = {};

  for (const [filePath, content] of Object.entries(files)) {
    if (!/\.(tsx|ts|jsx|js)$/.test(filePath)) continue;
    const importRe = /import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]/g;
    let m: RegExpExecArray | null;
    while ((m = importRe.exec(content)) !== null) {
      const from = m[2];
      const names = m[1].split(',').map(n => n.trim().split(/\s+as\s+/)[0].trim()).filter(n => /^[A-Z]/.test(n));
      for (const name of names) {
        components.add(name);
        const lib = from.includes('@/components/ui') || from.includes('shadcn') ? 'shadcn/ui'
          : from.includes('magicui') ? 'Magic UI'
          : from.includes('@radix-ui') ? 'Radix UI'
          : null;
        if (lib) {
          if (!libMap[lib]) libMap[lib] = new Set();
          libMap[lib].add(name);
        }
      }
    }
    const jsxRe = /<([A-Z][A-Za-z0-9]*)/g;
    while ((m = jsxRe.exec(content)) !== null) components.add(m[1]);
  }

  if (components.size === 0) return 'Empty sandbox — no components added yet.';

  const parts: string[] = [];
  const attributed = new Set<string>();
  for (const [lib, names] of Object.entries(libMap)) {
    parts.push(`${[...names].join(', ')} (${lib})`);
    names.forEach(n => attributed.add(n));
  }
  const rest = [...components].filter(n => !attributed.has(n));
  if (rest.length) parts.push(rest.join(', '));
  return `Sandbox already uses: ${parts.join('; ')}`;
}

// ---------------------------------------------------------------------------
// Component matching against backend DB
// ---------------------------------------------------------------------------

interface DBComponent {
  id: string;
  name: string;
  source_library?: string;
  tags?: string[];
  description?: string;
}

async function findTopComponent(query: string, allComponents: DBComponent[]): Promise<DBComponent | null> {
  if (!allComponents.length) return null;
  const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 3);

  // Score each component by tag + name overlap with the query words
  let best: DBComponent | null = null;
  let bestScore = 0;
  for (const c of allComponents) {
    const haystack = [
      c.name,
      ...(c.tags ?? []),
      c.description ?? '',
      c.source_library ?? '',
    ].join(' ').toLowerCase();
    const score = words.filter(w => haystack.includes(w)).length;
    if (score > bestScore) { bestScore = score; best = c; }
  }
  return bestScore > 0 ? best : null;
}

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

export async function POST(req: Request) {
  const { limit = 5 } = await req.json().catch(() => ({}));

  // 1. Build sandbox context from the test-next filesystem
  const basePath = path.resolve(process.cwd(), '../test-next');
  let context = 'Empty sandbox — no components added yet.';
  try {
    await fs.access(basePath);
    const tree = await buildTree(basePath);
    context = buildContext(flatFiles(tree));
  } catch { /* test-next not found */ }

  // 2. Fetch all indexed components from the backend (best-effort)
  let allComponents: DBComponent[] = [];
  try {
    const r = await fetch(`${BACKEND}/components?limit=500`, { signal: AbortSignal.timeout(3000) });
    if (r.ok) {
      const data = await r.json();
      allComponents = data.components ?? [];
    }
  } catch { /* backend not running */ }

  // 3. Ask the LLM for suggestions
  let raw: { title: string; description: string; search_query: string }[] = [];
  try {
    const completion = await client.chat.completions.create({
      model: process.env.MODEL_NAME ?? 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: [
            'You are a senior UI/UX advisor for modern React web apps.',
            'Given a description of components currently in a sandbox,',
            'suggest concrete, actionable improvements the developer can make next.',
            '',
            'Return a JSON object with key "suggestions", an array of objects with:',
            '- title: short imperative phrase (max 6 words)',
            '- description: one sentence explaining why this improves the UI',
            '- search_query: natural language query to find the ideal component',
            '',
            'Rules: focus on what is MISSING or WEAK, be specific, cover variety.',
            `Return exactly ${limit} suggestions ordered by impact.`,
          ].join('\n'),
        },
        { role: 'user', content: `Current sandbox state:\n${context}` },
      ],
      temperature: 0.5,
      response_format: { type: 'json_object' },
    });
    raw = JSON.parse(completion.choices[0].message.content ?? '{}').suggestions ?? [];
  } catch { /* LLM failed */ }

  // 4. Enrich each suggestion with the top matching component
  const suggestions = raw.slice(0, limit).map(s => ({
    title: s.title,
    description: s.description,
    search_query: s.search_query,
    top_component: findTopComponent(s.search_query, allComponents),
  }));

  return NextResponse.json({ suggestions, context });
}

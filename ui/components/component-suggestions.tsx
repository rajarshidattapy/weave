'use client';

import { useApp } from '@/providers/app-context';
import { BackendComponent } from '@/lib/api';
import { motion } from 'framer-motion';
import { Plus, Zap, Loader2, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const SOURCE_COLORS: Record<string, string> = {
  shadcn: 'bg-blue-500/20 text-blue-300',
  'shadcn/ui': 'bg-blue-500/20 text-blue-300',
  radix: 'bg-cyan-500/20 text-cyan-300',
  'radix ui': 'bg-cyan-500/20 text-cyan-300',
  magic: 'bg-pink-500/20 text-pink-300',
  'magic ui': 'bg-pink-500/20 text-pink-300',
  magicui: 'bg-pink-500/20 text-pink-300',
  watermelon: 'bg-red-500/20 text-red-300',
  'watermelon ui': 'bg-red-500/20 text-red-300',
  aceternity: 'bg-purple-500/20 text-purple-300',
};

function sourceColor(lib: string | undefined) {
  if (!lib) return 'bg-white/10 text-white/50';
  const key = lib.toLowerCase();
  for (const [k, v] of Object.entries(SOURCE_COLORS)) {
    if (key.includes(k)) return v;
  }
  return 'bg-white/10 text-white/50';
}

function sourceLabel(lib: string | undefined) {
  if (!lib) return 'unknown';
  // Shorten long names for display
  const map: Record<string, string> = {
    'shadcn/ui': 'shadcn',
    'magic ui': 'magic',
    'radix ui': 'radix',
    'watermelon ui': 'watermelon',
  };
  return map[lib.toLowerCase()] ?? lib;
}

export function ComponentSuggestions() {
  const { searchResults, isSearching, expandedTags, inject, injectingId, prompt } = useApp();

  const handleAdd = async (component: BackendComponent) => {
    toast.loading(`Adding "${component.name}"…`, { id: component.id });
    await inject(component);
    toast.success(`Added "${component.name}" to page`, { id: component.id });
  };

  // Loading skeleton
  if (isSearching) {
    return (
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-white/50 mb-4">
          Components
        </h2>
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-[72px] rounded-xl border border-white/10 bg-white/5 animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  // No results yet / empty prompt
  if (searchResults.length === 0) {
    if (!prompt.trim()) return null;
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center text-white/30">
        <Sparkles className="h-6 w-6 mb-2 opacity-40" />
        <p className="text-sm">No components found.</p>
        <p className="text-xs mt-1">Try a different prompt or add libraries in settings.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-white/50">
          Components
        </h2>
        <span className="text-xs text-white/30">{searchResults.length} found</span>
      </div>

      {/* Expanded tags */}
      {expandedTags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {expandedTags.slice(0, 8).map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-white/5 px-2 py-0.5 text-xs text-white/40"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      <div className="space-y-2">
        {searchResults.map((component, index) => {
          const isInjecting = injectingId === component.id;
          return (
            <motion.div
              key={component.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.04 }}
              whileHover={{ scale: 1.02, translateX: 4 }}
              className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-3 transition-all duration-200 hover:border-white/20 hover:bg-white/10 cursor-pointer"
              onClick={() => !isInjecting && handleAdd(component)}
            >
              <div className="flex items-start gap-3">
                {/* Icon placeholder */}
                <div className="mt-1 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white/5 text-xs font-bold text-white/40 uppercase">
                  {component.name.slice(0, 2)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-sm font-medium text-white truncate">
                      {component.name}
                    </h4>
                    {isInjecting ? (
                      <Loader2 className="h-4 w-4 text-white/60 animate-spin flex-shrink-0" />
                    ) : (
                      <Plus className="h-4 w-4 text-white/40 transition-all duration-200 group-hover:text-white/100 group-hover:scale-110 flex-shrink-0" />
                    )}
                  </div>

                  {component.description && (
                    <p className="mt-0.5 text-xs text-white/40 line-clamp-1">
                      {component.description}
                    </p>
                  )}

                  <div className="mt-2 flex items-center gap-2 flex-wrap">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${sourceColor(
                        component.source_library
                      )}`}
                    >
                      {sourceLabel(component.source_library)}
                    </span>

                    {component.styling?.motion && (
                      <span className="rounded-full bg-orange-500/20 px-2 py-0.5 text-xs font-medium text-orange-300 flex items-center gap-1">
                        <Zap className="h-3 w-3" />
                        animated
                      </span>
                    )}

                    {component.styling?.tailwind && (
                      <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-xs font-medium text-sky-300">
                        tailwind
                      </span>
                    )}
                  </div>

                  {/* Tags from DB metadata */}
                  {(component.tags || []).length > 0 && (
                    <div className="mt-1.5 flex gap-1 flex-wrap">
                      {(component.tags || []).slice(0, 4).map((tag) => (
                        <span key={tag} className="text-xs text-white/30">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

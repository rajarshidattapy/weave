'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, ArrowRight, RefreshCw, Loader2 } from 'lucide-react';
import { Suggestion } from '@/lib/api';
import { useApp } from '@/providers/app-context';

function SkeletonRow() {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 animate-pulse">
      <div className="flex items-center gap-2">
        <div className="h-4 w-4 rounded bg-white/10 shrink-0" />
        <div className="space-y-1.5 flex-1">
          <div className="h-3 w-3/4 rounded bg-white/10" />
          <div className="h-2.5 w-full rounded bg-white/[0.06]" />
        </div>
      </div>
    </div>
  );
}

export function AIRecommendations() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const { search, setPrompt } = useApp();

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await fetch('/api/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 5 }),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data = await res.json();
      setSuggestions(data.suggestions ?? []);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load once on mount
  useEffect(() => {
    load();
  }, [load]);

  const handleClick = (s: Suggestion) => {
    setPrompt(s.search_query);
    search(s.search_query);
  };

  return (
    <div className="space-y-2">
      {/* Refresh control */}
      <div className="flex justify-end mb-1">
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1 text-xs text-white/30 hover:text-white/60 transition-colors disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <RefreshCw className="h-3 w-3" />
          )}
          <span>Refresh</span>
        </button>
      </div>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-2"
          >
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonRow key={i} />
            ))}
          </motion.div>
        ) : error ? (
          <motion.p
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-white/30 text-center py-4"
          >
            Could not load suggestions —{' '}
            <button onClick={load} className="underline hover:text-white/50">
              retry
            </button>
          </motion.p>
        ) : suggestions.length === 0 ? (
          <motion.p
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-white/30 text-center py-4"
          >
            No suggestions yet
          </motion.p>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-2"
          >
            {suggestions.map((s, i) => (
              <motion.button
                key={s.title}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: i * 0.05 }}
                whileHover={{ translateX: 3 }}
                onClick={() => handleClick(s)}
                className="group w-full flex items-start justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-left transition-all duration-200 hover:border-white/20 hover:bg-white/10"
              >
                <div className="flex items-start gap-2 min-w-0">
                  <Lightbulb className="h-4 w-4 text-yellow-400/60 group-hover:text-yellow-400 transition-colors mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm text-white/70 group-hover:text-white transition-colors leading-snug">
                      {s.title}
                    </p>
                    {s.description && (
                      <p className="text-xs text-white/35 mt-0.5 leading-snug line-clamp-2">
                        {s.description}
                      </p>
                    )}
                    {s.top_component && (
                      <p className="text-xs text-white/25 mt-1">
                        → {s.top_component.name}{' '}
                        <span className="opacity-70">
                          [{s.top_component.source_library}]
                        </span>
                      </p>
                    )}
                  </div>
                </div>
                <ArrowRight className="h-3 w-3 text-white/30 group-hover:text-white/60 transition-all duration-200 group-hover:translate-x-1 mt-1 shrink-0" />
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

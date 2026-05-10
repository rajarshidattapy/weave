'use client';

import { useApp } from '@/providers/app-context';
import { motion } from 'framer-motion';
import { Search, Wand2, Paperclip, ChevronDown, Loader2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const SOURCES = ['all', 'shadcn', 'magic', 'watermelon', 'radix'];

export function PromptComposer() {
  const { prompt, setPrompt, selectedSource, setSelectedSource, search, isSearching } =
    useApp();
  const [isFocused, setIsFocused] = useState(false);
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [prompt]);

  const handleSearch = () => search(prompt);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="space-y-3">
      {/* Prompt Input */}
      <motion.div
        animate={{
          borderColor: isFocused
            ? 'rgba(255, 255, 255, 0.2)'
            : 'rgba(255, 255, 255, 0.1)',
        }}
        transition={{ duration: 0.2 }}
        className="relative overflow-hidden rounded-2xl border bg-white/5 backdrop-blur-sm"
      >
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onKeyDown={handleKeyDown}
          placeholder="Beautify this landing page with modern AI aesthetics..."
          className="w-full resize-none bg-transparent p-4 text-sm text-white placeholder-white/40 outline-none"
          rows={3}
        />
        {isFocused && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/5 to-transparent pointer-events-none"
          />
        )}
      </motion.div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={handleSearch}
          disabled={isSearching || !prompt.trim()}
          className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:border-white/20 hover:bg-white/10 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isSearching ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4" />
          )}
          <span>{isSearching ? 'Searching…' : 'Search'}</span>
        </button>
        <button
          onClick={handleSearch}
          disabled={isSearching || !prompt.trim()}
          className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:border-white/20 hover:bg-white/10 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Wand2 className="h-4 w-4" />
          <span>Generate</span>
        </button>
      </div>

      {/* Secondary Actions */}
      <div className="flex gap-2">
        <button className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all duration-200 hover:bg-white/10 hover:text-white/70">
          <Paperclip className="h-3 w-3" />
          Attach
        </button>

        {/* Source filter */}
        <div className="relative ml-auto">
          <button
            onClick={() => setShowSourceMenu((v) => !v)}
            className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all duration-200 hover:bg-white/10 hover:text-white/70"
          >
            <span className="font-medium capitalize">
              {selectedSource === 'all' ? 'All Sources' : selectedSource}
            </span>
            <ChevronDown className="h-3 w-3" />
          </button>
          {showSourceMenu && (
            <div className="absolute right-0 top-full mt-1 z-50 min-w-[130px] rounded-xl border border-white/10 bg-black/90 backdrop-blur-xl py-1 shadow-xl">
              {SOURCES.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setSelectedSource(s);
                    setShowSourceMenu(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 text-xs capitalize transition-colors hover:bg-white/10 ${
                    selectedSource === s ? 'text-white' : 'text-white/50'
                  }`}
                >
                  {s === 'all' ? 'All Sources' : s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

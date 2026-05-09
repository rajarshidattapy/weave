'use client';

import { useApp } from '@/providers/app-context';
import { motion } from 'framer-motion';
import { Search, Wand2, Paperclip, ChevronDown } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export function PromptComposer() {
  const { prompt, setPrompt, selectedSource, setSelectedSource } = useApp();
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [prompt]);

  return (
    <div className="space-y-3">
      {/* Prompt Input */}
      <motion.div
        animate={{
          borderColor: isFocused ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)',
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
        <button className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:border-white/20 hover:bg-white/10 hover:text-white">
          <Search className="h-4 w-4" />
          <span>Search</span>
        </button>
        <button className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:border-white/20 hover:bg-white/10 hover:text-white">
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
        <div className="relative ml-auto">
          <button className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all duration-200 hover:bg-white/10 hover:text-white/70">
            <span className="font-medium">{selectedSource === 'all' ? 'All Sources' : selectedSource}</span>
            <ChevronDown className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  );
}

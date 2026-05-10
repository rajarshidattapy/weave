'use client';

import { useApp } from '@/providers/app-context';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Wand2, Paperclip, ChevronDown, Loader2, Wrench, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';

const SOURCES = ['all', 'shadcn', 'magic', 'watermelon', 'radix'];

// Detect if a string looks like a developer error / stack trace
function looksLikeError(text: string): boolean {
  return (
    /^(fix\b|error:|typeerror:|uncaught|cannot|failed to|module not found)/i.test(text.trim()) ||
    /at\s+\S+\s+\(\S+:\d+:\d+\)/.test(text) ||          // stack trace line
    /\.(tsx?|jsx?)\(\d+,\d+\):\s+error\s+TS/.test(text) // tsc output
  );
}

export function PromptComposer() {
  const {
    prompt, setPrompt,
    selectedSource, setSelectedSource,
    search, isSearching,
    fixError, isFixing,
  } = useApp();

  const [isFocused, setIsFocused] = useState(false);
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const [fixMode, setFixMode] = useState(false);
  const [errorText, setErrorText] = useState('');
  const [fixResult, setFixResult] = useState<{ success: boolean; files: string[] } | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const errorRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand main textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [prompt]);

  // Auto-detect fix mode from prompt content
  useEffect(() => {
    if (looksLikeError(prompt)) {
      setFixMode(true);
      setErrorText(prompt);
      setPrompt('');
    }
  }, [prompt, setPrompt]);

  const handleSearch = () => search(prompt);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const handleFix = async () => {
    if (!errorText.trim()) return;
    setFixResult(null);
    const result = await fixError(errorText.trim());
    const applied = result.patches.filter(p => p.applied).map(p => p.file);
    setFixResult({ success: result.success, files: applied });
    if (result.success) {
      toast.success(`Fixed ${applied.length} file(s): ${applied.join(', ')}`);
    } else {
      toast.error('Could not automatically fix this error');
    }
  };

  const enterFixMode = () => {
    setFixMode(true);
    setFixResult(null);
    setTimeout(() => errorRef.current?.focus(), 50);
  };

  const exitFixMode = () => {
    setFixMode(false);
    setErrorText('');
    setFixResult(null);
  };

  return (
    <div className="space-y-3">
      <AnimatePresence mode="wait">
        {!fixMode ? (
          /* ---- Search Mode ---- */
          <motion.div
            key="search"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-3"
          >
            <motion.div
              animate={{ borderColor: isFocused ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)' }}
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
                placeholder="Add a modern AI hero section…"
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

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={handleSearch}
                disabled={isSearching || !prompt.trim()}
                className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all hover:border-white/20 hover:bg-white/10 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                <span>{isSearching ? 'Searching…' : 'Search'}</span>
              </button>
              <button
                onClick={handleSearch}
                disabled={isSearching || !prompt.trim()}
                className="flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-white/70 transition-all hover:border-white/20 hover:bg-white/10 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Wand2 className="h-4 w-4" />
                <span>Generate</span>
              </button>
            </div>

            <div className="flex gap-2">
              <button className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all hover:bg-white/10 hover:text-white/70">
                <Paperclip className="h-3 w-3" />
                Attach
              </button>

              {/* Fix Error toggle */}
              <button
                onClick={enterFixMode}
                className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all hover:bg-orange-500/20 hover:text-orange-300"
              >
                <Wrench className="h-3 w-3" />
                Fix Error
              </button>

              {/* Source filter */}
              <div className="relative ml-auto">
                <button
                  onClick={() => setShowSourceMenu(v => !v)}
                  className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-white/50 transition-all hover:bg-white/10 hover:text-white/70"
                >
                  <span className="font-medium capitalize">
                    {selectedSource === 'all' ? 'All Sources' : selectedSource}
                  </span>
                  <ChevronDown className="h-3 w-3" />
                </button>
                {showSourceMenu && (
                  <div className="absolute right-0 top-full mt-1 z-50 min-w-[130px] rounded-xl border border-white/10 bg-black/90 backdrop-blur-xl py-1 shadow-xl">
                    {SOURCES.map(s => (
                      <button
                        key={s}
                        onClick={() => { setSelectedSource(s); setShowSourceMenu(false); }}
                        className={`w-full text-left px-3 py-1.5 text-xs capitalize transition-colors hover:bg-white/10 ${selectedSource === s ? 'text-white' : 'text-white/50'}`}
                      >
                        {s === 'all' ? 'All Sources' : s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ) : (
          /* ---- Fix Error Mode ---- */
          <motion.div
            key="fix"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-3"
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-orange-300/80">
                <Wrench className="h-3.5 w-3.5" />
                <span className="font-medium">Fix Error Mode</span>
              </div>
              <button
                onClick={exitFixMode}
                className="text-white/30 hover:text-white/60 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Error textarea */}
            <motion.div
              animate={{ borderColor: 'rgba(249,115,22,0.3)' }}
              className="rounded-2xl border bg-white/5 backdrop-blur-sm"
            >
              <textarea
                ref={errorRef}
                value={errorText}
                onChange={e => { setErrorText(e.target.value); setFixResult(null); }}
                placeholder={`Paste your error here…\n\nExamples:\n• TypeError: Cannot read properties of undefined\n• Module not found: Can't resolve 'openai'\n• app/page.tsx(12,5): error TS2304`}
                className="w-full resize-none bg-transparent p-4 text-xs font-mono text-orange-100/80 placeholder-white/25 outline-none min-h-[120px] max-h-[240px]"
                rows={5}
              />
            </motion.div>

            {/* Fix result feedback */}
            {fixResult && (
              <motion.div
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex items-start gap-2 rounded-lg px-3 py-2.5 text-xs ${fixResult.success ? 'bg-green-500/10 text-green-300' : 'bg-red-500/10 text-red-300'}`}
              >
                {fixResult.success
                  ? <CheckCircle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                  : <AlertCircle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                }
                <span>
                  {fixResult.success
                    ? `Patched ${fixResult.files.length} file(s): ${fixResult.files.join(', ')}`
                    : 'Could not automatically fix this error. Try describing it in the search bar instead.'}
                </span>
              </motion.div>
            )}

            {/* Fix button */}
            <button
              onClick={handleFix}
              disabled={isFixing || !errorText.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-lg border border-orange-500/30 bg-orange-500/10 px-3 py-2.5 text-sm font-medium text-orange-300 transition-all hover:bg-orange-500/20 hover:border-orange-400/40 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isFixing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wrench className="h-4 w-4" />}
              <span>{isFixing ? 'Fixing…' : 'Auto-Fix'}</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

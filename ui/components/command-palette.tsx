'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, CommandIcon } from 'lucide-react';

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(!isOpen);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2"
          >
            <div className="rounded-2xl border border-white/20 bg-black/90 p-4 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-4 py-3">
                <Search className="h-4 w-4 text-white/50" />
                <input
                  type="text"
                  placeholder="Search components, actions..."
                  className="flex-1 bg-transparent text-sm text-white outline-none placeholder-white/40"
                  autoFocus
                />
              </div>

              <div className="mt-4 space-y-1 max-h-80 overflow-y-auto">
                {[
                  { label: 'New Component', action: '⌘N' },
                  { label: 'Search Components', action: '⌘F' },
                  { label: 'Generate with AI', action: '⌘G' },
                  { label: 'Deploy', action: '⌘D' },
                  { label: 'Settings', action: '⌘,' },
                ].map((item) => (
                  <motion.button
                    key={item.label}
                    whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                    className="w-full rounded-lg px-3 py-2 text-left text-sm text-white/70 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span>{item.label}</span>
                      <span className="text-xs text-white/40">{item.action}</span>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

'use client';

import { motion } from 'framer-motion';
import { Chrome, Minimize2, Maximize2, RotateCcw } from 'lucide-react';
import { PreviewContent } from './preview-content';
import { useState } from 'react';

export function RightPanel() {
  const [isMaximized, setIsMaximized] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="flex-1 flex flex-col overflow-hidden bg-black p-4"
    >
      {/* Browser Chrome */}
      <motion.div
        layout
        className={`flex flex-col rounded-2xl border border-white/10 bg-black overflow-hidden shadow-2xl ${
          isMaximized ? 'fixed inset-4 z-50' : ''
        }`}
      >
        {/* Browser Header */}
        <div className="flex items-center justify-between border-b border-white/10 bg-black/60 px-4 py-3 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <Chrome className="h-4 w-4 text-white/40" />
            <span className="text-xs text-white/60 font-medium">localhost:3000</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="rounded-lg p-1.5 text-white/40 transition-all duration-200 hover:bg-white/10 hover:text-white/60">
              <RotateCcw className="h-4 w-4" />
            </button>
            <button
              onClick={() => setIsMaximized(!isMaximized)}
              className="rounded-lg p-1.5 text-white/40 transition-all duration-200 hover:bg-white/10 hover:text-white/60"
            >
              {isMaximized ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className={`flex-1 overflow-y-auto bg-black ${isMaximized ? '' : 'max-h-[calc(100vh-200px)]'}`}>
          <PreviewContent />
        </div>
      </motion.div>

      {/* Floating Keyboard Shortcuts Hint */}
      {!isMaximized && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
          className="mt-4 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-xs text-white/50 backdrop-blur-sm"
        >
          <span className="font-medium">Tip:</span> Press{' '}
          <span className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-white/70">Cmd+K</span> for
          quick actions
        </motion.div>
      )}
    </motion.div>
  );
}

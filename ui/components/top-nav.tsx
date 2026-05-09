'use client';

import { useWebContainer } from '@/providers/webcontainer-provider';
import { motion } from 'framer-motion';
import { Download, Circle } from 'lucide-react';
export function TopNav() {
  const { isReady, isInitializing } = useWebContainer();

  const statusColor = isInitializing ? 'bg-yellow-500' : isReady ? 'bg-green-500' : 'bg-red-500';
  const statusText = isInitializing ? 'Initializing' : isReady ? 'Running' : 'Error';

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="sticky top-0 z-50 flex h-16 items-center justify-between border-b border-white/5 bg-black/40 px-6 backdrop-blur-xl"
    >
      {/* Left: Logo */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-black font-bold">
            W
          </div>
          <span className="text-lg font-semibold text-white">Weave</span>
        </div>
      </div>



      {/* Right: Status + Deploy */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-full bg-white/5 px-3 py-1.5">
          <Circle className={`h-2 w-2 ${statusColor}`} />
          <span className="text-xs font-medium text-white/70">{statusText}</span>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white/70 transition-all duration-200 hover:bg-white/20 hover:text-white">
          <Download className="h-4 w-4" />
          <span className="hidden sm:inline">Deploy</span>
        </button>
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />
      </div>
    </motion.div>
  );
}

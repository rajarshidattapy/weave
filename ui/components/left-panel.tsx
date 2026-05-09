'use client';

import { motion } from 'framer-motion';
import { PromptComposer } from './prompt-composer';
import { ComponentSuggestions } from './component-suggestions';
import { AIRecommendations } from './ai-recommendations';
import { RecentComponents } from './recent-components';

export function LeftPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="w-full md:w-[420px] flex-shrink-0 border-r border-white/5 bg-black/40 overflow-y-auto max-h-[calc(100vh-64px)]"
    >
      <div className="space-y-8 p-6">
        {/* Prompt Composer */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-white/50 mb-4">
            Composition
          </h2>
          <PromptComposer />
        </div>

        {/* Component Suggestions */}
        <ComponentSuggestions />

        {/* AI Recommendations */}
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-white/50 mb-4">
            Improvements
          </h2>
          <AIRecommendations />
        </div>

        {/* Recent Components */}
        <RecentComponents />
      </div>
    </motion.div>
  );
}

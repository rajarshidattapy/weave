'use client';

import { motion } from 'framer-motion';
import { Lightbulb, ArrowRight } from 'lucide-react';

const RECOMMENDATIONS = [
  'Improve hero spacing',
  'Add animated CTA',
  'Add social proof',
  'Add testimonials',
];

export function AIRecommendations() {
  return (
    <div className="space-y-2">
      {RECOMMENDATIONS.map((rec, index) => (
        <motion.button
          key={rec}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.05 }}
          whileHover={{ translateX: 4 }}
          className="group w-full flex items-center justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-left transition-all duration-200 hover:border-white/20 hover:bg-white/10"
        >
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-yellow-400/60 group-hover:text-yellow-400 transition-colors" />
            <span className="text-sm text-white/70 group-hover:text-white transition-colors">{rec}</span>
          </div>
          <ArrowRight className="h-3 w-3 text-white/30 group-hover:text-white/60 transition-all duration-200 group-hover:translate-x-1" />
        </motion.button>
      ))}
    </div>
  );
}

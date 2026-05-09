'use client';

import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const RECENT = [
  { title: 'Hero Section', date: '2 hours ago' },
  { title: 'Feature Grid', date: '5 hours ago' },
  { title: 'CTA Button', date: '1 day ago' },
  { title: 'Footer', date: '2 days ago' },
];

export function RecentComponents() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.6 }}
      className="mt-8 border-t border-white/10 pt-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock className="h-4 w-4 text-white/40" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-white/50">Recently Used</h3>
      </div>
      <div className="space-y-2">
        {RECENT.map((item) => (
          <motion.button
            key={item.title}
            whileHover={{ translateX: 4 }}
            className="w-full rounded-lg border border-white/5 bg-white/5 px-3 py-2 text-left text-xs transition-all duration-200 hover:border-white/20 hover:bg-white/10"
          >
            <div className="flex items-center justify-between">
              <span className="text-white/70">{item.title}</span>
              <span className="text-white/40">{item.date}</span>
            </div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

'use client';

import { motion } from 'framer-motion';
import { MessageCircle, Settings, HelpCircle } from 'lucide-react';

export function FloatingActions() {
  const actions = [
    { icon: MessageCircle, label: 'Feedback', color: 'from-blue-500 to-blue-600' },
    { icon: Settings, label: 'Settings', color: 'from-purple-500 to-purple-600' },
    { icon: HelpCircle, label: 'Help', color: 'from-pink-500 to-pink-600' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.5 }}
      className="fixed bottom-8 right-8 z-40 flex flex-col gap-3"
    >
      {actions.map((action, index) => (
        <motion.button
          key={action.label}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          initial={{ opacity: 0, scale: 0.8, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.5 + index * 0.05 }}
          className={`group relative rounded-full bg-gradient-to-br ${action.color} p-3 text-white shadow-lg transition-all duration-200 hover:shadow-xl`}
          title={action.label}
        >
          <action.icon className="h-5 w-5" />
          <div className="absolute right-full mr-3 whitespace-nowrap rounded-lg bg-black/90 px-3 py-1.5 text-xs text-white opacity-0 transition-opacity duration-200 group-hover:opacity-100">
            {action.label}
          </div>
        </motion.button>
      ))}
    </motion.div>
  );
}

'use client';

import { Component } from '@/providers/app-context';
import { useApp } from '@/providers/app-context';
import { motion } from 'framer-motion';
import { Plus, Zap } from 'lucide-react';
import { toast } from 'sonner';

const SUGGESTED_COMPONENTS: Component[] = [
  {
    id: 'hero-1',
    title: 'Modern Hero Section',
    source: 'shadcn',
    tags: ['hero', 'landing', 'animated'],
    compatibility: 98,
    preview: '🎨',
  },
  {
    id: 'features-grid',
    title: 'Feature Grid 3x2',
    source: 'aceternity',
    tags: ['features', 'grid', 'cards'],
    compatibility: 95,
    preview: '📊',
  },
  {
    id: 'cta-button',
    title: 'Animated CTA Button',
    source: 'magic',
    tags: ['button', 'cta', 'interactive'],
    compatibility: 100,
    preview: '🔘',
  },
  {
    id: 'testimonials',
    title: 'Social Proof Section',
    source: 'shadcn',
    tags: ['testimonials', 'social', 'cards'],
    compatibility: 92,
    preview: '💬',
  },
  {
    id: 'pricing-table',
    title: 'Pricing Table',
    source: 'watermelon',
    tags: ['pricing', 'table', 'comparison'],
    compatibility: 88,
    preview: '💰',
  },
  {
    id: 'footer-advanced',
    title: 'Advanced Footer',
    source: 'shadcn',
    tags: ['footer', 'links', 'social'],
    compatibility: 96,
    preview: '👣',
  },
];

const SOURCE_COLORS: Record<string, string> = {
  shadcn: 'bg-blue-500/20 text-blue-300',
  aceternity: 'bg-purple-500/20 text-purple-300',
  magic: 'bg-pink-500/20 text-pink-300',
  watermelon: 'bg-red-500/20 text-red-300',
};

export function ComponentSuggestions() {
  const { addComponent, prompt } = useApp();

  const handleAddComponent = (component: Component) => {
    addComponent(component);
    toast.success(`Added "${component.title}" to page`);
  };

  const filteredComponents = SUGGESTED_COMPONENTS.filter(c => 
    c.title.toLowerCase().includes(prompt.toLowerCase()) ||
    c.tags.some(t => t.toLowerCase().includes(prompt.toLowerCase()))
  );

  if (prompt.trim().length === 0 || filteredComponents.length === 0) {
    return null;
  }

  return (
    <div>
      <h2 className="text-xs font-semibold uppercase tracking-wider text-white/50 mb-4">
        Components
      </h2>
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">Suggested Components</h3>
          <div className="space-y-2">
            {filteredComponents.map((component, index) => (
            <motion.div
              key={component.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              whileHover={{ scale: 1.02, translateX: 4 }}
              className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-3 transition-all duration-200 hover:border-white/20 hover:bg-white/10 cursor-pointer"
              onClick={() => handleAddComponent(component)}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 text-lg font-semibold">
                  {component.preview}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-sm font-medium text-white truncate">{component.title}</h4>
                    <Plus className="h-4 w-4 text-white/40 transition-all duration-200 group-hover:text-white/100 group-hover:scale-110 flex-shrink-0" />
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-2">
                    <div className="flex gap-1 flex-wrap">
                      <span className={`rounded-full px-2 py-1 text-xs font-medium ${SOURCE_COLORS[component.source]}`}>
                        {component.source}
                      </span>
                      {component.compatibility >= 95 && (
                        <span className="rounded-full bg-green-500/20 px-2 py-1 text-xs font-medium text-green-300 flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          {component.compatibility}%
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 flex gap-1 flex-wrap">
                    {component.tags.map((tag) => (
                      <span key={tag} className="text-xs text-white/50">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
            </motion.div>
          ))}
            </div>
          </div>
        </div>
      </div>
  );
}

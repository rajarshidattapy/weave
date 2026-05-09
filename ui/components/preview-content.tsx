'use client';

import { motion } from 'framer-motion';
import { useApp } from '@/providers/app-context';
import { X } from 'lucide-react';

export function PreviewContent() {
  const { addedComponents, removeComponent } = useApp();

  return (
    <div className="min-h-full bg-gradient-to-b from-black via-slate-950 to-black">
      {/* Navbar */}
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="sticky top-0 z-50 border-b border-white/10 bg-black/40 backdrop-blur-xl"
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 font-bold text-white">
              W
            </div>
            <span className="font-semibold text-white">AI Studio</span>
          </div>
          <div className="hidden gap-8 md:flex">
            {['Product', 'Features', 'Pricing', 'Docs'].map((item) => (
              <button key={item} className="text-sm text-white/70 transition-colors hover:text-white">
                {item}
              </button>
            ))}
          </div>
          <button className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-black transition-all duration-200 hover:bg-white/90">
            Get Started
          </button>
        </div>
      </motion.nav>

      {/* Hero */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="border-b border-white/10 px-6 py-24"
      >
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-5xl font-bold text-white md:text-6xl">
            Build beautiful interfaces
            <span className="block bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              with AI superpowers
            </span>
          </h1>
          <p className="mt-6 text-lg text-white/60">
            Design, build, and deploy modern web experiences in minutes. No code required.
          </p>
          <button className="mt-8 rounded-lg bg-white px-8 py-3 font-medium text-black transition-all duration-200 hover:bg-white/90 hover:scale-105">
            Start Building
          </button>
        </div>
      </motion.section>

      {/* Features */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="border-b border-white/10 px-6 py-24"
      >
        <div className="mx-auto max-w-6xl">
          <h2 className="text-center text-3xl font-bold text-white mb-16">Powerful Features</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                title: 'AI-Powered',
                desc: 'Generate components with natural language',
              },
              {
                title: 'Live Preview',
                desc: 'See changes in real-time as you build',
              },
              {
                title: 'Production Ready',
                desc: 'Export clean, optimized React code',
              },
            ].map((feature) => (
              <motion.div
                key={feature.title}
                whileHover={{ scale: 1.05, translateY: -4 }}
                className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition-all duration-200 hover:border-white/20 hover:bg-white/10"
              >
                <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                <p className="mt-2 text-white/60">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Added Components Preview */}
      {addedComponents.length > 0 && (
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="border-b border-white/10 px-6 py-24"
        >
          <div className="mx-auto max-w-6xl">
            <h2 className="text-2xl font-bold text-white mb-8">Added Components</h2>
            <div className="space-y-4">
              {addedComponents.map((component) => (
                <motion.div
                  key={component.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 p-4 backdrop-blur-sm"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">{component.preview}</div>
                    <div>
                      <p className="font-medium text-white">{component.title}</p>
                      <p className="text-xs text-white/50">{component.source}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeComponent(component.id)}
                    className="rounded-lg p-2 text-white/50 transition-all duration-200 hover:bg-red-500/20 hover:text-red-400"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>
      )}

      {/* CTA */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="px-6 py-24"
      >
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold text-white">Ready to build?</h2>
          <p className="mt-4 text-white/60">Join thousands of developers using Weave</p>
          <button className="mt-8 rounded-lg bg-white px-8 py-3 font-medium text-black transition-all duration-200 hover:bg-white/90 hover:scale-105">
            Get Started Free
          </button>
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="border-t border-white/10 px-6 py-12">
        <div className="mx-auto max-w-6xl text-center text-sm text-white/50">
          <p>&copy; 2024 Weave. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

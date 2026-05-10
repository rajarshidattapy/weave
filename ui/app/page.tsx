'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Github, Folder, ChevronRight, Layers, Box, Terminal, Loader2, CheckCircle2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function OnboardingFlow() {
  const [step, setStep] = useState(1);
  const router = useRouter();

  const nextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleComplete = () => {
    router.push('/studio');
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-6 relative overflow-hidden selection:bg-blue-500/30">
      {/* Cinematic Backgrounds */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,0.15),transparent_50%)]" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-[0.03]" />

      <div className="w-full max-w-3xl relative z-10">
        <AnimatePresence mode="wait">
          {step === 1 && <StepOne key="step1" onNext={nextStep} />}
          {step === 2 && <StepTwo key="step2" onNext={nextStep} />}
          {step === 3 && <StepThree key="step3" onComplete={handleComplete} />}
        </AnimatePresence>
      </div>
    </div>
  );
}

function StepOne({ onNext }: { onNext: () => void }) {
  const [isDragging, setIsDragging] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col items-center w-full"
    >
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-white/50">
          Import your frontend
        </h1>
        <p className="text-lg text-white/50">
          Upload the interface you want Weave to enhance.
        </p>
      </div>

      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          className={`col-span-1 md:col-span-2 relative group rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-12 cursor-pointer ${
            isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20'
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragging(false); onNext(); }}
          onClick={onNext}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl pointer-events-none" />
          <Upload className={`w-10 h-10 mb-4 transition-colors ${isDragging ? 'text-blue-400' : 'text-white/40 group-hover:text-white/70'}`} />
          <p className="text-white/70 font-medium text-lg mb-2">Drag & drop your Next.js project</p>
          <p className="text-white/40 text-sm">Supports React, Next.js, and Tailwind CSS</p>
        </div>

        <button onClick={onNext} className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 text-left hover:bg-white/10 transition-colors">
          <Github className="w-6 h-6 text-white/50 mb-3 group-hover:text-white transition-colors" />
          <h3 className="text-white font-medium mb-1">Import from GitHub</h3>
          <p className="text-white/40 text-sm">Paste a repository URL</p>
        </button>

        <button onClick={onNext} className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 text-left hover:bg-white/10 transition-colors">
          <Folder className="w-6 h-6 text-white/50 mb-3 group-hover:text-white transition-colors" />
          <h3 className="text-white font-medium mb-1">Upload ZIP</h3>
          <p className="text-white/40 text-sm">Upload an archived project</p>
        </button>
      </div>
    </motion.div>
  );
}

function StepTwo({ onNext }: { onNext: () => void }) {
  const [selected, setSelected] = useState<string[]>(['shadcn/ui']);

  const libraries = [
    { id: 'shadcn/ui', name: 'shadcn/ui', tags: ['Radix', 'Tailwind'] },
    { id: 'aceternity', name: 'Aceternity UI', tags: ['Framer', 'Animations'] },
    { id: 'magic', name: 'Magic UI', tags: ['Motion', 'Tailwind'] },
    { id: 'watermelon', name: 'OneWatermelon', tags: ['Premium', 'Dark'] },
  ];

  const toggle = (id: string) => {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col items-center w-full"
    >
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-white/50">
          Choose your universe
        </h1>
        <p className="text-lg text-white/50">
          Select the component libraries Weave can compose with.
        </p>
      </div>

      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">
        {libraries.map((lib) => {
          const isSelected = selected.includes(lib.id);
          return (
            <button
              key={lib.id}
              onClick={() => toggle(lib.id)}
              className={`relative overflow-hidden flex flex-col p-6 rounded-2xl border text-left transition-all duration-300 ${
                isSelected 
                  ? 'border-blue-500/50 bg-blue-500/10 shadow-[0_0_30px_rgba(59,130,246,0.15)]' 
                  : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-blue-500/20 text-blue-400' : 'bg-white/10 text-white/50'}`}>
                  {isSelected ? <Layers className="w-5 h-5" /> : <Box className="w-5 h-5" />}
                </div>
                <div className={`w-5 h-5 rounded-full border flex items-center justify-center transition-colors ${
                  isSelected ? 'border-blue-500 bg-blue-500 text-white' : 'border-white/20 bg-transparent'
                }`}>
                  {isSelected && <CheckCircle2 className="w-3 h-3" />}
                </div>
              </div>
              <h3 className={`font-semibold text-lg mb-1 ${isSelected ? 'text-white' : 'text-white/80'}`}>{lib.name}</h3>
              <div className="flex gap-2">
                {lib.tags.map(tag => (
                  <span key={tag} className={`text-xs px-2 py-1 rounded-full ${isSelected ? 'bg-blue-500/20 text-blue-300' : 'bg-white/10 text-white/40'}`}>
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          )
        })}
      </div>

      <button
        onClick={onNext}
        disabled={selected.length === 0}
        className="group relative inline-flex items-center justify-center gap-2 rounded-full bg-white px-8 py-3.5 text-sm font-semibold text-black transition-all hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Continue Setup
        <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
      </button>
    </motion.div>
  );
}

function StepThree({ onComplete }: { onComplete: () => void }) {
  const [logs, setLogs] = useState<string[]>([]);
  
  useEffect(() => {
    const sequence = [
      'Initializing AI workspace...',
      'Analyzing repository structure...',
      'Detected Next.js App Router',
      'Indexing 42 UI components...',
      'Generating semantic design graph...',
      'Booting WebContainer sandbox...',
      'Installing dependencies...',
      'Environment ready.'
    ];

    let current = 0;
    const interval = setInterval(() => {
      if (current < sequence.length) {
        setLogs(prev => [...prev, sequence[current]]);
        current++;
      } else {
        clearInterval(interval);
        setTimeout(onComplete, 1500); // Transition out
      }
    }, 600);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center w-full"
    >
      <div className="w-full max-w-xl rounded-2xl border border-white/10 bg-black/60 backdrop-blur-xl overflow-hidden shadow-2xl relative">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent pointer-events-none" />
        
        <div className="flex items-center border-b border-white/10 px-4 py-3 bg-white/5">
          <Terminal className="w-4 h-4 text-white/50 mr-2" />
          <span className="text-xs font-mono text-white/50">weave-runtime-init</span>
        </div>
        
        <div className="p-6 font-mono text-sm h-[300px] flex flex-col justify-end">
          <div className="space-y-3 overflow-y-auto">
            <AnimatePresence>
              {logs.map((log, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-3"
                >
                  <span className="text-blue-500">→</span>
                  <span className={i === logs.length - 1 ? 'text-green-400 font-semibold' : 'text-white/70'}>{log}</span>
                  {i === logs.length - 1 && <Loader2 className="w-3 h-3 text-green-400 animate-spin ml-2" />}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <motion.p 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-8 text-white/40 text-sm flex items-center gap-2"
      >
        <Loader2 className="w-4 h-4 animate-spin" />
        Preparing your IDE...
      </motion.p>
    </motion.div>
  );
}

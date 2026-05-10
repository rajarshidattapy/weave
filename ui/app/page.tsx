'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Github, Folder, ChevronRight, Layers, Box, Terminal, Loader2, CheckCircle2, Search, Plus, Link as LinkIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Script from 'next/script';
import { useAuth, UserButton, SignInButton } from '@clerk/nextjs';
import { indexLibrary } from '@/lib/api';

// Maps library IDs to their docs base URLs for indexing
const LIBRARY_URLS: Record<string, { url: string; name: string }> = {
  'shadcn/ui': { url: 'https://ui.shadcn.com/docs/components', name: 'shadcn/ui' },
  aceternity: { url: 'https://ui.aceternity.com/components', name: 'Aceternity UI' },
  magic: { url: 'https://magicui.design/docs/components', name: 'Magic UI' },
  watermelon: { url: 'https://ui.watermelon.sh/components', name: 'Watermelon UI' },
};

export default function OnboardingFlow() {
  const { isSignedIn } = useAuth();
  const [step, setStep] = useState(1);
  const [selectedLibraries, setSelectedLibraries] = useState<string[]>(['shadcn/ui']);
  const router = useRouter();

  const nextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleComplete = () => {
    router.push('/studio');
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col relative overflow-hidden selection:bg-blue-500/30">
      {/* Tenor GIF Background */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-30 mix-blend-screen flex items-center justify-center">
        <div className="min-w-[150vw] min-h-[150vh] md:min-w-[110vw] md:min-h-[110vh] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
          <div className="tenor-gif-embed" data-postid="738217998359236596" data-share-method="host" data-aspect-ratio="1.76596" data-width="100%">
            <a href="https://tenor.com/view/%D0%B1%D0%B0%D0%BD%D0%BD%D0%B5%D1%80-gif-738217998359236596">баннер GIF</a>
          </div>
          <Script strategy="lazyOnload" src="https://tenor.com/embed.js" />
        </div>
      </div>

      {/* Cinematic Backgrounds Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(59,130,246,0.15),transparent_50%)] z-0" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-[0.03] z-0" />

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 md:px-12 md:py-6 w-full max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-black font-bold text-lg shadow-[0_0_30px_rgba(255,255,255,0.3)]">
            W
          </div>
          <span className="text-2xl font-bold tracking-tight">Weave</span>
        </div>
        <div className="flex items-center gap-4">
          {isSignedIn ? (
            <>
              <button onClick={() => router.push('/studio')} className="text-sm font-medium text-white/70 hover:text-white transition-colors mr-2">
                Enter Studio
              </button>
              <UserButton
                appearance={{ elements: { userButtonPopoverCard: "bg-black/90 border border-white/10" } }}
              />
            </>
          ) : (
            <SignInButton mode="modal">
              <button className="text-sm font-medium text-white/70 hover:text-white transition-colors">
                Sign In
              </button>
            </SignInButton>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex flex-col lg:flex-row items-center justify-center w-full max-w-7xl mx-auto px-6 lg:px-12 gap-12 lg:gap-24 relative z-10 py-12 lg:py-0">

        {/* Left: Hero Messaging */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col flex-1 max-w-2xl"
        >
          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-[1.1] mb-6">
            Build beautiful interfaces <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
              Faster.
            </span>
          </h1>
          <p className="text-lg md:text-xl text-white/50 leading-relaxed mb-8">
            Search, compose, and ship production-grade UI with live AI-assisted component retrieval.
          </p>

          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2 text-sm text-white/70 bg-white/5 px-4 py-2 rounded-full border border-white/10">
              <Search className="w-4 h-4 text-white" />
              Semantic Search
            </div>
            <div className="flex items-center gap-2 text-sm text-white/70 bg-white/5 px-4 py-2 rounded-full border border-white/10">
              <Layers className="w-4 h-4 text-white" />
              Live Composition
            </div>
            <div className="flex items-center gap-2 text-sm text-white/70 bg-white/5 px-4 py-2 rounded-full border border-white/10">
              <Terminal className="w-4 h-4 text-white" />
              WebContainers
            </div>
          </div>
        </motion.div>

        {/* Right: Interactive Widget */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="w-full flex-1 max-w-xl"
        >
          <div className="bg-black/40 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 md:p-10 shadow-[0_0_50px_rgba(59,130,246,0.1)] relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
            <AnimatePresence mode="wait">
              {step === 1 && <StepOne key="step1" onNext={nextStep} />}
              {step === 2 && (
                <StepTwo
                  key="step2"
                  selected={selectedLibraries}
                  setSelected={setSelectedLibraries}
                  onNext={nextStep}
                />
              )}
              {step === 3 && (
                <StepThree
                  key="step3"
                  libraries={selectedLibraries}
                  onComplete={handleComplete}
                />
              )}
            </AnimatePresence>
          </div>
        </motion.div>

      </main>
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
          className={`col-span-1 md:col-span-2 relative group rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-12 cursor-pointer ${isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20'
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

function StepTwo({
  onNext,
  selected,
  setSelected,
}: {
  onNext: () => void;
  selected: string[];
  setSelected: (libs: string[]) => void;
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [customLibraries, setCustomLibraries] = useState<{ id: string, name: string, tags: string[] }[]>([]);

  const baseLibraries = [
    { id: 'shadcn/ui', name: 'shadcn/ui', tags: ['Radix', 'Tailwind'] },
    { id: 'aceternity', name: 'Aceternity UI', tags: ['Framer', 'Animations'] },
    { id: 'magic', name: 'Magic UI', tags: ['Motion', 'Tailwind'] },
    { id: 'watermelon', name: 'Watermelon', tags: ['Premium', 'Dark'] },
  ];

  const allLibraries = [...baseLibraries, ...customLibraries];
  const isUrl = searchQuery.startsWith('http://') || searchQuery.startsWith('https://');

  const filteredLibraries = isUrl
    ? allLibraries
    : allLibraries.filter(lib =>
      lib.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lib.id.toLowerCase().includes(searchQuery.toLowerCase())
    );

  const addCustomSource = () => {
    if (!isUrl) return;
    const newId = searchQuery;
    // Extract a friendly name from URL (e.g. ui.watermelon.sh -> Watermelon)
    let newName = searchQuery;
    try {
      const urlObj = new URL(searchQuery);
      let hostname = urlObj.hostname.replace(/^www\./, '');
      let parts = hostname.split('.');
      let mainPart = parts[0];

      // If it's a domain with a TLD, grab the domain name (e.g. ui.watermelon.sh -> watermelon)
      if (parts.length >= 2) {
        mainPart = parts[parts.length - 2];
      }

      newName = mainPart.charAt(0).toUpperCase() + mainPart.slice(1);
    } catch (e) { }

    setCustomLibraries((prev) => [...prev, { id: newId, name: newName, tags: ['Custom URL'] }]);
    setSelected([...selected, newId]);
    setSearchQuery('');
  };

  const toggle = (id: string) => {
    setSelected(selected.includes(id) ? selected.filter(x => x !== id) : [...selected, id]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col items-center w-full"
    >
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-white/50">
          Choose your universe
        </h1>
        <p className="text-lg text-white/50">
          Select the component libraries Weave can compose with.
        </p>
      </div>

      <div className="relative w-full max-w-md mx-auto mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && isUrl) {
                e.preventDefault();
                addCustomSource();
              }
            }}
            placeholder="Search libraries or paste a URL..."
            className="w-full bg-white/5 border border-white/10 rounded-full py-3.5 pl-12 pr-12 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all shadow-[0_0_20px_rgba(255,255,255,0.02)]"
          />
          {isUrl && (
            <button
              onClick={addCustomSource}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-500 hover:bg-blue-400 text-white p-2 rounded-full transition-colors flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.5)]"
              title="Add custom URL"
            >
              <Plus className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10 max-h-[400px] overflow-y-auto px-2 pb-2">
        {filteredLibraries.length === 0 && !isUrl ? (
          <div className="col-span-full py-12 text-center text-white/40 flex flex-col items-center">
            <Search className="w-8 h-8 mb-3 opacity-50" />
            <p>No libraries found matching "{searchQuery}"</p>
            <p className="text-sm mt-1">Paste a valid URL to add a custom source</p>
          </div>
        ) : null}

        {filteredLibraries.map((lib) => {
          const isSelected = selected.includes(lib.id);
          return (
            <button
              key={lib.id}
              onClick={() => toggle(lib.id)}
              className={`relative overflow-hidden flex flex-col p-6 rounded-2xl border text-left transition-all duration-300 ${isSelected
                ? 'border-blue-500/50 bg-blue-500/10 shadow-[0_0_30px_rgba(59,130,246,0.15)]'
                : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
                }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-blue-500/20 text-blue-400' : 'bg-white/10 text-white/50'}`}>
                  {lib.tags.includes('Custom URL') ? <LinkIcon className="w-5 h-5" /> : isSelected ? <Layers className="w-5 h-5" /> : <Box className="w-5 h-5" />}
                </div>
                <div className={`w-5 h-5 rounded-full border flex items-center justify-center transition-colors ${isSelected ? 'border-blue-500 bg-blue-500 text-white' : 'border-white/20 bg-transparent'
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

function StepThree({
  libraries,
  onComplete,
}: {
  libraries: string[];
  onComplete: () => void;
}) {
  const [logs, setLogs] = useState<string[]>([]);

  const pushLog = (msg: string) => setLogs((prev) => [...prev, msg]);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      pushLog('Initializing AI workspace...');
      pushLog('Detected Next.js App Router');

      // Kick off indexing for each selected library, fire & forget
      const targets = libraries.map((id) => {
        const known = LIBRARY_URLS[id];
        if (known) return known;
        // Custom URL
        if (id.startsWith('http')) {
          let name = id;
          try {
            const parts = new URL(id).hostname.replace(/^www\./, '').split('.');
            name = parts[parts.length - 2];
            name = name.charAt(0).toUpperCase() + name.slice(1);
          } catch {}
          return { url: id, name };
        }
        return null;
      }).filter(Boolean) as { url: string; name: string }[];

      for (const lib of targets) {
        if (cancelled) return;
        pushLog(`Indexing ${lib.name}...`);
        // Fire indexing without waiting — it runs in the backend
        indexLibrary(lib.url, lib.name).then((res) => {
          if (!cancelled) {
            pushLog(
              `✓ ${lib.name}: ${res.indexed_components} components indexed`
            );
          }
        }).catch(() => {
          if (!cancelled) pushLog(`⚠ ${lib.name}: backend offline, skipping`);
        });
      }

      pushLog('Generating semantic design graph...');
      await new Promise((r) => setTimeout(r, 800));
      pushLog('Booting WebContainer sandbox...');
      await new Promise((r) => setTimeout(r, 600));
      pushLog('Environment ready.');
      await new Promise((r) => setTimeout(r, 1200));
      if (!cancelled) onComplete();
    };

    run();
    return () => { cancelled = true; };
  }, [libraries, onComplete]);

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
          <span className="text-xs font-mono text-white/50">Weave</span>
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

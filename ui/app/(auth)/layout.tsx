import { motion } from 'framer-motion';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-black text-white selection:bg-blue-500/30">
      {/* Left Panel - Branding & Messaging */}
      <div className="hidden md:flex md:flex-1 relative overflow-hidden bg-black border-r border-white/5">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(59,130,246,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-[0.02]" />

        {/* Animated Glow */}
        <div className="absolute -left-1/2 -top-1/2 h-[200%] w-[200%] animate-[spin_60s_linear_infinite] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(59,130,246,0.3)_360deg)] blur-3xl opacity-20" />

        <div className="relative z-10 flex flex-col justify-center p-16 w-full max-w-2xl mx-auto h-full">
          <div className="flex items-center gap-3 mb-12">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-black font-bold text-xl shadow-[0_0_30px_rgba(255,255,255,0.3)]">
              W
            </div>
            <span className="text-3xl font-bold tracking-tight">Weave</span>
          </div>

          <h1 className="text-5xl font-bold tracking-tighter leading-[1.1] mb-6">
            Compose interfaces <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500">
              with intelligence.
            </span>
          </h1>

          <p className="text-lg text-white/50 leading-relaxed mb-12 max-w-lg">
            The retrieval-native frontend operating system. Stop rebuilding the same components. Retrieve, compose, and deploy production-grade UI instantly.
          </p>

          <div className="space-y-4">
            {[
              "Semantic UI Search",
              "Live Component Injection",
              "Sandboxed WebContainer Runtime",
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-white/70">
                <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                {feature}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Component */}
      <div className="flex-1 flex flex-col justify-center items-center relative overflow-hidden bg-black/50">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(168,85,247,0.1),transparent_40%)]" />

        <div className="relative z-10 w-full max-w-md px-6 md:px-0">
          <div className="md:hidden flex items-center justify-center gap-3 mb-12">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-black font-bold text-lg shadow-[0_0_30px_rgba(255,255,255,0.3)]">
              W
            </div>
            <span className="text-2xl font-bold tracking-tight">Weave</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

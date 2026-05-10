import Button from "./components/Button";
import {
  FeatureGrid,
  HeroSection,
  MetricsStrip,
} from "./components";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="bg-foreground text-background shadow-sm">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 md:px-6">
          <span className="text-base font-semibold">test-next</span>
          <span className="text-sm opacity-70"></span>
        </div>
      </nav>

      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-4 py-10 md:px-6 md:py-12">
        <HeroSection
          title="Simple components for swap demos"
          description="Hero sections and cards are the clearest blocks to retrieve, swap, and compare without changing the page structure."
        />

        <MetricsStrip />
        <FeatureGrid />
        <Button />
      </main>
    </div>
  );
}
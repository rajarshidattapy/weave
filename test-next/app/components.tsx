type SectionProps = {
  title: string;
  description: string;
};

type CardProps = {
  title: string;
  description: string;
};

type MetricProps = {
  label: string;
  value: string;
};

export function HeroSection({ title, description }: SectionProps) {
  return (
    <section className="flex flex-col gap-6 rounded-2xl border border-border bg-surface p-8">
      <div className="flex flex-col gap-3">
        <span className="w-fit rounded-full border border-border px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
          Composition Demo
        </span>
        <h1 className="max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
          {title}
        </h1>
        <p className="max-w-2xl text-base leading-7 text-muted-foreground">
          {description}
        </p>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          className="min-h-10 rounded-md bg-foreground px-6 py-3 text-sm font-medium text-background transition-colors hover:opacity-90 focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          Inject Component
        </button>
        <button
          type="button"
          className="min-h-10 rounded-md border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-surface-strong focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          Swap Variant
        </button>
      </div>
    </section>
  );
}

export function MetricsStrip() {
  const metrics: MetricProps[] = [
    { label: "Libraries", value: "4+" },
    { label: "Swap Targets", value: "3" },
    { label: "Preview Speed", value: "Live" },
  ];

  return (
    <section
      aria-label="Project metrics"
      className="grid gap-4 sm:grid-cols-3"
    >
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded-xl border border-border p-5 text-center"
        >
          <div className="text-2xl font-semibold">{metric.value}</div>
          <div className="mt-1 text-sm text-muted-foreground">{metric.label}</div>
        </div>
      ))}
    </section>
  );
}

export function FeatureGrid() {
  const cards: CardProps[] = [
    {
      title: "Hero",
      description:
        "Best place to compare different design systems quickly.",
    },
    {
      title: "Cards",
      description:
        "Useful for demonstrating layout, spacing, and hierarchy changes.",
    },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2">
      {cards.map((card) => (
        <article
          key={card.title}
          className="rounded-xl border border-border p-6 transition-colors hover:bg-surface"
        >
          <h2 className="text-lg font-semibold">{card.title}</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {card.description}
          </p>
        </article>
      ))}
    </section>
  );
}

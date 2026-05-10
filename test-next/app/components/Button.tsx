type ButtonProps = {
  label?: string;
};

export default function Button({ label = "Button" }: ButtonProps) {
  return (
    <button
      type="button"
      className="min-h-10 rounded-md border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-surface-strong focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-background"
    >
      {label}
    </button>
  );
}

"use client";

import { useState, useRef, useEffect } from "react";

export default function DropdownMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="min-h-10 rounded-md border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-surface-strong focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        Open
      </button>

      {open && (
        <div className="absolute left-0 z-10 mt-2 w-48 rounded-md border border-border bg-background shadow-lg">
          <div className="py-1">
            <span className="block px-4 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              My Account
            </span>
            <button className="block w-full px-4 py-2 text-left text-sm hover:bg-surface">
              Profile
            </button>
            <button className="block w-full px-4 py-2 text-left text-sm hover:bg-surface">
              Billing
            </button>
          </div>
          <hr className="border-border" />
          <div className="py-1">
            <button className="block w-full px-4 py-2 text-left text-sm hover:bg-surface">
              Team
            </button>
            <button className="block w-full px-4 py-2 text-left text-sm hover:bg-surface">
              Subscription
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
"""
Reset Agent — restores the test-next sandbox to its original template state.

Called on every Weave studio page load so injected components don't persist
across browser refreshes.
"""
import logging
import os
import shutil

logger = logging.getLogger(__name__)

SANDBOX_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test-next")
)

# Canonical clean state of app/page.tsx — updated here if the template changes.
ORIGINAL_PAGE = """\
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
      </main>
    </div>
  );
}
"""

# Files inside app/components/ that ship with the template and must not be removed.
_ORIGINAL_COMPONENTS = {"Button.tsx"}


def reset_sandbox() -> dict:
    """
    Restore test-next to its clean template state:
    - Overwrite app/page.tsx with the original content
    - Delete any injected component files from app/components/
      (keeps the original template components)
    """
    restored = []
    removed = []

    try:
        page_path = os.path.join(SANDBOX_ROOT, "app", "page.tsx")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(ORIGINAL_PAGE)
        restored.append("app/page.tsx")
        logger.info("Sandbox reset: restored app/page.tsx")
    except Exception as e:
        logger.error(f"Failed to restore page.tsx: {e}")
        return {"success": False, "restored": restored, "removed": removed, "error": str(e)}

    comp_dir = os.path.join(SANDBOX_ROOT, "app", "components")
    if os.path.isdir(comp_dir):
        for fname in os.listdir(comp_dir):
            if fname not in _ORIGINAL_COMPONENTS:
                try:
                    fpath = os.path.join(comp_dir, fname)
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                        removed.append(f"app/components/{fname}")
                    elif os.path.isdir(fpath):
                        shutil.rmtree(fpath)
                        removed.append(f"app/components/{fname}/")
                except Exception as e:
                    logger.warning(f"Could not remove {fname}: {e}")

    logger.info(f"Sandbox reset complete — removed: {removed}")
    return {"success": True, "restored": restored, "removed": removed, "error": None}

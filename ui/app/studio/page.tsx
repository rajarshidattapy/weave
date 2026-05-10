'use client';

import { useCallback } from 'react';
import { toast } from 'sonner';
import { TopNav } from '@/components/top-nav';
import { LeftPanel } from '@/components/left-panel';
import { RightPanel } from '@/components/right-panel';
import { ResizableLayout } from '@/components/resizable-layout';
import { CommandPalette } from '@/components/command-palette';
import { FloatingActions } from '@/components/floating-actions';
import { WebContainerProvider } from '@/providers/webcontainer-provider';
import { AppProvider } from '@/providers/app-context';
import { useBackendWS, BackendEvent } from '@/hooks/use-backend-ws';

function StudioWithWS({ children }: { children: React.ReactNode }) {
  const handleEvent = useCallback((event: BackendEvent) => {
    if (event.type === 'indexing_progress') {
      const e = event as { type: string; phase: string; count?: number; current?: number; total?: number; component?: string };
      if (e.phase === 'discovery') {
        toast.info(`Discovered ${e.count ?? 0} component pages`, {
          id: 'indexing',
          duration: 3000,
        });
      } else if (e.phase === 'extraction' && e.component) {
        toast.loading(
          `Indexing ${e.current ?? '?'}/${e.total ?? '?'}: ${e.component}`,
          { id: 'indexing' }
        );
        if (e.current === e.total) {
          toast.success(`Indexed ${e.total} components`, {
            id: 'indexing',
            duration: 3000,
          });
        }
      }
    } else if (event.type === 'injection_complete') {
      const e = event as { type: string; data: { success: boolean; error?: string; installed_deps: string[] } };
      if (e.data.success) {
        const deps = e.data.installed_deps.length;
        toast.success(
          deps > 0
            ? `Component added — installed ${deps} package${deps > 1 ? 's' : ''}`
            : 'Component added to page',
          { duration: 3000 }
        );
      } else if (e.data.error) {
        toast.error(`Injection failed: ${e.data.error}`);
      }
    }
  }, []);

  useBackendWS(handleEvent);

  return <>{children}</>;
}

export default function StudioPage() {
  return (
    <WebContainerProvider>
      <AppProvider>
        <StudioWithWS>
          <main className="flex h-screen flex-col overflow-hidden bg-black">
            <TopNav />
            <ResizableLayout
              left={<LeftPanel />}
              right={<RightPanel />}
            />
            <CommandPalette />
            <FloatingActions />
          </main>
        </StudioWithWS>
      </AppProvider>
    </WebContainerProvider>
  );
}

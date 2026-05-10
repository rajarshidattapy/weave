'use client';

import { TopNav } from '@/components/top-nav';
import { LeftPanel } from '@/components/left-panel';
import { RightPanel } from '@/components/right-panel';
import { ResizableLayout } from '@/components/resizable-layout';
import { CommandPalette } from '@/components/command-palette';
import { FloatingActions } from '@/components/floating-actions';
import { WebContainerProvider } from '@/providers/webcontainer-provider';
import { AppProvider } from '@/providers/app-context';

export default function Home() {
  return (
    <WebContainerProvider>
      <AppProvider>
        <main className="flex h-screen flex-col overflow-hidden bg-black">
          <TopNav />
          <ResizableLayout 
            left={<LeftPanel />} 
            right={<RightPanel />} 
          />
          <CommandPalette />
          <FloatingActions />
        </main>
      </AppProvider>
    </WebContainerProvider>
  );
}

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth, WebContainer } from '@webcontainer/api';

interface WebContainerContextType {
  isReady: boolean;
  isInitializing: boolean;
  error: string | null;
  webcontainerInstance: WebContainer | null;
}

const WebContainerContext = createContext<WebContainerContextType | undefined>(undefined);

export function WebContainerProvider({ children }: { children: React.ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [webcontainerInstance, setWebcontainerInstance] = useState<WebContainer | null>(null);

  useEffect(() => {
    let instance: WebContainer | null = null;
    const initializeWebContainer = async () => {
      // Disabled WebContainer boot since we are running the local iframe directly.
      // WebContainers require strict Cross-Origin Isolation headers which block local cross-port iframes.
      setIsInitializing(false);
      setIsReady(false);
    };

    initializeWebContainer();

    return () => {
      if (instance) {
        instance.teardown();
      }
    };
  }, []);

  return (
    <WebContainerContext.Provider value={{ isReady, isInitializing, error, webcontainerInstance }}>
      {children}
    </WebContainerContext.Provider>
  );
}

export function useWebContainer() {
  const context = useContext(WebContainerContext);
  if (context === undefined) {
    throw new Error('useWebContainer must be used within WebContainerProvider');
  }
  return context;
}

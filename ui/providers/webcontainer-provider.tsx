'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth } from '@webcontainer/api';

interface WebContainerContextType {
  isReady: boolean;
  isInitializing: boolean;
  error: string | null;
}

const WebContainerContext = createContext<WebContainerContextType | undefined>(undefined);

export function WebContainerProvider({ children }: { children: React.ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeWebContainer = async () => {
      try {
        setIsInitializing(true);
        // Initialize WebContainer auth
        await auth.init({
          clientId: 'wc_api_rajarshidattapy_5ee426531513fe05951db62afa8fccd8',
          scope: '',
        });
        setIsReady(true);
        setError(null);
      } catch (err) {
        console.error('[v0] WebContainer initialization error:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize WebContainer');
        setIsReady(false);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeWebContainer();
  }, []);

  return (
    <WebContainerContext.Provider value={{ isReady, isInitializing, error }}>
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

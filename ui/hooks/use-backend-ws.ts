'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

// Resolve once at module load — must NOT go through the HTTP proxy path.
// WebSocket requires a direct connection to the backend.
const WS_URL = (() => {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';
  return base.replace(/^http/, 'ws') + '/ws';
})();

export interface IndexingProgress {
  type: 'indexing_progress';
  phase: 'discovery' | 'extraction';
  count?: number;
  current?: number;
  total?: number;
  component?: string;
}

export interface InjectionComplete {
  type: 'injection_complete';
  data: {
    success: boolean;
    component_id: string;
    modified_files: string[];
    installed_deps: string[];
    error?: string;
  };
}

export type BackendEvent =
  | IndexingProgress
  | InjectionComplete
  | { type: string; [key: string]: unknown };

export function useBackendWS(onEvent?: (event: BackendEvent) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const onEventRef = useRef(onEvent);
  const [connected, setConnected] = useState(false);

  // Keep callback ref fresh without reconnecting
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  const send = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    let socket: WebSocket;
    let retryTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      try {
        socket = new WebSocket(WS_URL);
        wsRef.current = socket;

        socket.onopen = () => setConnected(true);

        socket.onmessage = (e) => {
          try {
            const event = JSON.parse(e.data) as BackendEvent;
            onEventRef.current?.(event);
          } catch {}
        };

        socket.onclose = () => {
          setConnected(false);
          // Retry after 3 s if backend goes away
          retryTimeout = setTimeout(connect, 3000);
        };

        socket.onerror = () => {
          setConnected(false);
        };
      } catch {
        retryTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      clearTimeout(retryTimeout);
      socket?.close();
    };
  }, []);

  return { connected, send };
}

'use client';

import { useEffect, useState, useRef } from 'react';
import { useWebContainer } from '@/providers/webcontainer-provider';
import { motion } from 'framer-motion';
import { Terminal, Loader2 } from 'lucide-react';

export function WebContainerPreview() {
  const { isReady, isInitializing, webcontainerInstance } = useWebContainer();
  const [url, setUrl] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [status, setStatus] = useState<'booting' | 'fetching' | 'mounting' | 'installing' | 'starting' | 'ready' | 'error'>('booting');
  const logsEndRef = useRef<HTMLDivElement>(null);

  const appendLog = (log: string) => {
    setLogs((prev) => [...prev, log]);
  };

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  useEffect(() => {
    if (!isReady || !webcontainerInstance) {
      setStatus('booting');
      return;
    }

    let isMounted = true;

    const startDevEnvironment = async () => {
      try {
        setStatus('fetching');
        appendLog('Fetching project files from local system...');
        
        const res = await fetch('/api/fs');
        if (!res.ok) throw new Error('Failed to fetch file system');
        const { tree } = await res.json();
        
        if (!isMounted) return;

        setStatus('mounting');
        appendLog('Mounting files to WebContainer...');
        await webcontainerInstance.mount(tree);

        if (!isMounted) return;

        setStatus('installing');
        appendLog('Running npm install...');
        const installProcess = await webcontainerInstance.spawn('npm', ['install']);
        
        installProcess.output.pipeTo(new WritableStream({
          write(data) {
            appendLog(data);
          }
        }));

        const installExitCode = await installProcess.exit;
        if (installExitCode !== 0) {
          throw new Error('npm install failed');
        }

        if (!isMounted) return;

        setStatus('starting');
        appendLog('Running npm run dev...');
        const devProcess = await webcontainerInstance.spawn('npm', ['run', 'dev']);
        
        devProcess.output.pipeTo(new WritableStream({
          write(data) {
            appendLog(data);
          }
        }));

        webcontainerInstance.on('server-ready', (port, serverUrl) => {
          if (isMounted) {
            appendLog(`Server ready at ${serverUrl}`);
            setUrl(serverUrl);
            setStatus('ready');
          }
        });

      } catch (err: any) {
        if (isMounted) {
          console.error(err);
          appendLog(`Error: ${err.message}`);
          setStatus('error');
        }
      }
    };

    startDevEnvironment();

    return () => {
      isMounted = false;
    };
  }, [isReady, webcontainerInstance]);

  if (status === 'ready' && url) {
    return (
      <iframe 
        src={url} 
        className="w-full h-full border-none bg-white" 
        title="WebContainer Preview" 
        allow="cross-origin-isolated"
      />
    );
  }

  return (
    <div className="flex flex-col h-full bg-black/90 p-4 font-mono text-xs text-green-400 overflow-hidden">
      <div className="flex items-center gap-2 mb-4 text-white/50 border-b border-white/10 pb-2 flex-shrink-0">
        {status === 'error' ? <Terminal className="h-4 w-4 text-red-500" /> : <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
        <span className="uppercase tracking-wider">
          {status === 'error' ? 'Environment Error' : 'Initializing Sandbox Environment...'}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-1">
        {logs.map((log, i) => (
          <div key={i} className="break-all whitespace-pre-wrap leading-relaxed">{log}</div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}

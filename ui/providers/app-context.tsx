'use client';

import React, { createContext, useContext, useState } from 'react';

export interface Component {
  id: string;
  title: string;
  source: 'shadcn' | 'aceternity' | 'magic' | 'watermelon';
  tags: string[];
  compatibility: number;
  preview: string;
}

export interface Workspace {
  id: string;
  name: string;
  components: Component[];
}

interface AppContextType {
  currentWorkspace: Workspace;
  setCurrentWorkspace: (workspace: Workspace) => void;
  addedComponents: Component[];
  addComponent: (component: Component) => void;
  removeComponent: (id: string) => void;
  prompt: string;
  setPrompt: (prompt: string) => void;
  selectedSource: string;
  setSelectedSource: (source: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const INITIAL_WORKSPACE: Workspace = {
  id: '1',
  name: 'Landing Page',
  components: [],
};

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace>(INITIAL_WORKSPACE);
  const [addedComponents, setAddedComponents] = useState<Component[]>([]);
  const [prompt, setPrompt] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');

  const addComponent = (component: Component) => {
    setAddedComponents((prev) => [...prev, { ...component, id: `${component.id}-${Date.now()}` }]);
  };

  const removeComponent = (id: string) => {
    setAddedComponents((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <AppContext.Provider
      value={{
        currentWorkspace,
        setCurrentWorkspace,
        addedComponents,
        addComponent,
        removeComponent,
        prompt,
        setPrompt,
        selectedSource,
        setSelectedSource,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

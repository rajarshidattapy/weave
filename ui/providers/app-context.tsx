'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  retrieveComponents,
  integrateComponent,
  fixError as apiFix,
  getSandboxContext,
  BackendComponent,
} from '@/lib/api';

// -----------------------------------------------------------------------
// Legacy Component type (kept for UI compatibility)
// -----------------------------------------------------------------------
export interface Component {
  id: string;
  backendId: string;        // original backend component ID used for injection
  title: string;
  source: string;
  tags: string[];
  compatibility: number;
  preview: string;
  description?: string;
}

export interface Workspace {
  id: string;
  name: string;
  components: Component[];
}

// -----------------------------------------------------------------------
// Context shape
// -----------------------------------------------------------------------
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

  // Search
  searchResults: BackendComponent[];
  isSearching: boolean;
  expandedTags: string[];
  search: (prompt: string) => Promise<void>;

  // Inject
  injectingId: string | null;
  inject: (component: BackendComponent) => Promise<void>;

  // Fix pasted error
  fixError: (errorText: string) => Promise<{ success: boolean; patches: { file: string; applied: boolean }[] }>;
  isFixing: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const INITIAL_WORKSPACE: Workspace = {
  id: '1',
  name: 'Landing Page',
  components: [],
};

// -----------------------------------------------------------------------
// Provider
// -----------------------------------------------------------------------
export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace>(INITIAL_WORKSPACE);
  const [addedComponents, setAddedComponents] = useState<Component[]>([]);
  const [prompt, setPrompt] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');

  const [searchResults, setSearchResults] = useState<BackendComponent[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [expandedTags, setExpandedTags] = useState<string[]>([]);
  const [injectingId, setInjectingId] = useState<string | null>(null);
  const [isFixing, setIsFixing] = useState(false);

  const addComponent = (component: Component) => {
    setAddedComponents((prev) => [
      ...prev,
      { ...component, id: `${component.id}-${Date.now()}` },
    ]);
  };

  const removeComponent = (id: string) => {
    setAddedComponents((prev) => prev.filter((c) => c.id !== id));
  };

  // Search: call backend /retrieve, apply source filter client-side
  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setIsSearching(true);
    try {
      const context = await getSandboxContext();
      const res = await retrieveComponents(query, context || undefined);
      let results = res.components;
      if (selectedSource !== 'all') {
        results = results.filter(
          (c) =>
            (c.source_library || '').toLowerCase().includes(selectedSource.toLowerCase())
        );
      }
      setSearchResults(results);
      setExpandedTags(res.expanded_tags);
    } catch (err) {
      console.error('[weave] search failed:', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [selectedSource]);

  // Inject: use agentic pipeline (plan → files → deps → AST → validate → fix)
  const inject = useCallback(async (component: BackendComponent) => {
    setInjectingId(component.id);
    try {
      const res = await integrateComponent(component.id);
      if (res.success || res.files_created.length > 0) {
        const mapped: Component = {
          id: component.id,
          backendId: component.id,
          title: component.name,
          source: component.source_library || 'unknown',
          tags: component.tags || [],
          compatibility: 100,
          preview: '',
          description: component.description || '',
        };
        addComponent(mapped);
      } else {
        console.warn('[weave] integrate error:', res.error);
      }
    } catch (err) {
      console.error('[weave] integrate failed:', err);
    } finally {
      setInjectingId(null);
    }
  }, []);

  const fixError = useCallback(async (errorText: string) => {
    setIsFixing(true);
    try {
      return await apiFix(errorText);
    } catch {
      return { success: false, patches: [] };
    } finally {
      setIsFixing(false);
    }
  }, []);

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
        searchResults,
        isSearching,
        expandedTags,
        search,
        injectingId,
        inject,
        fixError,
        isFixing,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}

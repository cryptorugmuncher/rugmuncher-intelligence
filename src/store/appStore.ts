/**
 * App State Management (Zustand)
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Wallet, Investigation, SystemStats } from '../types';

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  authToken: string | null;
  setUser: (user: User | null) => void;
  setAuthenticated: (value: boolean) => void;
  setAuthToken: (token: string | null) => void;
  logout: () => void;

  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  currentPage: string;
  setCurrentPage: (page: string) => void;
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;

  // Data
  wallets: Wallet[];
  setWallets: (wallets: Wallet[]) => void;
  addWallet: (wallet: Wallet) => void;

  investigations: Investigation[];
  setInvestigations: (investigations: Investigation[]) => void;
  addInvestigation: (investigation: Investigation) => void;

  currentInvestigation: Investigation | null;
  setCurrentInvestigation: (investigation: Investigation | null) => void;

  // System
  stats: SystemStats | null;
  setStats: (stats: SystemStats) => void;
  backendStatus: 'connected' | 'disconnected' | 'checking';
  setBackendStatus: (status: 'connected' | 'disconnected' | 'checking') => void;

  // Loading states
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  // Error handling
  error: string | null;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Auth
      user: null,
      isAuthenticated: false,
      authToken: localStorage.getItem('access_token'),
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAuthenticated: (value) => set({ isAuthenticated: value }),
      setAuthToken: (token) => {
        if (token) {
          localStorage.setItem('access_token', token);
        } else {
          localStorage.removeItem('access_token');
        }
        set({ authToken: token });
      },
      logout: () => {
        localStorage.removeItem('access_token');
        set({ user: null, isAuthenticated: false, authToken: null });
      },

      // UI
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      currentPage: 'dashboard',
      setCurrentPage: (page) => set({ currentPage: page }),
      theme: 'dark',
      setTheme: (theme) => set({ theme }),

      // Data
      wallets: [],
      setWallets: (wallets) => set({ wallets }),
      addWallet: (wallet) => set((state) => ({ wallets: [wallet, ...state.wallets] })),

      investigations: [],
      setInvestigations: (investigations) => set({ investigations }),
      addInvestigation: (investigation) =>
        set((state) => ({ investigations: [investigation, ...state.investigations] })),

      currentInvestigation: null,
      setCurrentInvestigation: (investigation) => set({ currentInvestigation: investigation }),

      // System
      stats: null,
      setStats: (stats) => set({ stats }),
      backendStatus: 'checking',
      setBackendStatus: (status) => set({ backendStatus: status }),

      // Loading
      isLoading: false,
      setIsLoading: (loading) => set({ isLoading: loading }),

      // Error
      error: null,
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: 'rmi-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        authToken: state.authToken,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);

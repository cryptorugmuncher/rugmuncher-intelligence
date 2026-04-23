/**
 * Backend Connection Hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { db } from '../services/supabase';
import { useAppStore } from '../store/appStore';

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const result = await api.health();
      return result;
    },
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });
};

// Wallet analysis hook
export const useWalletAnalysis = () => {
  const setError = useAppStore((state) => state.setError);

  return useMutation({
    mutationFn: async ({ address, chain }: { address: string; chain?: string }) => {
      const result = await api.analyzeWallet(address, chain);
      return result;
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to analyze wallet');
    },
  });
};

// Wallet lookup hook (uses Dragonfly cache)
export const useWalletLookup = (address: string, chain: string = 'ethereum') => {
  return useQuery({
    queryKey: ['wallet', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      const result = await api.lookupWallet(address, chain);
      return result;
    },
    enabled: address.length >= 10,
    staleTime: 5 * 60 * 1000, // 5 minutes - matches Dragonfly TTL
    gcTime: 10 * 60 * 1000,
  });
};

// AI analysis hook
export const useAIAnalysis = () => {
  const setError = useAppStore((state) => state.setError);

  return useMutation({
    mutationFn: async ({
      address,
      chain,
      tier,
    }: {
      address: string;
      chain?: string;
      tier?: string;
    }) => {
      const result = await api.aiAnalyze(address, chain, tier);
      return result;
    },
    onError: (error: any) => {
      setError(error.message || 'AI analysis failed');
    },
  });
};

// Pattern detection hook
export const usePatternDetection = () => {
  return useMutation({
    mutationFn: async ({ address, chain }: { address: string; chain?: string }) => {
      const result = await api.detectPatterns(address, chain);
      return result;
    },
  });
};

// System stats hook
export const useSystemStats = () => {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const result = await api.getStats();
      return result;
    },
    refetchInterval: 60000, // Refresh every minute
  });
};

// Supabase wallets hook
export const useWallets = () => {
  return useQuery({
    queryKey: ['wallets'],
    queryFn: async () => {
      const { data, error } = await db.wallets.getAll();
      if (error) throw error;
      return data || [];
    },
  });
};

// Supabase investigations hook
export const useInvestigations = () => {
  return useQuery({
    queryKey: ['investigations'],
    queryFn: async () => {
      const { data, error } = await db.investigations.getAll();
      if (error) throw error;
      return data || [];
    },
  });
};

// Create investigation mutation
export const useCreateInvestigation = () => {
  const queryClient = useQueryClient();
  const addInvestigation = useAppStore((state) => state.addInvestigation);

  return useMutation({
    mutationFn: async (investigation: {
      title: string;
      description?: string;
      wallet_addresses?: string[];
      status?: string;
    }) => {
      const { data, error } = await db.investigations.create(investigation);
      if (error) throw error;
      return data?.[0];
    },
    onSuccess: (data) => {
      if (data) {
        addInvestigation(data);
        queryClient.invalidateQueries({ queryKey: ['investigations'] });
      }
    },
  });
};

// Evidence hook
export const useEvidence = () => {
  return useQuery({
    queryKey: ['evidence'],
    queryFn: async () => {
      const { data, error } = await db.evidence.getAll();
      if (error) throw error;
      return data || [];
    },
  });
};

// Create wallet mutation
export const useCreateWallet = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (wallet: {
      address: string;
      chain: string;
      label?: string;
      status?: string;
    }) => {
      const { data, error } = await db.wallets.create(wallet);
      if (error) throw error;
      return data?.[0];
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
    },
  });
};

/**
 * Advanced Analytics Hooks
 * Multi-model AI routing for cost-efficient intelligence
 */
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';

// Smart model selection based on complexity
const selectModel = (complexity: 'low' | 'medium' | 'high' | 'forensic') => {
  switch (complexity) {
    case 'low':
      return { model: 'gpt-4o-mini', provider: 'openai', cost: 0.002 };
    case 'medium':
      return { model: 'gpt-4o', provider: 'openai', cost: 0.015 };
    case 'high':
      return { model: 'claude-3-5-sonnet-20241022', provider: 'anthropic', cost: 0.08 };
    case 'forensic':
      return { model: 'claude-3-opus-20240229', provider: 'anthropic', cost: 0.25 };
    default:
      return { model: 'gpt-4o-mini', provider: 'openai', cost: 0.002 };
  }
};

// Wallet clusters hook (ELITE+)
export const useWalletClusters = (_options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['wallet-clusters'],
    queryFn: async () => {
      const result = await api.getWalletClusters();
      return result;
    },
    enabled: _options?.enabled ?? true,
    staleTime: 5 * 60 * 1000,
  });
};

// Cluster analysis hook
export const useClusterAnalysis = (_options?: { enabled?: boolean }) => {
  return useMutation({
    mutationFn: async ({ address }: { address: string }) => {
      const result = await api.analyzeCluster(address);
      return result;
    },
  });
};

// Network graph hook
export const useNetworkGraph = (
  address: string,
  chain: string,
  options?: { enabled?: boolean; hops?: number }
) => {
  return useQuery({
    queryKey: ['network-graph', address, chain, options?.hops],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Route to backend which handles multi-model processing
      const result = await api.getNetworkGraph(address, chain, options?.hops || 3);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// Bundle detection hook
export const useBundleDetection = (
  address: string,
  chain: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['bundle-detection', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Uses GPT-4o for pattern detection, GPT-4o-mini for initial screening
      const result = await api.detectBundles(address, chain);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// Fresh wallet analysis hook
export const useFreshWalletAnalysis = (
  address: string,
  chain: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['fresh-wallet', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Uses GPT-4o-mini for data crunching, GPT-4o for risk assessment
      const result = await api.analyzeFreshWallets(address, chain);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// Sniper detection hook
export const useSniperDetection = (
  address: string,
  chain: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['sniper-detection', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Uses GPT-4o-mini for block analysis, GPT-4o for pattern matching
      const result = await api.detectSnipers(address, chain);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// Copy trading detection hook
export const useCopyTradingDetection = (
  address: string,
  chain: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['copy-trading', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Uses GPT-4o for correlation analysis
      const result = await api.detectCopyTrading(address, chain);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// Bot farm detection hook
export const useBotFarmDetection = (
  address: string,
  chain: string,
  options?: { enabled?: boolean }
) => {
  return useQuery({
    queryKey: ['bot-farm', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      // Uses GPT-4o for behavioral fingerprinting
      const result = await api.detectBotFarms(address, chain);
      return result;
    },
    enabled: options?.enabled ?? false,
    staleTime: 5 * 60 * 1000,
  });
};

// AI analysis with smart model routing
export const useSmartAIAnalysis = () => {
  return useMutation({
    mutationFn: async ({
      address,
      chain,
      tier,
      complexity,
    }: {
      address: string;
      chain?: string;
      tier?: string;
      complexity?: 'low' | 'medium' | 'high' | 'forensic';
    }) => {
      // Select model based on complexity and user tier
      const selectedModel = selectModel(complexity || 'medium');
      
      // Tier-based routing for cost control
      if (tier === 'FREE') {
        throw new Error('AI analysis requires BASIC+ tier');
      }
      if (tier === 'BASIC' && complexity === 'high') {
        throw new Error('Deep analysis requires PRO tier');
      }
      if (tier !== 'ELITE' && tier !== 'ENTERPRISE' && complexity === 'forensic') {
        throw new Error('Forensic analysis requires ELITE tier');
      }

      const result = await api.aiAnalyze(address, chain || 'ethereum', selectedModel.model);
      return {
        ...result,
        model_used: selectedModel.model,
        cost_estimate: selectedModel.cost,
      };
    },
  });
};

// Muncher Map export mutation
export const useExportMuncherMap = () => {
  return useMutation({
    mutationFn: async ({
      format,
      nodes,
      edges,
    }: {
      format: 'png' | 'svg' | 'pdf' | 'gexf';
      nodes: any[];
      edges: any[];
    }) => {
      // Uses GPT-4o-mini for data formatting, no LLM for image export
      const result = await api.exportGraph({ format, nodes, edges });
      return result;
    },
  });
};

// Whale tracking hook
export const useWhaleTracking = (options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['whale-tracking'],
    queryFn: async () => {
      // Uses GPT-4o-mini for sorting/filtering, GPT-4o for pattern insights
      const result = await api.getWhaleActivity();
      return result;
    },
    enabled: options?.enabled ?? true,
    refetchInterval: 60000, // 1 minute
    staleTime: 30000,
  });
};

// Predictive analytics hook (ELITE+ only)
export const usePredictiveAnalytics = (
  address: string,
  chain: string,
  tier?: string
) => {
  return useQuery({
    queryKey: ['predictive', address, chain],
    queryFn: async () => {
      if (!address || address.length < 10) return null;
      if (tier !== 'ELITE' && tier !== 'ENTERPRISE') {
        throw new Error('Predictive analytics requires ELITE tier');
      }
      // Uses GPT-4o for prediction modeling
      const result = await api.getPredictions(address, chain);
      return result;
    },
    enabled: tier === 'ELITE' || tier === 'ENTERPRISE',
    staleTime: 10 * 60 * 1000,
  });
};

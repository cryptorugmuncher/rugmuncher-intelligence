/**
 * Type Definitions
 */

export interface Wallet {
  id?: string;
  address: string;
  chain: string;
  risk_score?: number;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  tags?: string[];
  balance?: number;
  tx_count?: number;
  scanned_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Investigation {
  id?: string;
  title: string;
  description?: string;
  wallet_addresses: string[];
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED';
  tier: 'FREE' | 'BASIC' | 'PRO' | 'ENTERPRISE';
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  findings?: any;
  created_by?: string;
  assigned_to?: string;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
}

export interface Evidence {
  id?: string;
  investigation_id: string;
  wallet_address?: string;
  evidence_type: 'TRANSACTION' | 'CONTRACT' | 'SOCIAL' | 'OSINT' | 'AI_ANALYSIS' | 'USER_SUBMITTED';
  source: string;
  content: any;
  confidence: number;
  verification_status?: 'UNVERIFIED' | 'PENDING' | 'VERIFIED' | 'REJECTED';
  chain_of_custody?: any[];
  collected_at?: string;
  verified_at?: string;
  verified_by?: string;
}

export interface RiskPattern {
  type: string;
  confidence: number;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface AIAnalysis {
  analysis: string;
  model: string;
  provider: string;
  latency_ms: number;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  role: 'USER' | 'ANALYST' | 'ADMIN';
  tier: 'FREE' | 'BASIC' | 'PRO' | 'ELITE' | 'ENTERPRISE';
  wallet_address?: string;
  reputation_score?: number;
  badges?: string[];
  created_at?: string;
}

export interface SystemStats {
  total_investigations: number;
  total_wallets: number;
  total_evidence: number;
  api_calls_today: number;
  api_calls_month: number;
  cache_hit_rate: number;
  average_response_time_ms: number;
  dragonfly_status: 'connected' | 'disconnected';
  supabase_status: 'connected' | 'disconnected';
  active_providers: number;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}

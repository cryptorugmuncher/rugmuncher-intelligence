// ============================================================================
// RMI Platform - TypeScript Types for Lovable Integration
// ============================================================================

// ============================================================================
// ENUMS
// ============================================================================

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'safe' | 'unknown';
export type InvestigationStatus = 'active' | 'completed' | 'archived';
export type Chain = 'solana' | 'ethereum' | 'bsc' | 'arbitrum' | 'base';
export type APIProvider = 'birdeye' | 'helius' | 'shyft' | 'quicknode' | 'alchemy' | 'moralis' | 'bitquery';
export type PackageTier = 'starter' | 'pro' | 'whale' | 'enterprise';
export type KOLPlatform = 'twitter' | 'telegram' | 'youtube' | 'discord';
export type TransparencyGrade = 'A+' | 'A' | 'A-' | 'B+' | 'B' | 'B-' | 'C+' | 'C' | 'C-' | 'D' | 'F';

// ============================================================================
// USER & PROFILE
// ============================================================================

export interface Profile {
  id: string;
  wallet_address?: string;
  display_name?: string;
  avatar_url?: string;
  is_crm_holder: boolean;
  crm_balance: number;
  subscription_tier: 'free' | 'starter' | 'pro' | 'whale';
  scans_remaining: number;
  total_scans_used: number;
  reputation_score: number;
  created_at: string;
  updated_at: string;
}

export interface UserStats {
  investigations_count: number;
  scans_used: number;
  api_credits_total: number;
  api_credits_used: number;
  alerts_triggered: number;
}

// ============================================================================
// INVESTIGATIONS
// ============================================================================

export interface Investigation {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  token_address?: string;
  token_symbol?: string;
  chain: Chain;
  status: InvestigationStatus;
  risk_level: RiskLevel;
  tags: string[];
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface InvestigationSummary {
  id: string;
  title: string;
  token_symbol?: string;
  risk_level: RiskLevel;
  status: InvestigationStatus;
  evidence_count: number;
  wallet_count: number;
  created_at: string;
}

// ============================================================================
// EVIDENCE
// ============================================================================

export interface Evidence {
  id: string;
  investigation_id: string;
  user_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  content_hash: string;
  source?: string;
  description?: string;
  metadata: Record<string, any>;
  processed: boolean;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  extracted_text?: string;
  ai_summary?: string;
  created_at: string;
}

export interface EvidenceUpload {
  file: File;
  description?: string;
  source?: string;
}

// ============================================================================
// WALLET ANALYSIS
// ============================================================================

export interface WalletAnalysis {
  id: string;
  investigation_id: string;
  wallet_address: string;
  chain: Chain;
  analysis_type: string;
  risk_score: number;
  risk_level: RiskLevel;
  tags: string[];
  connections: WalletConnections;
  transaction_stats: TransactionStats;
  token_holdings: TokenHolding[];
  findings: WalletFindings;
  related_scams: string[];
  behavioral_profile: BehavioralProfile;
  analyzed_at: string;
  expires_at: string;
}

export interface WalletConnections {
  incoming: Connection[];
  outgoing: Connection[];
  unique_counterparties: number;
  cluster_wallets: string[];
}

export interface Connection {
  address: string;
  type: string;
  transaction_count: number;
  total_volume_usd: number;
  first_transaction: string;
  last_transaction: string;
}

export interface TransactionStats {
  total_transactions: number;
  total_volume_usd: number;
  avg_transaction_size: number;
  largest_transaction: number;
  first_seen: string;
  last_active: string;
  activity_period_days: number;
}

export interface TokenHolding {
  token_address: string;
  token_symbol: string;
  balance: number;
  value_usd: number;
  percentage_of_supply: number;
}

export interface WalletFindings {
  risk_factors: RiskFactor[];
  positive_signals: PositiveSignal[];
  behavioral_patterns: string[];
  flags: string[];
}

export interface RiskFactor {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  evidence?: string;
}

export interface PositiveSignal {
  type: string;
  description: string;
}

export interface BehavioralProfile {
  trading_style: string;
  holding_period_avg: number;
  profit_loss_ratio: number;
  risk_tolerance: string;
  sophistication_level: string;
}

// ============================================================================
// TOKEN ANALYSIS
// ============================================================================

export interface TokenAnalysis {
  id: string;
  investigation_id: string;
  token_address: string;
  chain: Chain;
  token_symbol?: string;
  token_name?: string;
  analysis_type: string;
  risk_score: number;
  risk_level: RiskLevel;
  mint_authority?: string;
  freeze_authority?: string;
  supply_info: SupplyInfo;
  holder_analysis: HolderAnalysis;
  liquidity_analysis: LiquidityAnalysis;
  contract_flags: ContractFlag[];
  findings: TokenFindings;
  analyzed_at: string;
  expires_at: string;
}

export interface SupplyInfo {
  total_supply: number;
  circulating_supply: number;
  burned_amount: number;
  mintable: boolean;
  freeze_enabled: boolean;
}

export interface HolderAnalysis {
  total_holders: number;
  top_holders: TopHolder[];
  concentration_risk: string;
  whale_count: number;
  new_holders_24h: number;
}

export interface TopHolder {
  address: string;
  balance: number;
  percentage: number;
  label?: string;
}

export interface LiquidityAnalysis {
  total_liquidity_usd: number;
  primary_dex: string;
  liquidity_locked: boolean;
  lock_duration_days?: number;
  lp_token_burned: boolean;
}

export interface ContractFlag {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  recommendation?: string;
}

export interface TokenFindings {
  red_flags: string[];
  green_flags: string[];
  warnings: string[];
}

// ============================================================================
// CLUSTER ANALYSIS
// ============================================================================

export interface ClusterAnalysis {
  id: string;
  investigation_id: string;
  cluster_id: string;
  wallets: string[];
  detection_methods: string[];
  confidence_score: number;
  cluster_type: string;
  behavior_tags: string[];
  transaction_patterns: TransactionPattern;
  funding_sources: string[];
  common_counterparties: string[];
  temporal_analysis: TemporalAnalysis;
  related_clusters: string[];
  analyzed_at: string;
  expires_at: string;
}

export interface TransactionPattern {
  pattern_type: string;
  frequency: string;
  avg_amount_usd: number;
  typical_hours: number[];
  coordination_signals: string[];
}

export interface TemporalAnalysis {
  first_seen: string;
  last_active: string;
  active_period_days: number;
  coordination_events: number;
  peak_activity_hours: number[];
}

// ============================================================================
// BUBBLE MAPS
// ============================================================================

export interface BubbleMap {
  id: string;
  investigation_id: string;
  center_wallet: string;
  depth: number;
  map_data: BubbleMapData;
  node_count: number;
  edge_count: number;
  cluster_count: number;
  interactive_html?: string;
  export_paths: {
    png?: string;
    svg?: string;
    json?: string;
  };
  created_at: string;
  expires_at: string;
}

export interface BubbleMapData {
  nodes: BubbleNode[];
  edges: BubbleEdge[];
}

export interface BubbleNode {
  id: string;
  type: 'center' | 'scammer' | 'exchange' | 'whale' | 'bot' | 'kol' | 'retail' | 'unknown';
  label: string;
  value: number;
  x?: number;
  y?: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface BubbleEdge {
  source: string;
  target: string;
  value: number;
  transactions: number;
  first_tx: string;
  last_tx: string;
  color?: string;
}

// ============================================================================
// KOL TRACKING
// ============================================================================

export interface KOLProfile {
  id: string;
  handle: string;
  platform: KOLPlatform;
  display_name?: string;
  bio?: string;
  follower_count: number;
  verified_wallets: string[];
  reputation_score: number;
  accuracy_score: number;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  rug_signals: number;
  tags: string[];
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface KOLWallet {
  id: string;
  kol_id: string;
  wallet_address: string;
  chain: Chain;
  verification_status: 'verified' | 'unverified' | 'pending';
  verification_method?: string;
  first_seen?: string;
  last_active?: string;
  total_trades: number;
  pnl_30d: number;
  metadata: Record<string, any>;
}

export interface KOLCall {
  id: string;
  kol_id: string;
  token_address: string;
  token_symbol?: string;
  call_type: 'buy' | 'sell' | 'shill' | 'warn' | 'neutral';
  platform?: string;
  post_url?: string;
  timestamp: string;
  price_at_call?: number;
  current_price?: number;
  performance_24h?: number;
  performance_7d?: number;
  verified: boolean;
  wallet_activity_match?: boolean;
  metadata: Record<string, any>;
}

export interface KOLPosition {
  id: string;
  kol_id: string;
  wallet_address: string;
  token_address: string;
  token_symbol?: string;
  amount: number;
  value_usd: number;
  entry_price?: number;
  current_price?: number;
  unrealized_pnl: number;
  realized_pnl: number;
  first_acquired?: string;
  last_updated: string;
  is_active: boolean;
}

export interface KOLStats {
  total_kols: number;
  verified_kols: number;
  avg_accuracy: number;
  top_performers: KOLProfile[];
  recent_calls: KOLCall[];
}

// ============================================================================
// TRANSPARENCY TRACKER
// ============================================================================

export interface TransparencyScore {
  token_address: string;
  chain: Chain;
  token_symbol?: string;
  overall_score: number;
  overall_grade: TransparencyGrade;
  percentile_rank: number;
  category_scores: CategoryScores;
  red_flags: TransparencyFlag[];
  green_flags: TransparencyFlag[];
  team_info: TeamInfo;
  contract_info: ContractInfo;
  treasury_info: TreasuryInfo;
  audit_info: AuditInfo;
  roadmap_info: RoadmapInfo;
  assessed_at: string;
  expires_at: string;
}

export interface CategoryScores {
  team: number;
  contract: number;
  treasury: number;
  communication: number;
  audit: number;
  roadmap: number;
}

export interface TransparencyFlag {
  category: string;
  description: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  date_identified?: string;
}

export interface TeamInfo {
  members: TeamMember[];
  is_doxxed: boolean;
  linkedin_verified: boolean;
  previous_projects: string[];
}

export interface TeamMember {
  name?: string;
  role: string;
  twitter?: string;
  linkedin?: string;
  is_verified: boolean;
}

export interface ContractInfo {
  mint_authority_revoked: boolean;
  freeze_authority_revoked: boolean;
  upgrade_authority: string | null;
  is_verified: boolean;
  top_holders: TopHolder[];
  concentration_risk: string;
}

export interface TreasuryInfo {
  treasury_wallets: string[];
  total_value_usd: number;
  allocation: Record<string, number>;
  vesting_schedule?: string;
  transparency_score: number;
}

export interface AuditInfo {
  has_audit: boolean;
  audit_firm?: string;
  audit_date?: string;
  audit_url?: string;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
}

export interface RoadmapInfo {
  has_roadmap: boolean;
  roadmap_url?: string;
  milestones: Milestone[];
  completion_rate: number;
}

export interface Milestone {
  title: string;
  target_date?: string;
  completed: boolean;
  completed_date?: string;
}

// ============================================================================
// PREMIUM & PAYMENTS
// ============================================================================

export interface ScanPackage {
  id: string;
  name: string;
  package_type: string;
  scan_count: number;
  base_price_usd: number;
  crm_discount_percent: number;
  features: string[];
  is_active: boolean;
}

export interface ScanPurchase {
  id: string;
  user_id: string;
  package_id: string;
  scans_purchased: number;
  scans_remaining: number;
  amount_paid: number;
  currency: string;
  transaction_signature?: string;
  payment_status: 'pending' | 'paid' | 'failed';
  is_crm_holder: boolean;
  discount_applied: number;
  purchased_at: string;
  expires_at?: string;
}

export interface APIPackage {
  id: string;
  package_key: string;
  provider: APIProvider;
  tier: PackageTier;
  credits: number;
  bonus_credits: number;
  effective_credits: number;
  base_price_usd: number;
  discount_percent: number;
  final_price: number;
  price_per_1k: number;
  features: string[];
  rate_limit_per_min: number;
  validity_days: number;
  is_active: boolean;
}

export interface UserAPICredits {
  id: string;
  user_id: string;
  package_id: string;
  provider: APIProvider;
  credits_remaining: number;
  credits_used: number;
  utilization_percent: number;
  rate_limit_per_min: number;
  activated_at: string;
  expires_at: string;
  days_until_expiry: number;
  is_active: boolean;
}

export interface APIUsage {
  id: string;
  user_id: string;
  provider: APIProvider;
  endpoint?: string;
  credits_used: number;
  response_time_ms?: number;
  status_code?: number;
  timestamp: string;
}

export interface PendingPayment {
  id: string;
  payment_id: string;
  user_id: string;
  item_type: 'scan_pack' | 'api_credits' | 'subscription';
  item_id?: string;
  amount_usdc: number;
  recipient_wallet: string;
  status: 'pending' | 'paid' | 'expired' | 'failed';
  transaction_signature?: string;
  created_at: string;
  expires_at: string;
  completed_at?: string;
}

export interface PricingBreakdown {
  package: string;
  provider: string;
  base_price: number;
  base_discount: number;
  crm_discount: number;
  total_discount: number;
  final_price: number;
  savings_vs_retail: {
    retail_cost: number;
    your_price: number;
    total_savings: number;
    savings_percent: number;
  };
  crm_holder_info: CRMHolderInfo;
  payment_wallet: string;
  currency: string;
}

export interface CRMHolderInfo {
  wallet: string;
  is_crm_holder: boolean;
  crm_balance: number;
  additional_discount: number;
  discount_tier: 'None' | 'Bronze' | 'Silver' | 'Gold' | 'VIP';
}

// ============================================================================
// NOTIFICATIONS & ALERTS
// ============================================================================

export interface Notification {
  id: string;
  user_id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  data: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export interface AlertSubscription {
  id: string;
  user_id: string;
  alert_type: string;
  target_address?: string;
  target_type?: 'wallet' | 'token' | 'kol';
  conditions: AlertConditions;
  is_active: boolean;
  last_triggered?: string;
  created_at: string;
}

export interface AlertConditions {
  min_transaction_size?: number;
  risk_level_change?: boolean;
  new_cluster_detected?: boolean;
  kol_call_made?: boolean;
  price_change_percent?: number;
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    has_more?: boolean;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// ============================================================================
// UI COMPONENT PROPS
// ============================================================================

export interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

export interface WalletAddressProps {
  address: string;
  chain?: Chain;
  truncate?: boolean;
  truncateLength?: number;
  showCopy?: boolean;
  showExplorer?: boolean;
  className?: string;
}

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
  onClick?: () => void;
}

export interface InvestigationCardProps {
  investigation: InvestigationSummary;
  onClick: () => void;
  onDelete?: () => void;
}

export interface EvidenceCardProps {
  evidence: Evidence;
  onView: () => void;
  onDelete: () => void;
}

export interface BubbleMapVisualizationProps {
  data: BubbleMapData;
  onNodeClick?: (node: BubbleNode) => void;
  onEdgeClick?: (edge: BubbleEdge) => void;
  height?: number;
  width?: number;
  interactive?: boolean;
}

export interface ClusterVisualizationProps {
  clusters: ClusterAnalysis[];
  selectedCluster?: string;
  onClusterSelect?: (cluster: ClusterAnalysis) => void;
}

export interface KOLCardProps {
  kol: KOLProfile;
  onClick?: () => void;
  showStats?: boolean;
}

export interface TransparencyScoreProps {
  score: TransparencyScore;
  showDetails?: boolean;
  compareWith?: TransparencyScore;
}

export interface PackageCardProps {
  package: APIPackage | ScanPackage;
  isSelected?: boolean;
  isPopular?: boolean;
  onSelect: () => void;
  userDiscount?: number;
}

export interface LoadingStateProps {
  type: 'spinner' | 'skeleton' | 'pulse';
  count?: number;
  height?: number;
}

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

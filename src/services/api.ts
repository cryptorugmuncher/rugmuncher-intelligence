/**
 * Backend API Client
 * ==================
 * Connects to FastAPI backend with Dragonfly caching
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiClient {
  public client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL || undefined,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async health(): Promise<{ status: string; dragonfly: boolean; supabase: boolean }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Wallet analysis
  async analyzeWallet(address: string, chain: string = 'ethereum'): Promise<{
    address: string;
    risk_score: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    analysis: string;
    details: any;
  }> {
    const response = await this.client.post('/api/v1/investigation/wallet/analyze', {
      address,
      chain,
    });
    return response.data;
  }

  // Quick wallet lookup (uses Dragonfly cache)
  async lookupWallet(address: string, chain: string = 'ethereum'): Promise<any> {
    const response = await this.client.get('/api/v1/investigation/wallet/lookup', {
      params: { address, chain },
    });
    return response.data;
  }

  // Transaction tracing
  async traceTransactions(
    address: string,
    chain: string = 'ethereum',
    depth: number = 2
  ): Promise<any> {
    const response = await this.client.post('/api/v1/investigation/trace', {
      address,
      chain,
      depth,
    });
    return response.data;
  }

  // Cross-chain analysis
  async crossChainAnalysis(address: string): Promise<any> {
    const response = await this.client.post('/api/v1/investigation/cross-chain', {
      address,
    });
    return response.data;
  }

  // Pattern detection
  async detectPatterns(address: string, chain: string = 'ethereum'): Promise<{
    patterns: Array<{
      type: string;
      confidence: number;
      description: string;
    }>;
    risk_indicators: string[];
  }> {
    const response = await this.client.post('/api/v1/investigation/patterns', {
      address,
      chain,
    });
    return response.data;
  }

  // AI-powered analysis
  async aiAnalyze(address: string, chain: string = 'ethereum', tier: string = 'HIGH'): Promise<{
    analysis: string;
    model: string;
    provider: string;
    latency_ms: number;
  }> {
    const response = await this.client.post('/api/v1/investigation/ai-analyze', {
      address,
      chain,
      tier,
    });
    return response.data;
  }

  // Submit evidence
  async submitEvidence(evidence: {
    investigation_id?: string;
    wallet_address: string;
    evidence_type: string;
    source: string;
    content: any;
    confidence?: number;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/investigation/evidence', evidence);
    return response.data;
  }

  // Get investigation status
  async getInvestigationStatus(id: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/${id}/status`);
    return response.data;
  }

  // List investigations
  async listInvestigations(params?: {
    status?: string;
    tier?: string;
    limit?: number;
    offset?: number;
  }): Promise<any> {
    const response = await this.client.get('/api/v1/investigation/list', { params });
    return response.data;
  }

  // ═══════════ CASE MANAGEMENT (CRM) ═══════════

  async listCases(): Promise<{ cases: any[] }> {
    const response = await this.client.get('/api/v1/investigation/cases');
    return response.data;
  }

  async getCaseCRMFull(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/full`);
    return response.data;
  }

  async getCaseCRMTimeline(caseId: string): Promise<{ timeline: any[] }> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/timeline`);
    return response.data;
  }

  async getCaseCRMStats(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/stats`);
    return response.data;
  }

  async getCaseCRMEvidence(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/evidence`);
    return response.data;
  }

  async getCaseCRMWallets(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/wallets`);
    return response.data;
  }

  async getCaseCRMStructure(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/structure`);
    return response.data;
  }

  async getCaseCRMGraph(caseId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/investigation/cases/${caseId}/crm/graph`);
    return response.data;
  }

  // ═══════════ UNIVERSAL COMMENTS ═══════════
  async createComment(contentType: string, contentId: string, body: string, parentId?: string): Promise<any> {
    const response = await this.client.post('/api/v1/comments', {
      content_type: contentType,
      content_id: contentId,
      body,
      parent_id: parentId,
    });
    return response.data;
  }

  async listComments(contentType: string, contentId: string): Promise<{ comments: any[]; total: number }> {
    const response = await this.client.get('/api/v1/comments', {
      params: { content_type: contentType, content_id: contentId },
    });
    return response.data;
  }

  async upvoteComment(commentId: string): Promise<any> {
    const response = await this.client.post(`/api/v1/comments/${commentId}/upvote`);
    return response.data;
  }

  async deleteComment(commentId: string): Promise<any> {
    const response = await this.client.delete(`/api/v1/comments/${commentId}`);
    return response.data;
  }

  // ═══════════ ADMIN PUBLISH CONTROL ═══════════
  async getCaseCRMPublishStatus(caseId: string): Promise<{ published: boolean }> {
    const response = await this.client.get(`/api/v1/admin/cases/${caseId}/publish-status`);
    return response.data;
  }

  async publishCase(caseId: string, adminKey: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/cases/${caseId}/publish`, {}, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async unpublishCase(caseId: string, adminKey: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/cases/${caseId}/unpublish`, {}, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // Get system stats
  async getStats(): Promise<{
    total_investigations: number;
    total_wallets: number;
    api_calls_today: number;
    cache_hit_rate: number;
    dragonfly_status: string;
    supabase_status: string;
  }> {
    const response = await this.client.get('/api/v1/stats');
    return response.data;
  }

  // ============ ADVANCED ANALYTICS (MUNCHER MAPS) ============

  // Network graph for Muncher Maps
  async getNetworkGraph(address: string, chain: string, hops: number = 3): Promise<{
    nodes: Array<{
      id: string;
      type: string;
      x: number;
      y: number;
      risk: number;
      label: string;
    }>;
    edges: Array<{
      from: string;
      to: string;
      type: string;
      value: number;
    }>;
    metadata: {
      total_nodes: number;
      total_edges: number;
      cex_nodes: number;
      bridge_nodes: number;
      high_risk_nodes: number;
    };
  }> {
    const response = await this.client.post('/api/v1/analytics/network-graph', {
      address,
      chain,
      hops,
    });
    return response.data;
  }

  // Bundle detection - find coordinated wallet groups
  async detectBundles(address: string, chain: string): Promise<{
    bundles: Array<{
      id: number;
      size: number;
      wallets: string[];
      coordination_score: number;
      first_seen: string;
      total_volume: number;
      risk_level: string;
      pattern: string;
    }>;
    total_detected: number;
    largest_bundle_size: number;
  }> {
    const response = await this.client.post('/api/v1/analytics/bundles', {
      address,
      chain,
    });
    return response.data;
  }

  // Fresh wallet analysis - predict rugs by wallet age
  async analyzeFreshWallets(address: string, chain: string): Promise<{
    total_holders: number;
    fresh_wallets: number;
    fresh_percentage: number;
    avg_wallet_age_hours: number;
    funding_sources: Array<{
      source: string;
      count: number;
      percentage: number;
    }>;
    age_distribution: Array<{
      range: string;
      count: number;
      percentage: number;
    }>;
    risk_assessment: {
      score: number;
      level: string;
      factors: string[];
    };
  }> {
    const response = await this.client.post('/api/v1/analytics/fresh-wallets', {
      address,
      chain,
    });
    return response.data;
  }

  // Sniper detection - track first-block buyers
  async detectSnipers(address: string, chain: string): Promise<{
    snipers: Array<{
      address: string;
      entry_block: number;
      exit_block: number | null;
      hold_time: string;
      profit: string;
      gas_paid: number;
      entry_price: number;
      exit_price: number | null;
      dump_percentage: number;
      is_sniper: boolean;
    }>;
    total_snipers: number;
    avg_dump_time_minutes: number;
    total_sniper_profit_eth: number;
    dump_warning: boolean;
  }> {
    const response = await this.client.post('/api/v1/analytics/snipers', {
      address,
      chain,
    });
    return response.data;
  }

  // Copy trading detection
  async detectCopyTrading(address: string, chain: string): Promise<{
    copies: Array<{
      leader: string;
      followers: number;
      total_copy_volume: number;
      avg_delay_blocks: number;
      success_rate: number;
      pattern: string;
    }>;
    total_patterns: number;
    top_leader_volume: number;
  }> {
    const response = await this.client.post('/api/v1/analytics/copy-trading', {
      address,
      chain,
    });
    return response.data;
  }

  // Bot farm detection
  async detectBotFarms(address: string, chain: string): Promise<{
    bot_farms: Array<{
      size: number;
      wallets: string[];
      bot_probability: number;
      pattern_type: string;
      funding_source: string;
      total_volume: number;
      gas_patterns: {
        consistency_score: number;
        avg_variance: number;
      };
      timing_patterns: {
        inter_tx_avg_seconds: number;
        block_position_avg: number;
        time_clustering: number;
      };
    }>;
    total_farms: number;
    total_bot_wallets: number;
  }> {
    const response = await this.client.post('/api/v1/analytics/bot-farms', {
      address,
      chain,
    });
    return response.data;
  }

  // Export Muncher Map graph
  async exportGraph(params: {
    format: 'png' | 'svg' | 'pdf' | 'gexf';
    nodes: any[];
    edges: any[];
  }): Promise<{
    download_url: string;
    expires_at: string;
  }> {
    const response = await this.client.post('/api/v1/analytics/export-graph', params);
    return response.data;
  }

  // Whale activity tracking
  async getWhaleActivity(): Promise<{
    whales: Array<{
      address: string;
      label: string | null;
      net_volume_24h: number;
      trades_24h: number;
      avg_trade_size: number;
      latest_trade: {
        token: string;
        type: 'buy' | 'sell';
        amount: number;
        timestamp: string;
      };
    }>;
    total_volume_24h: number;
    buy_sell_ratio: number;
  }> {
    const response = await this.client.get('/api/v1/analytics/whales');
    return response.data;
  }

  // Predictive analytics (ELITE+)
  async getPredictions(address: string, chain: string): Promise<{
    rug_pull_probability: number;
    price_prediction_24h: {
      direction: 'up' | 'down' | 'stable';
      confidence: number;
      estimated_change_percent: number;
    };
    dump_warning: boolean;
    insider_trading_flag: boolean;
    top_signals: string[];
    model_confidence: number;
  }> {
    const response = await this.client.post('/api/v1/analytics/predictions', {
      address,
      chain,
    });
    return response.data;
  }

  // Wallet clusters (ELITE+)
  async getWalletClusters(): Promise<any[]> {
    const response = await this.client.get('/api/v1/analytics/clusters');
    return response.data;
  }

  // Cluster analysis (ELITE+)
  async analyzeCluster(address: string): Promise<{
    cluster_id: string;
    related_wallets: string[];
    confidence: number;
    analysis: string;
  }> {
    const response = await this.client.post('/api/v1/analytics/cluster/analyze', {
      address,
    });
    return response.data;
  }

  // ═══════════ RUG MUNCH INTELLIGENCE CHAT ═══════════

  async initChatSession(sessionId?: string): Promise<{
    session_id: string;
    messages_used: number;
    messages_remaining: number;
    created_at: string;
  }> {
    const response = await this.client.post('/api/v1/intel/chat', {
      session_id: sessionId,
    });
    return response.data;
  }

  async sendChatMessage(message: string, sessionId?: string): Promise<{
    type: string;
    response?: string;
    message?: string;
    formatted?: {
      text: string;
      structured?: any;
      risk_score?: number;
    };
    session: {
      session_id: string;
      messages_used: number;
      messages_remaining: number;
    };
  }> {
    const response = await this.client.post('/api/v1/intel/chat/message', {
      message,
      session_id: sessionId,
    });
    return response.data;
  }

  streamChatMessage(
    message: string,
    sessionId: string,
    onToken: (token: string) => void,
    onSession: (session: any) => void,
    onDone: (full: string, formatted?: any) => void,
    onPaywall: () => void
  ): () => void {
    const abort = new AbortController();

    const run = async () => {
      try {
        const resp = await fetch(`${API_BASE_URL || ''}/api/v1/intel/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, session_id: sessionId, stream: true }),
          signal: abort.signal,
        });

        if (!resp.body) return;
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data: ')) continue;
            const data = trimmed.slice(6);
            if (data === '[DONE]') continue;
            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'token') onToken(parsed.content);
              else if (parsed.type === 'session') onSession(parsed.data);
              else if (parsed.type === 'paywall') onPaywall();
              else if (parsed.type === 'done') onDone(parsed.full_response, parsed.formatted);
            } catch {
              // ignore malformed
            }
          }
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          console.error('Stream error:', err);
        }
      }
    };

    run();
    return () => abort.abort();
  }

  async getChatSession(sessionId: string): Promise<{
    session: any;
    history: Array<{ role: string; content: string }>;
  }> {
    const response = await this.client.get(`/api/v1/intel/chat/session/${sessionId}`);
    return response.data;
  }

  // ═══════════ PROFILE ═══════════

  async getMyProfile(): Promise<any> {
    const response = await this.client.get('/api/v1/me');
    return response.data;
  }

  async updateMyProfile(updates: Record<string, any>): Promise<any> {
    const response = await this.client.put('/api/v1/me', updates);
    return response.data;
  }

  async getMyBadges(): Promise<any[]> {
    const response = await this.client.get('/api/v1/me/badges');
    return response.data;
  }

  async getMyScans(limit: number = 20, offset: number = 0): Promise<{ items: any[]; total: number; limit: number; offset: number }> {
    const response = await this.client.get('/api/v1/me/scans', { params: { limit, offset } });
    return response.data;
  }

  async uploadAvatar(file: File): Promise<{ avatar_url: string; success: boolean }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/api/v1/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getPublicProfile(username: string): Promise<any> {
    const response = await this.client.get(`/api/v1/profiles/${username}`);
    return response.data;
  }

  // ═══════════ GAMIFICATION ═══════════

  async getGamificationProfile(): Promise<any> {
    const response = await this.client.get('/api/v1/gamification/profile');
    return response.data;
  }

  async getLeaderboard(category: string = 'xp', limit: number = 50): Promise<any> {
    const response = await this.client.get(`/api/v1/gamification/leaderboard?category=${category}&limit=${limit}`);
    return response.data;
  }

  async recordActivity(activityType: string, metadata?: any): Promise<any> {
    const response = await this.client.post('/api/v1/gamification/event', {
      activity_type: activityType,
      metadata,
    });
    return response.data;
  }

  async getBadges(): Promise<any> {
    const response = await this.client.get('/api/v1/gamification/badges');
    return response.data;
  }

  // ═══════════ TRENCHES ═══════════

  async getTrenchesPosts(category?: string, limit: number = 50): Promise<any> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('limit', String(limit));
    const response = await this.client.get(`/api/v1/trenches/posts?${params}`);
    return response.data;
  }

  async createTrenchesPost(post: { title: string; content: string; category: string; tags?: string[] }): Promise<any> {
    const response = await this.client.post('/api/v1/trenches/posts', post);
    return response.data;
  }

  async createTrenchesComment(postId: string, content: string): Promise<any> {
    const response = await this.client.post(`/api/v1/trenches/posts/${postId}/comments`, { content });
    return response.data;
  }

  async upvoteTrenchesPost(postId: string): Promise<any> {
    const response = await this.client.post(`/api/v1/trenches/posts/${postId}/upvote`);
    return response.data;
  }

  // ═══════════ GMGN v2 ═══════════

  async getGMGNTrending(chain: string = 'sol'): Promise<any> {
    const response = await this.client.get(`/api/v1/gmgn-v2/trending?chain=${chain}`);
    return response.data;
  }

  async getGMGNSmartMoney(): Promise<any> {
    const response = await this.client.get('/api/v1/gmgn-v2/smart-money-dashboard');
    return response.data;
  }

  async getGMGNTokenSecurity(address: string, chain: string = 'sol'): Promise<any> {
    const response = await this.client.get(`/api/v1/gmgn-v2/token-security?address=${address}&chain=${chain}`);
    return response.data;
  }

  async getGMGNTopHolders(address: string, chain: string = 'sol'): Promise<any> {
    const response = await this.client.get(`/api/v1/gmgn-v2/top-holders?address=${address}&chain=${chain}`);
    return response.data;
  }

  async getGMGNWalletIntelligence(wallet: string, chain: string = 'sol'): Promise<any> {
    const response = await this.client.get(`/api/v1/gmgn-v2/wallet-intelligence?wallet=${wallet}&chain=${chain}`);
    return response.data;
  }

  // ═══════════ HELIUS ═══════════

  async getHeliusWhaleProfile(wallet: string): Promise<any> {
    const response = await this.client.get(`/api/v1/helius/whale-profile?wallet=${wallet}`);
    return response.data;
  }

  async getHeliusSniperDetect(address: string, chain: string = 'sol'): Promise<any> {
    const response = await this.client.get(`/api/v1/helius/sniper-detect?address=${address}&chain=${chain}`);
    return response.data;
  }

  async getHeliusSyndicateScan(address: string): Promise<any> {
    const response = await this.client.get(`/api/v1/helius/syndicate/scan?address=${address}`);
    return response.data;
  }

  async getHeliusWalletGraph(wallet: string): Promise<any> {
    const response = await this.client.get(`/api/v1/helius/syndicate/wallet-graph?wallet=${wallet}`);
    return response.data;
  }

  // ═══════════ CONTRACT ═══════════

  async auditContract(address: string, chain: string = 'ethereum', source?: string): Promise<any> {
    const response = await this.client.post('/api/v1/contract/audit', {
      contract_address: address,
      chain,
      source_code: source,
    });
    return response.data;
  }

  // ═══════════ INTELLIGENCE ═══════════

  async getCrossRefIntel(address: string): Promise<any> {
    const response = await this.client.get(`/api/v1/intelligence/crossref/${address}`);
    return response.data;
  }

  async getDegenIntel(address: string): Promise<any> {
    const response = await this.client.get(`/api/v1/intelligence/degen/${address}`);
    return response.data;
  }

  async getNarrativeIntel(address: string): Promise<any> {
    const response = await this.client.get(`/api/v1/intelligence/narrative/${address}`);
    return response.data;
  }

  async getTrendingIntel(): Promise<any> {
    const response = await this.client.get('/api/v1/intelligence/trending');
    return response.data;
  }

  // ═══════════ TOKEN SCANS ═══════════
  async fullCryptoScan(address: string, chain: string = 'solana'): Promise<any> {
    const response = await this.client.post('/api/v1/crypto/full-scan', { address, chain });
    return response.data;
  }
  async securityScan(address: string, chain: string = 'solana'): Promise<any> {
    const response = await this.client.get(`/api/v1/security/scan/${address}?chain=${chain}`);
    return response.data;
  }

  // ═══════════ PAYMENTS & SUBSCRIPTIONS ═══════════
  async getPaymentProducts(): Promise<any> {
    const response = await this.client.get('/api/v1/payments/products');
    return response.data;
  }
  async createPaymentCharge(productId: string, metadata: Record<string, any> = {}): Promise<any> {
    const response = await this.client.post('/api/v1/payments/charge', {
      product_id: productId, metadata,
    });
    return response.data;
  }
  async getPaymentCharge(chargeId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/payments/charge/${chargeId}`);
    return response.data;
  }

  // ═══════════ NEWS ═══════════
  async getNews(limit: number = 50): Promise<any> {
    const response = await this.client.get(`/api/v1/news?limit=${limit}`);
    return response.data;
  }
  async getHeadlines(count: number = 5): Promise<any> {
    const response = await this.client.get(`/api/v1/news/headlines?count=${count}`);
    return response.data;
  }



  // ═══════════ BACKEND CONTROL (ADMIN) — EXPANDED ═══════════
  async getSystemStats(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/system', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getLogs(adminKey: string, lines: number = 100, level?: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/logs', {
      headers: { 'X-Admin-Key': adminKey },
      params: { lines, level },
    });
    return response.data;
  }

  async getDatabaseTables(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/database/tables', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async runDatabaseQuery(adminKey: string, sql: string, limit: number = 100): Promise<any> {
    const response = await this.client.post('/api/v1/admin/database/query', {
      sql, limit,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getServices(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/services', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async serviceAction(adminKey: string, serviceId: string, action: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/services/${serviceId}/action`, {
      action,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getBots(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/bots', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async updateBot(adminKey: string, botId: string, updates: Record<string, any>): Promise<any> {
    const response = await this.client.put(`/api/v1/admin/bots/${botId}`, updates, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getAlertsHistory(adminKey: string, limit: number = 50): Promise<any> {
    const response = await this.client.get('/api/v1/admin/alerts', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit },
    });
    return response.data;
  }

  async sendTestAlert(adminKey: string, message: string, channel: string = '@rmi_backend', severity: string = 'info'): Promise<any> {
    const response = await this.client.post('/api/v1/admin/alerts/test', {
      message, channel, severity,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // Content Management
  async getAdminContentPosts(adminKey: string, limit: number = 50, status?: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/content/posts', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit, status },
    });
    return response.data;
  }

  async moderateContent(adminKey: string, postId: string, action: string, reason?: string): Promise<any> {
    const response = await this.client.post('/api/v1/admin/content/moderate', {
      post_id: postId, action, reason,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // Trenches Management
  async getAdminTrenchesPosts(adminKey: string, limit: number = 50): Promise<any> {
    const response = await this.client.get('/api/v1/admin/trenches/posts', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit },
    });
    return response.data;
  }

  async trenchesAction(adminKey: string, postId: string, action: string, reason?: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/trenches/posts/${postId}/action`, {
      action, reason,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // User Management
  async getAdminUsers(adminKey: string, limit: number = 50, offset: number = 0, role?: string, tier?: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/users', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit, offset, role, tier },
    });
    return response.data;
  }

  async userAction(adminKey: string, userId: string, action: string, value?: string, reason?: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/users/${userId}/action`, {
      action, value, reason,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // N8N Workflows
  async getN8nWorkflows(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/n8n/workflows', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async n8nWorkflowAction(adminKey: string, workflowId: string, action: string): Promise<any> {
    const response = await this.client.post(`/api/v1/admin/n8n/workflows/${workflowId}/action`, {
      action,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  // Infrastructure
  async getInfrastructure(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/admin/infrastructure', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }
  // ═══════════ MIRROR.XYZ ═══════════
  async publishToMirror(title: string, body: string, tags?: string[]): Promise<any> {
    const response = await this.client.post('/api/v1/newsletter/mirror/publish', {
      title, body, tags,
    });
    return response.data;
  }

  // ═══════════ DARKROOM CONTROL CENTER ═══════════
  async getMarketBriefing(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/market/briefing', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getMarketTrending(adminKey: string, limit: number = 20): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/market/trending', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit },
    });
    return response.data;
  }

  async getContentDrafts(adminKey: string, status?: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/content/drafts', {
      headers: { 'X-Admin-Key': adminKey },
      params: { status },
    });
    return response.data;
  }

  async createContentDraft(adminKey: string, draft: any): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/content/draft', draft, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async publishContent(adminKey: string, draftId: string): Promise<any> {
    const response = await this.client.post(`/api/v1/darkroom/content/publish?draft_id=${draftId}`, {}, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getContentStats(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/content/stats', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async postTelegram(adminKey: string, message: string, channel: string = '@rmi_alpha_alerts', pin: boolean = false): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/social/telegram/post', {
      message, channel, pin,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getTelegramStats(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/social/telegram/stats', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getGhostStats(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/social/ghost/stats', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getProjectStatus(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/project/status', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getAgentMesh(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/agents/mesh', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getActiveTasks(adminKey: string, limit: number = 50): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/tasks/active', {
      headers: { 'X-Admin-Key': adminKey },
      params: { limit },
    });
    return response.data;
  }

  // Advisor Agent

  // Auto-Content Pipeline
  async autoGenerateContent(adminKey: string, source: string = 'market_intel', count: number = 3, tone: string = 'analytical'): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/content/auto-generate', {
      source, count, tone,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async getPreparedContent(adminKey: string): Promise<any> {
    const response = await this.client.get('/api/v1/darkroom/content/prepared', {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async approveContent(adminKey: string, draftId: string, decision: string, scheduledFor?: string): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/content/approve', {
      draft_id: draftId, decision, scheduled_for: scheduledFor,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async advisorChat(adminKey: string, message: string, sessionId?: string, context?: any): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/advisor/chat', {
      message, session_id: sessionId, context,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async advisorSuggest(adminKey: string): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/advisor/suggest', {}, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }

  async advisorAct(adminKey: string, action: string, params?: any, confirm?: boolean): Promise<any> {
    const response = await this.client.post('/api/v1/darkroom/advisor/act', {
      action, params, confirm,
    }, {
      headers: { 'X-Admin-Key': adminKey },
    });
    return response.data;
  }
}

export const api = new ApiClient();
export default api;

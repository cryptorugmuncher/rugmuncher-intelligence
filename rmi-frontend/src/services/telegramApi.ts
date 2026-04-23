/**
 * Telegram Bot API Service
 * ==========================
 * Frontend client for backend Telegram endpoints.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TelegramUser {
  telegram_id: number;
  username?: string;
  first_name?: string;
  tier: string;
  scans_used: number;
  scans_limit: number;
  scans_remaining: number;
  xp: number;
  level: number;
  level_name: string;
  badges: string[];
  total_scans: number;
  wallet_address?: string;
}

interface ScanRecord {
  id: string;
  scan_type: string;
  token: string;
  chain: string;
  result: Record<string, any>;
  risk_score?: number;
  ai_consensus?: string;
  created_at: string;
}

interface LeaderboardEntry {
  telegram_id: number;
  username?: string;
  first_name?: string;
  total_scans: number;
  tier: string;
  xp: number;
  level: number;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(err || `HTTP ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export async function getTelegramUserStatus(telegramId: number): Promise<TelegramUser> {
  return fetchJson<TelegramUser>(`${API_BASE}/api/v1/telegram/user/${telegramId}`);
}

export async function getTelegramScanHistory(telegramId: number, limit = 50): Promise<ScanRecord[]> {
  const data = await fetchJson<{ scans: ScanRecord[] }>(
    `${API_BASE}/api/v1/telegram/scans/${telegramId}?limit=${limit}`
  );
  return data.scans;
}

export async function getTelegramLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
  const data = await fetchJson<{ leaderboard: LeaderboardEntry[] }>(
    `${API_BASE}/api/v1/telegram/leaderboard?limit=${limit}`
  );
  return data.leaderboard;
}

export async function createStarsInvoice(
  telegramId: number,
  title: string,
  description: string,
  payload: string,
  amount: number
): Promise<{ success: boolean; invoice_url?: string; error?: string }> {
  return fetchJson(`${API_BASE}/api/v1/telegram/stars-invoice`, {
    method: 'POST',
    body: JSON.stringify({
      telegram_id: telegramId,
      title,
      description,
      payload,
      amount,
    }),
  });
}

export async function registerTelegramUser(user: {
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
}): Promise<{ success: boolean; user: TelegramUser }> {
  return fetchJson(`${API_BASE}/api/v1/telegram/user/register`, {
    method: 'POST',
    body: JSON.stringify(user),
  });
}

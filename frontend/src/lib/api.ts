const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getToken(): string | null {
  return localStorage.getItem('access_token');
}

async function fetchJson(path: string, options: RequestInit = {}) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getProfile: () => fetchJson('/api/v1/user/profile'),
  updateProfile: (data: any) =>
    fetchJson('/api/v1/user/profile', { method: 'PUT', body: JSON.stringify(data) }),
  completeOnboarding: (data: any) =>
    fetchJson('/api/v1/user/onboarding', { method: 'POST', body: JSON.stringify(data) }),
  getScans: (page = 1, pageSize = 20) =>
    fetchJson(`/api/v1/user/scans?page=${page}&page_size=${pageSize}`),
  getBadges: () => fetchJson('/api/v1/user/badges'),
  linkTelegram: (telegram_username: string) =>
    fetchJson('/api/v1/user/telegram-link', {
      method: 'POST',
      body: JSON.stringify({ telegram_username }),
    }),
};

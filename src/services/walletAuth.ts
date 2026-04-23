/**
 * Wallet Authentication Service
 * =============================
 * Handles SIWE-style sign-in with Ethereum wallets.
 */
import { signMessage } from '@wagmi/core';
import { config } from './wagmi';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface WalletAuthResult {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    wallet_address: string;
    role: string;
    tier: string;
    created_at: string;
  };
}

export async function getAuthNonce(): Promise<{ nonce: string; timestamp: string }> {
  const resp = await fetch(`${API_BASE_URL}/auth/nonce`);
  if (!resp.ok) throw new Error('Failed to get nonce');
  return resp.json();
}

export async function signInWithWallet(walletAddress: string): Promise<WalletAuthResult> {
  // 1. Get nonce from backend
  const { nonce, timestamp } = await getAuthNonce();

  // 2. Build sign message
  const message = [
    'RugMunch Intelligence wants you to sign in with your Ethereum account.',
    walletAddress,
    '',
    'Sign in to RugMunch Intelligence.',
    '',
    `Wallet: ${walletAddress}`,
    `Nonce: ${nonce}`,
    `Timestamp: ${timestamp}`,
  ].join('\n');

  // 3. Sign message
  const signature = await signMessage(config, { message });

  // 4. Send to backend
  const resp = await fetch(`${API_BASE_URL}/auth/wallet`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, signature, wallet_address: walletAddress }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || 'Wallet authentication failed');
  }

  return resp.json();
}

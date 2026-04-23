/**
 * Login Component
 * ===============
 * Dual auth: Web3 wallet (primary) + Email/Password (fallback)
 */
import { useState, useEffect } from 'react';
import { useAccount, useDisconnect } from 'wagmi';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAppStore } from '../store/appStore';
import { auth } from '../services/supabase';
import { signInWithWallet } from '../services/walletAuth';
import {
  Shield,
  Loader2,
  Eye,
  EyeOff,
  Wallet,
  Mail,
  ArrowRight,
} from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isWalletLoading, setIsWalletLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'wallet' | 'email'>('wallet');

  const setUser = useAppStore((state) => state.setUser);
  const setAuthenticated = useAppStore((state) => state.setAuthenticated);
  const setAuthToken = useAppStore((state) => state.setAuthToken);

  const { address, isConnected } = useAccount();
  const { disconnect } = useDisconnect();

  // Auto-authenticate when wallet connects
  useEffect(() => {
    if (isConnected && address && !isWalletLoading) {
      handleWalletAuth(address);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isConnected, address]);

  const handleWalletAuth = async (walletAddress: string) => {
    setIsWalletLoading(true);
    setError(null);

    try {
      const result = await signInWithWallet(walletAddress);

      // Store tokens
      setAuthToken(result.access_token);
      localStorage.setItem('access_token', result.access_token);

      // Update store
      setUser({
        id: result.user.id,
        email: result.user.email,
        wallet_address: result.user.wallet_address,
        role: result.user.role as any,
        tier: result.user.tier as any,
        created_at: result.user.created_at,
      });
      setAuthenticated(true);
    } catch (err: any) {
      setError(err.message || 'Wallet authentication failed');
      disconnect();
    } finally {
      setIsWalletLoading(false);
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      let result;
      result = await auth.signIn(email, password);

      if (result.error) {
        setError(result.error.message);
      } else if (result.data?.user) {
        const token = result.data.session?.access_token || '';
        setAuthToken(token);
        localStorage.setItem('access_token', token);
        setUser({
          id: result.data.user.id,
          email: result.data.user.email || '',
          role: 'USER',
          tier: 'FREE',
          created_at: result.data.user.created_at,
        });
        setAuthenticated(true);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="crypto-card w-full max-w-md">
        <div className="text-center mb-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center">
            <Shield className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">
            {mode === 'wallet' ? 'Connect Wallet' : 'Welcome Back'}
          </h1>
          <p className="text-gray-400">
            {mode === 'wallet'
              ? 'Sign in with your Web3 wallet for instant access'
              : 'Sign in with email to access your investigations'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded bg-red-500/10 border border-red-500/50 text-red-400 text-sm">
            {error}
          </div>
        )}

        {mode === 'wallet' ? (
          <div className="space-y-4">
            {/* Wallet Connect Button */}
            <div className="flex justify-center">
              <ConnectButton
                showBalance={false}
                chainStatus="icon"
                accountStatus="address"
              />
            </div>

            {isWalletLoading && (
              <div className="flex items-center justify-center gap-2 text-purple-400 text-sm">
                <Loader2 className="w-4 h-4 animate-spin" />
                Verifying wallet signature...
              </div>
            )}

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[#12121a] px-2 text-gray-500">or</span>
              </div>
            </div>

            <button
              onClick={() => setMode('email')}
              className="w-full py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg flex items-center justify-center gap-2 transition-colors"
            >
              <Mail className="w-4 h-4" />
              Sign in with Email
            </button>
          </div>
        ) : (
          <form onSubmit={handleEmailSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white
                           focus:border-purple-500 focus:outline-none transition-colors"
                placeholder="agent@rmi.intel"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 pr-10 text-white
                             focus:border-purple-500 focus:outline-none transition-colors"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[#12121a] px-2 text-gray-500">or</span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setMode('wallet')}
              className="w-full py-3 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-400 rounded-lg flex items-center justify-center gap-2 transition-colors"
            >
              <Wallet className="w-4 h-4" />
              Connect Wallet
            </button>
          </form>
        )}

        <div className="mt-6 pt-4 border-t border-crypto-border text-center">
          <p className="text-xs text-gray-500">
            {mode === 'wallet'
              ? 'Web3-first authentication powered by Ethereum signatures'
              : 'Secured by Supabase Auth with Row Level Security'}
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Auth Page — Unified Login / Register / OAuth
 * Supports: Wallet, Email, Google, GitHub, X/Twitter
 */
import { useState, useEffect } from 'react';
import { useAccount, useDisconnect } from 'wagmi';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAppStore } from '../store/appStore';
import { auth, supabase } from '../services/supabase';
import { signInWithWallet } from '../services/walletAuth';
import {
  Shield, Loader2, Eye, EyeOff, Wallet, Mail, ArrowRight,
  Globe, Code, AtSign, UserPlus, LogIn, ChevronLeft,
} from 'lucide-react';

type AuthMode = 'login' | 'register' | 'forgot';

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isWalletLoading, setIsWalletLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
      setAuthToken(result.access_token);
      localStorage.setItem('access_token', result.access_token);
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
    setSuccess(null);

    try {
      if (mode === 'login') {
        const result = await auth.signIn(email, password);
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
      } else if (mode === 'register') {
        const result = await auth.signUp(email, password);
        if (result.error) {
          setError(result.error.message);
        } else if (result.data?.user) {
          // Update profile with display name
          if (displayName) {
            await supabase.from('profiles').update({ display_name: displayName }).eq('id', result.data.user.id);
          }
          setSuccess('Account created! Check your email to confirm, then sign in.');
          setMode('login');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github' | 'twitter') => {
    setIsLoading(true);
    setError(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: window.location.origin + '/auth/callback',
        },
      });
      if (error) setError(error.message);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const isLogin = mode === 'login';
  const isRegister = mode === 'register';

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#12121a] border border-gray-800 rounded-2xl p-8 shadow-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center">
            <Shield className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">
            {isLogin ? 'Welcome Back' : isRegister ? 'Create Account' : 'Reset Password'}
          </h1>
          <p className="text-gray-400 text-sm">
            {isLogin
              ? 'Sign in to access your investigations and profile'
              : isRegister
              ? 'Join the RugMunch Intelligence community'
              : 'Enter your email to reset your password'}
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm">
            {success}
          </div>
        )}

        {/* Wallet Auth — always visible */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-center">
            <ConnectButton showBalance={false} chainStatus="icon" accountStatus="address" />
          </div>
          {isWalletLoading && (
            <div className="flex items-center justify-center gap-2 text-purple-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Verifying wallet signature...
            </div>
          )}
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-700" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-[#12121a] px-3 text-gray-500 uppercase tracking-wider">or continue with</span>
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <button
            onClick={() => handleOAuth('google')}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            <Globe className="w-5 h-5 text-red-400" />
            <span className="text-sm">Google</span>
          </button>
          <button
            onClick={() => handleOAuth('github')}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            <Code className="w-5 h-5" />
            <span className="text-sm">GitHub</span>
          </button>
          <button
            onClick={() => handleOAuth('twitter')}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            <AtSign className="w-5 h-5 text-blue-400" />
            <span className="text-sm">X</span>
          </button>
        </div>

        {/* Email Form */}
        <form onSubmit={handleEmailSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Display Name</label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="Crypto Detective"
              />
            </div>
          )}

          <div>
            <label className="block text-sm text-gray-400 mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="you@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 pr-10 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="••••••••"
                required
                minLength={6}
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
            className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isLogin ? (
              <LogIn className="w-4 h-4" />
            ) : (
              <UserPlus className="w-4 h-4" />
            )}
            {isLoading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center text-sm text-gray-400">
          {isLogin ? (
            <>
              Don&apos;t have an account?{' '}
              <button onClick={() => { setMode('register'); setError(null); setSuccess(null); }} className="text-purple-400 hover:text-purple-300 font-medium">
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button onClick={() => { setMode('login'); setError(null); setSuccess(null); }} className="text-purple-400 hover:text-purple-300 font-medium">
                Sign in
              </button>
            </>
          )}
        </div>

        <div className="mt-4 text-center text-xs text-gray-500">
          By signing up, you agree to receive notifications and updates. You can unsubscribe anytime.
        </div>
      </div>
    </div>
  );
}

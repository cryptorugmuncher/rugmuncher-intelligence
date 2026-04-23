/**
 * Top Header Component
 */
import { useAppStore } from '../store/appStore';
import { Bell, User, LogOut, Search, Wallet } from 'lucide-react';
import { auth } from '../services/supabase';

export default function Header() {
  const { user, isAuthenticated, logout } = useAppStore();

  const handleLogout = async () => {
    try {
      await auth.signOut();
    } catch {
      // Wallet users don't have Supabase sessions
    }
    logout();
  };

  return (
    <header className="h-16 bg-[#12121a]/80 backdrop-blur border-b border-purple-500/20 flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            type="text"
            placeholder="Search wallets, investigations, or transactions..."
            className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="relative p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User Menu */}
        {isAuthenticated && user ? (
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-white">
                {user.wallet_address
                  ? `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}`
                  : user.email}
              </p>
              <p className="text-xs text-gray-500 flex items-center justify-end gap-1">
                {user.wallet_address ? (
                  <>
                    <Wallet size={10} className="text-purple-400" />
                    <span className="text-purple-400">Wallet</span>
                  </>
                ) : (
                  user.role || 'USER'
                )}
              </p>
            </div>
            <button
              onClick={() => useAppStore.getState().setCurrentPage('profile')}
              className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center hover:ring-2 hover:ring-purple-400 transition-all"
              title="Profile"
            >
              <User size={18} className="text-white" />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <button
            onClick={() => useAppStore.getState().setCurrentPage('login')}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}

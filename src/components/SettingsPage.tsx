/**
 * User Profile & Settings Page
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  User, 
  Key,
  Bell,
  Shield,
  CreditCard,
  Check,
  Copy,
  ExternalLink,
  Star,
  AlertTriangle,
  Save,
  Eye,
  EyeOff
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

const SETTINGS_TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'subscription', label: 'Subscription', icon: CreditCard },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'api', label: 'API Keys', icon: Key },
];

const MOCK_ACTIVITY = [
  { action: 'Logged in', time: '2 hours ago', ip: '192.168.1.1' },
  { action: 'Updated password', time: '2 days ago', ip: '192.168.1.1' },
  { action: 'Changed notification settings', time: '1 week ago', ip: '192.168.1.1' },
  { action: 'Generated API key', time: '2 weeks ago', ip: '192.168.1.1' },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [showApiKey, setShowApiKey] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';

  const { data: gamification } = useQuery({
    queryKey: ['gamification', user?.id],
    queryFn: () => api.getGamificationProfile(),
    enabled: !!user,
  });

  const handleCopyKey = () => {
    navigator.clipboard.writeText('rm_live_xxxxxxxxxxxxxxxx');
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400">Manage your account, subscription, and preferences</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-[#12121a] border border-gray-800 rounded-xl overflow-hidden">
            {SETTINGS_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-green-500/10 border-l-2 border-green-500 text-green-400'
                    : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* User Summary Card */}
          <div className="mt-4 bg-[#12121a] border border-gray-800 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center text-lg font-bold">
                {user?.email?.[0].toUpperCase() || 'U'}
              </div>
              <div>
                <div className="font-semibold text-white">{user?.email?.split('@')[0] || 'User'}</div>
                <div className="text-sm text-gray-400">{user?.email}</div>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Tier</span>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full font-medium">
                {tier}
              </span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Profile Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Email Address</label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      readOnly
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Display Name</label>
                    <input
                      type="text"
                      placeholder="How you appear to others"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Bio</label>
                    <textarea
                      rows={3}
                      placeholder="Tell us about yourself..."
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500 resize-none"
                    />
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-gray-800 flex justify-end">
                  <button className="px-6 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg flex items-center gap-2">
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                </div>
              </div>

              {/* Reputation */}
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Reputation</h2>
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-full flex items-center justify-center">
                    <span className="text-2xl font-bold text-purple-400">
                      {gamification?.level?.xp || 0}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-white">
                      {gamification?.level?.title || 'Rookie'}
                    </div>
                    <p className="text-sm text-gray-400">
                      Level {gamification?.level?.level || 1} • {gamification?.stats?.scan_count || 0} scans • {gamification?.stats?.post_count || 0} posts
                    </p>
                    <div className="mt-2 h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                        style={{ width: `${gamification?.level?.progress_percent || 0}%` }}
                      />
                    </div>
                    <div className="flex gap-2 mt-2">
                      {gamification?.badges?.slice(0, 4).map((badge: any) => (
                        <span
                          key={badge.badge_id}
                          className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full"
                          title={badge.description}
                        >
                          {badge.emoji} {badge.name}
                        </span>
                      ))}
                      {(gamification?.badges?.length || 0) > 4 && (
                        <span className="px-2 py-1 bg-gray-700 text-gray-400 text-xs rounded-full">
                          +{gamification.badges.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
                <div className="space-y-3">
                  {MOCK_ACTIVITY.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                      <div>
                        <div className="text-white">{item.action}</div>
                        <div className="text-xs text-gray-500">{item.time} • IP: {item.ip}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'subscription' && (
            <div className="space-y-6">
              {/* Current Plan */}
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Current Plan</h2>
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                      <Star className="w-6 h-6 text-green-400" />
                    </div>
                    <div>
                      <div className="text-xl font-bold text-white">{tier}</div>
                      <div className="text-sm text-gray-400">Renews on Feb 15, 2024</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">
                      {tier === 'FREE' ? '$0' : tier === 'BASIC' ? '$29' : tier === 'PRO' ? '$99' : '$299'}
                    </div>
                    <div className="text-sm text-gray-400">/month</div>
                  </div>
                </div>
                <div className="mt-6 flex gap-3">
                  <a href="/pricing" className="px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                    Upgrade Plan
                  </a>
                  <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg">
                    Cancel Subscription
                  </button>
                </div>
              </div>

              {/* Usage Stats */}
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Usage This Month</h2>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Wallet Scans</span>
                      <span className="text-white">45 / {tier === 'FREE' ? '5' : tier === 'BASIC' ? '25' : 'Unlimited'}</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 rounded-full" style={{ width: '75%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">API Calls</span>
                      <span className="text-white">1,245 / {tier === 'FREE' ? '0' : tier === 'BASIC' ? '1,000' : tier === 'PRO' ? '10,000' : '50,000'}</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: '12%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Investigations</span>
                      <span className="text-white">3 / {tier === 'FREE' ? '1' : tier === 'BASIC' ? '5' : tier === 'PRO' ? '20' : 'Unlimited'}</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500 rounded-full" style={{ width: '15%' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Payment History */}
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Payment History</h2>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <div>
                      <div className="text-white">Pro Plan - Monthly</div>
                      <div className="text-xs text-gray-500">Jan 15, 2024</div>
                    </div>
                    <div className="text-right">
                      <div className="text-white">$99.00</div>
                      <div className="text-xs text-green-400">Paid</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <div>
                      <div className="text-white">Pro Plan - Monthly</div>
                      <div className="text-xs text-gray-500">Dec 15, 2023</div>
                    </div>
                    <div className="text-right">
                      <div className="text-white">$99.00</div>
                      <div className="text-xs text-green-400">Paid</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Notification Preferences</h2>
              <div className="space-y-4">
                {[
                  { id: 'email_alerts', label: 'Email Alerts', desc: 'Scam detection alerts via email', checked: true },
                  { id: 'telegram_alerts', label: 'Telegram Alerts', desc: 'Real-time alerts via @rugmunchbot', checked: true },
                  { id: 'weekly_digest', label: 'Weekly Digest', desc: 'Summary of your portfolio activity', checked: false },
                  { id: 'investigation_updates', label: 'Investigation Updates', desc: 'Updates on cases you\'re following', checked: true },
                  { id: 'price_alerts', label: 'Price Alerts', desc: 'Token price movement notifications', checked: false },
                  { id: 'marketing', label: 'Product Updates', desc: 'New features and announcements', checked: false },
                ].map((item) => (
                  <div key={item.id} className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id={item.id}
                      defaultChecked={item.checked}
                      className="w-5 h-5 rounded border-gray-700 bg-gray-800 text-green-500 focus:ring-green-500 mt-0.5"
                    />
                    <div>
                      <label htmlFor={item.id} className="font-medium text-white cursor-pointer">
                        {item.label}
                      </label>
                      <p className="text-sm text-gray-400">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-gray-800 flex justify-end">
                <button className="px-6 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                  Save Preferences
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Password</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Current Password</label>
                    <input
                      type="password"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">New Password</label>
                    <input
                      type="password"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Confirm New Password</label>
                    <input
                      type="password"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button className="px-6 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                    Update Password
                  </button>
                </div>
              </div>

              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Two-Factor Authentication</h2>
                <div className="flex items-center justify-between p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-yellow-400" />
                    <div>
                      <div className="font-medium text-white">2FA Not Enabled</div>
                      <p className="text-sm text-gray-400">Enable 2FA for additional security</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg transition-colors">
                    Enable 2FA
                  </button>
                </div>
              </div>

              <div className="bg-[#12121a] border border-red-500/30 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-red-400 mb-4">Danger Zone</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-white">Delete Account</div>
                      <p className="text-sm text-gray-400">Permanently delete your account and all data</p>
                    </div>
                    <button 
                      onClick={() => setShowDeleteConfirm(true)}
                      className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">API Keys</h2>
                {tier === 'FREE' ? (
                  <div className="text-center py-8">
                    <Key className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">API access requires PRO tier or higher</p>
                    <a href="/pricing" className="mt-4 inline-block px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                      Upgrade to PRO
                    </a>
                  </div>
                ) : (
                  <>
                    <div className="p-4 bg-gray-800/50 rounded-lg mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-400">Production Key</span>
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Active</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type={showApiKey ? 'text' : 'password'}
                          value="rm_live_xxxxxxxxxxxxxxxx"
                          readOnly
                          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white font-mono text-sm"
                        />
                        <button
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400"
                        >
                          {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={handleCopyKey}
                          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400"
                        >
                          {copiedKey ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                        </button>
                      </div>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                        <span>Rate Limit: {tier === 'PRO' ? '1,000' : tier === 'ELITE' ? '50,000' : 'Unlimited'}/min</span>
                        <span>•</span>
                        <span>Last used: 2 hours ago</span>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button className="px-4 py-2 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg">
                        Generate New Key
                      </button>
                      <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg">
                        Revoke All Keys
                      </button>
                    </div>
                  </>
                )}
              </div>

              <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">API Documentation</h2>
                <p className="text-gray-400 mb-4">
                  Use our REST API to integrate RMI intelligence into your own applications.
                </p>
                <a 
                  href="https://docs.rmi.io/api"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  View Documentation
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirm Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-[#12121a] border border-red-500/30 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-red-400 mb-4">Delete Account?</h3>
            <p className="text-gray-400 mb-6">
              This will permanently delete your account, all investigations, and settings. 
              This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg"
              >
                Cancel
              </button>
              <button 
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-2 bg-red-500 hover:bg-red-600 text-white font-bold rounded-lg"
              >
                Delete Forever
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * User Management Panel
 * Complete user administration with roles, tiers, bans
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { db, supabase } from '../../services/supabase';
import {
  Users,
  Search,
  Shield,
  Crown,
  User,
  Ban,
  CheckCircle,
  AlertTriangle,
  Lock,
  Unlock,
  Edit3,
  Download,
  RefreshCw,
  Star,
} from 'lucide-react';

const TIERS = ['FREE', 'BASIC', 'PRO', 'ELITE', 'ENTERPRISE'];
const ROLES = ['USER', 'ANALYST', 'MODERATOR', 'ADMIN'];

export default function UserManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [tierFilter, setTierFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showBanModal, setShowBanModal] = useState(false);
  const [banReason, setBanReason] = useState('');

  // Fetch users
  const { data: users, isLoading, refetch } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const { data, error } = await db.users.getAll();
      if (error) throw error;
      return data || [];
    },
  });

  // Update user mutation
  const updateUser = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      const { data, error } = await db.users.update(id, updates);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      refetch();
      setShowEditModal(false);
    },
  });

  // Ban user mutation
  const banUser = useMutation({
    mutationFn: async ({ id, reason, duration }: { id: string; reason: string; duration?: number }) => {
      const { data, error } = await db.users.ban(id, reason, duration);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      refetch();
      setShowBanModal(false);
      setBanReason('');
    },
  });

  // Unban user helper
  const unbanUser = useMutation({
    mutationFn: async (id: string) => {
      const { data, error } = await db.users.unban(id);
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      refetch();
      setShowBanModal(false);
    },
  });

  // Reset password mutation - triggers email via Supabase Auth
  const resetPassword = useMutation({
    mutationFn: async (userId: string) => {
      // Get user email first
      const { data: user, error: userError } = await db.users.getById(userId);
      if (userError || !user?.email) throw new Error('User not found');

      // Trigger password reset email via Supabase Auth
      const { error } = await supabase.auth.resetPasswordForEmail(user.email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      if (error) throw error;
      return { success: true };
    },
  });

  const filteredUsers = users?.filter((u: any) => {
    const matchesSearch =
      u.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'all' || u.role === roleFilter;
    const matchesTier = tierFilter === 'all' || u.tier === tierFilter;
    return matchesSearch && matchesRole && matchesTier;
  });

  const stats = {
    total: users?.length || 0,
    admins: users?.filter((u: any) => u.role === 'ADMIN').length || 0,
    analysts: users?.filter((u: any) => u.role === 'ANALYST').length || 0,
    proUsers: users?.filter((u: any) => ['PRO', 'ELITE', 'ENTERPRISE'].includes(u.tier)).length || 0,
    banned: users?.filter((u: any) => u.banned).length || 0,
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return <Shield className="w-4 h-4 text-red-400" />;
      case 'MODERATOR':
        return <Shield className="w-4 h-4 text-orange-400" />;
      case 'ANALYST':
        return <User className="w-4 h-4 text-blue-400" />;
      default:
        return <User className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'ENTERPRISE':
        return 'text-purple-400 bg-purple-500/20';
      case 'ELITE':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'PRO':
        return 'text-blue-400 bg-blue-500/20';
      case 'BASIC':
        return 'text-green-400 bg-green-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard title="Total Users" value={stats.total} icon={Users} color="blue" />
        <StatCard title="Admins" value={stats.admins} icon={Shield} color="red" />
        <StatCard title="Analysts" value={stats.analysts} icon={User} color="cyan" />
        <StatCard title="Pro+ Users" value={stats.proUsers} icon={Crown} color="purple" />
        <StatCard title="Banned" value={stats.banned} icon={Ban} color="orange" />
      </div>

      {/* Filters */}
      <div className="crypto-card">
        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by email or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-crypto-dark border border-crypto-border rounded-lg pl-10 pr-4 py-2 text-white"
            />
          </div>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Roles</option>
            {ROLES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
          >
            <option value="all">All Tiers</option>
            {TIERS.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="crypto-card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading users...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-crypto-border text-gray-400">
                  <th className="text-left p-3">User</th>
                  <th className="text-left p-3">Role</th>
                  <th className="text-left p-3">Tier</th>
                  <th className="text-left p-3">Reputation</th>
                  <th className="text-left p-3">Joined</th>
                  <th className="text-left p-3">Last Active</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers?.map((user: any) => (
                  <tr key={user.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                    <td className="p-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                          <span className="text-white text-xs font-bold">
                            {user.email?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-white font-medium">{user.email}</p>
                          <p className="text-xs text-gray-500 font-mono">{user.id?.slice(0, 8)}...</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        {getRoleIcon(user.role)}
                        <span className="text-gray-300">{user.role}</span>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs ${getTierColor(user.tier)}`}>
                        {user.tier}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400" />
                        <span className="text-white">{user.reputation_score || 0}</span>
                      </div>
                    </td>
                    <td className="p-3 text-gray-400">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-gray-400">
                      {user.last_active ? new Date(user.last_active).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="p-3">
                      {user.banned ? (
                        <span className="flex items-center gap-1 text-red-400">
                          <Ban className="w-4 h-4" />
                          Banned
                        </span>
                      ) : user.email_confirmed ? (
                        <span className="flex items-center gap-1 text-green-400">
                          <CheckCircle className="w-4 h-4" />
                          Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-yellow-400">
                          <AlertTriangle className="w-4 h-4" />
                          Unconfirmed
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => {
                            setSelectedUser(user);
                            setShowEditModal(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-blue-400"
                          title="Edit"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => resetPassword.mutate(user.id)}
                          className="p-2 hover:bg-crypto-card rounded text-yellow-400"
                          title="Reset Password"
                        >
                          <Lock className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedUser(user);
                            setShowBanModal(true);
                          }}
                          className="p-2 hover:bg-crypto-card rounded text-red-400"
                          title={user.banned ? 'Unban' : 'Ban'}
                        >
                          {user.banned ? <Unlock className="w-4 h-4" /> : <Ban className="w-4 h-4" />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">Edit User</h3>
            <div className="mb-4 p-3 bg-crypto-dark rounded">
              <p className="text-sm text-gray-400">{selectedUser.email}</p>
              <p className="text-xs text-gray-500 font-mono">{selectedUser.id}</p>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                updateUser.mutate({
                  id: selectedUser.id,
                  updates: {
                    role: formData.get('role'),
                    tier: formData.get('tier'),
                    reputation_score: parseInt(formData.get('reputation') as string),
                  },
                });
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm text-gray-400 mb-1">Role</label>
                <select
                  name="role"
                  defaultValue={selectedUser.role}
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tier</label>
                <select
                  name="tier"
                  defaultValue={selectedUser.tier}
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                >
                  {TIERS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Reputation Score</label>
                <input
                  type="number"
                  name="reputation"
                  defaultValue={selectedUser.reputation_score || 0}
                  min="0"
                  max="1000"
                  className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Ban User Modal */}
      {showBanModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">
              {selectedUser.banned ? 'Unban User' : 'Ban User'}
            </h3>
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded">
              <p className="text-sm text-red-400">{selectedUser.email}</p>
              <p className="text-xs text-gray-500">ID: {selectedUser.id}</p>
            </div>
            {!selectedUser.banned && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Reason for Ban</label>
                  <textarea
                    value={banReason}
                    onChange={(e) => setBanReason(e.target.value)}
                    className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white"
                    rows={3}
                    placeholder="Enter reason..."
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Duration (optional)</label>
                  <select className="w-full bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-white">
                    <option>Permanent</option>
                    <option>24 hours</option>
                    <option>7 days</option>
                    <option>30 days</option>
                  </select>
                </div>
              </div>
            )}
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => setShowBanModal(false)}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (selectedUser.banned) {
                    unbanUser.mutate(selectedUser.id);
                  } else {
                    banUser.mutate({ id: selectedUser.id, reason: banReason });
                  }
                  setShowBanModal(false);
                }}
                className={`flex-1 ${selectedUser.banned ? 'btn-primary' : 'bg-red-500/20 text-red-400 border border-red-500/50 rounded px-4 py-2 hover:bg-red-500/30'}`}
              >
                {selectedUser.banned ? 'Unban User' : 'Ban User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-500/20',
    red: 'text-red-400 bg-red-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    orange: 'text-orange-400 bg-orange-500/20',
  };

  return (
    <div className="crypto-card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded ${colors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

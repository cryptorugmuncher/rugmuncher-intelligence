/**
 * Content Management Panel
 * Manage posts, articles, newsletters, and Mirror.xyz publishing
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import {
  FileText,
  Eye,
  CheckCircle,
  XCircle,
  Star,
  Trash2,
  RefreshCw,
  Filter,
  Globe,
  Newspaper,
  Megaphone,
  PenTool,
  AlertTriangle,
  Search,
} from 'lucide-react';

const STATUS_COLORS: Record<string, string> = {
  published: 'bg-green-500/20 text-green-400',
  pending: 'bg-yellow-500/20 text-yellow-400',
  rejected: 'bg-red-500/20 text-red-400',
  featured: 'bg-purple-500/20 text-purple-400',
  draft: 'bg-gray-500/20 text-gray-400',
};

export default function ContentManagement({ adminKey }: { adminKey: string }) {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-content-posts', adminKey, statusFilter],
    queryFn: () => api.getAdminContentPosts(adminKey, 50, statusFilter === 'all' ? undefined : statusFilter),
    enabled: !!adminKey,
  });

  const moderateMutation = useMutation({
    mutationFn: ({ postId, action, reason }: { postId: string; action: string; reason?: string }) =>
      api.moderateContent(adminKey, postId, action, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-content-posts'] }),
  });

  const posts = (data?.posts || []).filter((p: any) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (p.title || '').toLowerCase().includes(q) ||
      (p.content || '').toLowerCase().includes(q) ||
      (p.author || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <PenTool className="w-6 h-6 text-neon-purple" />
          Content Management
        </h2>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-2 bg-crypto-dark border border-crypto-border rounded text-sm text-white w-48"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-crypto-dark border border-crypto-border rounded px-3 py-2 text-sm text-white"
          >
            <option value="all">All Status</option>
            <option value="published">Published</option>
            <option value="pending">Pending</option>
            <option value="featured">Featured</option>
            <option value="draft">Draft</option>
            <option value="rejected">Rejected</option>
          </select>
          <button onClick={() => refetch()} className="btn-secondary p-2">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard label="Total" value={data?.total || 0} icon={FileText} color="blue" />
        <StatCard label="Published" value={posts.filter((p: any) => p.status === 'published').length} icon={CheckCircle} color="green" />
        <StatCard label="Pending" value={posts.filter((p: any) => p.status === 'pending').length} icon={AlertTriangle} color="yellow" />
        <StatCard label="Featured" value={posts.filter((p: any) => p.status === 'featured').length} icon={Star} color="purple" />
        <StatCard label="Rejected" value={posts.filter((p: any) => p.status === 'rejected').length} icon={XCircle} color="red" />
      </div>

      {/* Posts Table */}
      <div className="crypto-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-crypto-border text-gray-400 text-left">
                <th className="p-3">Post</th>
                <th className="p-3">Author</th>
                <th className="p-3">Status</th>
                <th className="p-3">Date</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={5} className="p-8 text-center text-gray-500">Loading...</td></tr>
              ) : posts.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-gray-500">No posts found</td></tr>
              ) : (
                posts.map((post: any) => (
                  <tr key={post.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                    <td className="p-3">
                      <div className="max-w-xs">
                        <p className="text-white font-medium truncate">{post.title || 'Untitled'}</p>
                        <p className="text-gray-500 text-xs truncate">{post.content?.slice(0, 80)}...</p>
                        <div className="flex gap-1 mt-1">
                          {(post.tags || []).map((t: string) => (
                            <span key={t} className="text-[10px] px-1.5 py-0.5 bg-crypto-dark rounded text-gray-400">{t}</span>
                          ))}
                        </div>
                      </div>
                    </td>
                    <td className="p-3 text-gray-300">{post.author_id?.slice(0, 8) || 'unknown'}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-xs ${STATUS_COLORS[post.status] || STATUS_COLORS.draft}`}>
                        {post.status || 'draft'}
                      </span>
                    </td>
                    <td className="p-3 text-gray-400 text-xs">
                      {post.created_at ? new Date(post.created_at).toLocaleDateString() : '-'}
                    </td>
                    <td className="p-3">
                      <div className="flex gap-1">
                        <button
                          className="p-1.5 hover:bg-green-500/20 rounded text-green-400"
                          title="Approve"
                          onClick={() => moderateMutation.mutate({ postId: post.id, action: 'approve' })}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          className="p-1.5 hover:bg-purple-500/20 rounded text-purple-400"
                          title="Feature"
                          onClick={() => moderateMutation.mutate({ postId: post.id, action: 'feature' })}
                        >
                          <Star className="w-4 h-4" />
                        </button>
                        <button
                          className="p-1.5 hover:bg-red-500/20 rounded text-red-400"
                          title="Delete"
                          onClick={() => moderateMutation.mutate({ postId: post.id, action: 'delete' })}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color }: any) {
  const colors: any = {
    blue: 'text-blue-400 bg-blue-500/20',
    green: 'text-green-400 bg-green-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    red: 'text-red-400 bg-red-500/20',
  };
  return (
    <div className="crypto-card p-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-gray-400 text-xs">{label}</span>
        <div className={`p-1 rounded ${colors[color]}`}><Icon className="w-3 h-3" /></div>
      </div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}

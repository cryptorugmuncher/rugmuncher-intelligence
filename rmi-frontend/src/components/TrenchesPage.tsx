/**
 * The Trenches - Community Message Board
 * ======================================
 * Real-time community posts with gamification integration.
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MessageSquare, Shield, AlertTriangle, ThumbsUp, MessageCircle,
  Share2, Flag, Check, Clock, Users, TrendingUp, Plus, Search,
  Send, Star, Zap, Trophy, Loader2,
} from 'lucide-react';
import { useAppStore } from '../store/appStore';
import api from '../services/api';

const CATEGORIES = [
  { id: 'all', label: 'All Posts', icon: MessageSquare },
  { id: 'scam_report', label: 'Scam Reports', icon: AlertTriangle, color: 'red' },
  { id: 'intel', label: 'Intel', icon: Zap, color: 'blue' },
  { id: 'discussion', label: 'Discussion', icon: MessageCircle, color: 'gray' },
  { id: 'announcement', label: 'Official', icon: Star, color: 'yellow' },
];

interface Post {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  author_id: string;
  author_email: string;
  author_wallet: string;
  upvotes: number;
  comments: number;
  created_at: string;
}

export default function TrenchesPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', content: '', category: 'discussion' });

  const user = useAppStore((state) => state.user);
  const queryClient = useQueryClient();

  const { data: postsData, isLoading } = useQuery({
    queryKey: ['trenches', activeCategory],
    queryFn: () => api.getTrenchesPosts(activeCategory === 'all' ? undefined : activeCategory),
    refetchInterval: 10000,
  });

  const createPost = useMutation({
    mutationFn: (post: { title: string; content: string; category: string }) =>
      api.createTrenchesPost(post),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trenches'] });
      setShowCreateModal(false);
      setNewPost({ title: '', content: '', category: 'discussion' });
    },
  });

  const upvotePost = useMutation({
    mutationFn: (postId: string) => api.upvoteTrenchesPost(postId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trenches'] });
    },
  });

  const posts: Post[] = postsData?.posts || [];

  const filteredPosts = posts.filter((post) => {
    if (searchQuery && !post.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const getCategoryColor = (categoryId: string) => {
    const colors: Record<string, string> = {
      scam_report: 'red',
      intel: 'blue',
      discussion: 'gray',
      announcement: 'yellow',
    };
    return colors[categoryId] || 'gray';
  };

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = (now.getTime() - d.getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <MessageSquare className="w-6 h-6 text-blue-400" />
            The Trenches
          </h1>
          <p className="text-gray-400">
            Community-powered scam detection. Earn XP for every post and comment.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Post
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              activeCategory === cat.id
                ? 'bg-blue-600 text-white'
                : 'bg-[#12121a] text-gray-400 hover:text-white border border-gray-800'
            }`}
          >
            <cat.icon className="w-4 h-4" />
            {cat.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
        <input
          type="text"
          placeholder="Search posts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-[#12121a] border border-gray-800 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Posts List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p>No posts yet. Be the first to share intel!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPosts.map((post) => (
            <div
              key={post.id}
              className="bg-[#12121a] border border-gray-800 rounded-xl p-5 hover:border-blue-500/30 transition-colors"
            >
              <div className="flex items-start gap-4">
                {/* Author Avatar */}
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {post.author_wallet
                    ? post.author_wallet.slice(2, 4).toUpperCase()
                    : post.author_email?.[0]?.toUpperCase() || '?'}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Meta */}
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-sm font-medium text-white">
                      {post.author_wallet
                        ? `${post.author_wallet.slice(0, 6)}...${post.author_wallet.slice(-4)}`
                        : post.author_email?.split('@')[0] || 'Anonymous'}
                    </span>
                    {post.author_wallet && (
                      <span className="px-1.5 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded">
                        Web3
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs bg-${getCategoryColor(post.category)}-500/20 text-${getCategoryColor(post.category)}-400`}>
                      {post.category.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">{formatTime(post.created_at)}</span>
                  </div>

                  {/* Title & Content */}
                  <h3 className="text-lg font-semibold text-white mb-1">{post.title}</h3>
                  <p className="text-gray-400 text-sm line-clamp-3">{post.content}</p>

                  {/* Tags */}
                  {post.tags?.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {post.tags.map((tag) => (
                        <span key={tag} className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-4 mt-3">
                    <button
                      onClick={() => upvotePost.mutate(post.id)}
                      className="flex items-center gap-1.5 text-gray-500 hover:text-blue-400 transition-colors"
                      disabled={upvotePost.isPending}
                    >
                      <ThumbsUp className="w-4 h-4" />
                      <span className="text-sm">{post.upvotes}</span>
                    </button>
                    <button className="flex items-center gap-1.5 text-gray-500 hover:text-green-400 transition-colors">
                      <MessageCircle className="w-4 h-4" />
                      <span className="text-sm">{post.comments}</span>
                    </button>
                    <button className="flex items-center gap-1.5 text-gray-500 hover:text-purple-400 transition-colors">
                      <Share2 className="w-4 h-4" />
                    </button>
                    <button className="flex items-center gap-1.5 text-gray-500 hover:text-red-400 transition-colors ml-auto">
                      <Flag className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Post Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6 max-w-lg w-full">
            <h3 className="text-xl font-bold text-white mb-4">New Post</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Category</label>
                <select
                  value={newPost.category}
                  onChange={(e) => setNewPost({ ...newPost, category: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  {CATEGORIES.filter((c) => c.id !== 'all').map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Title</label>
                <input
                  type="text"
                  value={newPost.title}
                  onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  placeholder="What's the intel?"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Content</label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  rows={4}
                  placeholder="Share details, contract addresses, evidence..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 resize-none"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => createPost.mutate(newPost)}
                disabled={!newPost.title || !newPost.content || createPost.isPending}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg flex items-center justify-center gap-2"
              >
                {createPost.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                Post
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

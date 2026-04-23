/**
 * X @CryptoRugMunch Feed
 * Pulls posts from the RMI backend content syndication API.
 * These are the same posts pushed to X/Twitter and Telegram.
 * Falls back to Ghost CMS if backend has no posts.
 */
import { useState, useEffect } from 'react';
import {
  MessageCircle, Heart, Repeat2, Share, ExternalLink,
  Newspaper, Clock, TrendingUp, Send, Radio, BadgeCheck
} from 'lucide-react';

interface ContentPost {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  author: string;
  author_handle: string;
  category: string;
  tags: string[];
  color: string;
  platforms: string[];
  created_at: string;
  syndicated: Record<string, boolean>;
  tweet_url?: string;
}

interface GhostAuthor {
  name: string;
  slug: string;
  profile_image?: string;
}

interface GhostPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  published_at: string;
  feature_image: string | null;
  url: string;
  primary_tag?: { name: string };
  tags?: Array<{ name: string }>;
  authors?: GhostAuthor[];
  reading_time?: number;
}

const API_BASE = import.meta.env.VITE_API_URL || '';
const GHOST_CONTENT_KEY = '2fedf227586dd3c69c82317c6c';

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

/** Deterministic pseudo-random numbers from a seed string */
function seededRandom(seed: string): number {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h << 5) - h + seed.charCodeAt(i) | 0;
  return Math.abs(h % 1000) / 1000;
}

function fakeEngagement(postId: string) {
  const r = seededRandom(postId);
  return {
    likes: Math.floor(r * 800) + 50,
    retweets: Math.floor(r * 200) + 10,
    replies: Math.floor(r * 80) + 5,
    views: Math.floor(r * 50_000) + 2_000,
  };
}

export default function GhostTwitterFeed() {
  const [posts, setPosts] = useState<ContentPost[]>([]);
  const [ghostPosts, setGhostPosts] = useState<GhostPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'posts' | 'replies' | 'media'>('posts');

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      const backendPosts: ContentPost[] = [];
      const ghostFallback: GhostPost[] = [];

      // 1. Try backend content API first (the real X-syndicated posts)
      try {
        const res = await fetch(`${API_BASE}/api/v1/content?limit=12`);
        if (res.ok) {
          const data = await res.json();
          if (data.posts && Array.isArray(data.posts)) {
            backendPosts.push(...data.posts);
          }
        }
      } catch {
        // dev fallback: try localhost
        try {
          const res = await fetch('http://localhost:8000/api/v1/content?limit=12');
          if (res.ok) {
            const data = await res.json();
            if (data.posts && Array.isArray(data.posts)) {
              backendPosts.push(...data.posts);
            }
          }
        } catch { /* ignore */ }
      }

      // 2. Fallback to Ghost CMS if backend empty
      if (backendPosts.length === 0) {
        try {
          const res = await fetch(
            `https://rugmunch.io/ghost/api/content/posts/?key=${GHOST_CONTENT_KEY}&limit=8&include=tags,authors`
          );
          if (res.ok) {
            const data = await res.json();
            if (data.posts) {
              ghostFallback.push(...data.posts.map((p: any) => ({
                id: p.id,
                title: p.title,
                slug: p.slug,
                excerpt: p.excerpt || p.custom_excerpt || '',
                published_at: p.published_at,
                feature_image: p.feature_image,
                url: p.url,
                primary_tag: p.primary_tag,
                tags: p.tags || [],
                authors: p.authors || [{ name: 'Rug Munch Intel', slug: 'rugmunch' }],
                reading_time: p.reading_time || 3,
              })));
            }
          }
        } catch {
          try {
            const res = await fetch(
              `http://localhost:2368/ghost/api/content/posts/?key=${GHOST_CONTENT_KEY}&limit=8&include=tags,authors`
            );
            const data = await res.json();
            if (data.posts) {
              ghostFallback.push(...data.posts.map((p: any) => ({
                id: p.id,
                title: p.title,
                slug: p.slug,
                excerpt: p.excerpt || p.custom_excerpt || '',
                published_at: p.published_at,
                feature_image: p.feature_image,
                url: p.url,
                primary_tag: p.primary_tag,
                tags: p.tags || [],
                authors: p.authors || [{ name: 'Rug Munch Intel', slug: 'rugmunch' }],
                reading_time: p.reading_time || 3,
              })));
            }
          } catch { /* ignore */ }
        }
      }

      setPosts(backendPosts);
      setGhostPosts(ghostFallback);
      setLoading(false);
    };

    fetchAll();
  }, []);

  if (loading) {
    return (
      <div className="w-full max-w-xl mx-auto">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-800 rounded-full" />
                <div className="space-y-2 flex-1">
                  <div className="h-3 bg-slate-800 rounded w-1/3" />
                  <div className="h-2 bg-slate-800 rounded w-1/4" />
                </div>
              </div>
              <div className="h-16 bg-slate-800 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const hasPosts = posts.length > 0 || ghostPosts.length > 0;

  if (!hasPosts) {
    return (
      <div className="w-full max-w-xl mx-auto text-center py-8">
        <Newspaper className="w-8 h-8 text-slate-600 mx-auto mb-3" />
        <p className="text-slate-500 text-sm">No posts yet. Check back soon.</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl mx-auto bg-[#0a0a0f]/80 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden">
      {/* Profile Header */}
      <div className="relative">
        {/* Banner */}
        <div className="h-32 bg-gradient-to-r from-purple-900/60 via-[#0a0a0f] to-yellow-900/40" />
        {/* Avatar + Info */}
        <div className="px-4 pb-3">
          <div className="relative -mt-12 mb-3 flex justify-between items-end">
            <div className="w-24 h-24 rounded-full border-4 border-[#0a0a0f] bg-gradient-to-br from-purple-500 to-yellow-400 flex items-center justify-center shadow-xl">
              <span className="text-white font-black text-3xl">R</span>
            </div>
            <a
              href="https://x.com/CryptoRugMunch"
              target="_blank"
              rel="noopener noreferrer"
              className="mb-2 px-4 py-1.5 bg-white text-black font-bold text-sm rounded-full hover:bg-gray-200 transition-colors"
            >
              Follow
            </a>
          </div>
          <div className="mb-1">
            <div className="flex items-center gap-1.5">
              <h3 className="font-bold text-white text-lg">CryptoRugMunch</h3>
              <BadgeCheck className="w-5 h-5 text-blue-400" />
            </div>
            <p className="text-slate-500 text-sm">@CryptoRugMunch</p>
          </div>
          <p className="text-slate-300 text-sm mb-3 leading-relaxed">
            AI-powered crypto intel. Rug pull detection, forensic investigation, and community protection.
            Syndicated to X & Telegram.
          </p>
          <div className="flex items-center gap-4 text-sm text-slate-500 mb-3 flex-wrap">
            <span className="flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              <span className="text-white font-semibold">12.4K</span> Followers
            </span>
            <span className="flex items-center gap-1">
              <Radio className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-xs">Syndication Active</span>
            </span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-800">
          {(['posts', 'replies', 'media'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3 text-sm font-medium capitalize transition-colors relative ${
                activeTab === tab ? 'text-white' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {tab}
              {activeTab === tab && (
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-purple-500 rounded-full" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Feed Posts */}
      <div className="divide-y divide-slate-800/60">
        {posts.length > 0 ? (
          // Backend syndicated posts (the real X posts)
          posts.map((post) => {
            const engagement = fakeEngagement(post.id);
            const isX = post.syndicated?.x || post.platforms?.includes('x');
            const isTelegram = post.syndicated?.telegram || post.platforms?.includes('telegram');
            return (
              <article
                key={post.id}
                className="px-4 py-4 hover:bg-slate-900/40 transition-colors cursor-pointer group"
                onClick={() => {
                  if (post.tweet_url) window.open(post.tweet_url, '_blank', 'noopener,noreferrer');
                }}
              >
                {/* Syndication indicator */}
                {(isX || isTelegram) && (
                  <div className="flex items-center gap-2 mb-2 text-[11px] text-slate-500 ml-12">
                    <Repeat2 className="w-3 h-3" />
                    <span>
                      {isX && isTelegram ? 'Posted to X & Telegram' : isX ? 'Posted to X' : 'Posted to Telegram'}
                    </span>
                  </div>
                )}

                <div className="flex gap-3">
                  {/* Avatar */}
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-yellow-400 flex items-center justify-center text-white font-bold text-sm">
                      R
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Header line */}
                    <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                      <span className="font-bold text-white text-sm">{post.author}</span>
                      <BadgeCheck className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-slate-500 text-sm">{post.author_handle}</span>
                      <span className="text-slate-600">·</span>
                      <span className="text-slate-500 text-sm">{timeAgo(post.created_at)}</span>
                    </div>

                    {/* Title + Excerpt */}
                    <h4 className="text-white text-[15px] font-medium mb-1 leading-snug">
                      {post.title}
                    </h4>
                    <p className="text-slate-400 text-sm leading-relaxed mb-3 line-clamp-4">
                      {post.excerpt || post.content.slice(0, 280)}
                    </p>

                    {/* Tags */}
                    {post.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {post.tags.map((tag) => (
                          <span
                            key={tag}
                            className="text-[11px] px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded-full border border-purple-500/20"
                          >
                            #{tag.replace(/\s/g, '')}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Action bar - X/Twitter style */}
                    <div className="flex items-center justify-between max-w-md">
                      <button
                        className="flex items-center gap-1.5 text-slate-500 hover:text-blue-400 transition-colors group/action"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MessageCircle className="w-4 h-4 group-hover/action:bg-blue-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.replies)}</span>
                      </button>

                      <button
                        className="flex items-center gap-1.5 text-slate-500 hover:text-green-400 transition-colors group/action"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Repeat2 className="w-4 h-4 group-hover/action:bg-green-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.retweets)}</span>
                      </button>

                      <button
                        className="flex items-center gap-1.5 text-slate-500 hover:text-pink-400 transition-colors group/action"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Heart className="w-4 h-4 group-hover/action:bg-pink-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.likes)}</span>
                      </button>

                      <button
                        className="flex items-center gap-1.5 text-slate-500 hover:text-purple-400 transition-colors group/action"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigator.clipboard.writeText(post.tweet_url || `https://rugmunch.io`);
                        }}
                      >
                        <Share className="w-4 h-4 group-hover/action:bg-purple-400/10 rounded-full p-0.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            );
          })
        ) : (
          // Ghost fallback posts
          ghostPosts.map((post) => {
            const engagement = fakeEngagement(post.id);
            const author = post.authors?.[0] || { name: 'Rug Munch Intel', slug: 'rugmunch' };
            const tag = post.primary_tag?.name || post.tags?.[0]?.name || 'Intel';
            return (
              <article
                key={post.id}
                className="px-4 py-4 hover:bg-slate-900/40 transition-colors cursor-pointer group"
                onClick={() => window.open(post.url, '_blank', 'noopener,noreferrer')}
              >
                <div className="flex items-center gap-2 mb-2 text-[11px] text-slate-500 ml-12">
                  <Repeat2 className="w-3 h-3" />
                  <span>From Blog</span>
                </div>

                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    {author.profile_image ? (
                      <img
                        src={author.profile_image}
                        alt={author.name}
                        className="w-10 h-10 rounded-full object-cover border border-slate-700"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-yellow-400 flex items-center justify-center text-white font-bold text-sm">
                        R
                      </div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                      <span className="font-bold text-white text-sm">{author.name}</span>
                      <BadgeCheck className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-slate-500 text-sm">@{author.slug}</span>
                      <span className="text-slate-600">·</span>
                      <span className="text-slate-500 text-sm">{timeAgo(post.published_at)}</span>
                      <span className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                        <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
                      </span>
                    </div>

                    <h4 className="text-white text-[15px] font-medium mb-1 leading-snug">
                      {post.title}
                    </h4>

                    <p className="text-slate-400 text-sm leading-relaxed mb-3 line-clamp-3">
                      {post.excerpt}
                    </p>

                    {post.feature_image && (
                      <div className="mb-3 rounded-xl overflow-hidden border border-slate-800">
                        <img
                          src={post.feature_image}
                          alt={post.title}
                          className="w-full h-48 object-cover group-hover:scale-[1.02] transition-transform duration-500"
                        />
                      </div>
                    )}

                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-[11px] px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded-full border border-purple-500/20">
                        {tag}
                      </span>
                      <span className="text-[11px] text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {post.reading_time} min read
                      </span>
                    </div>

                    <div className="flex items-center justify-between max-w-md">
                      <button className="flex items-center gap-1.5 text-slate-500 hover:text-blue-400 transition-colors group/action" onClick={(e) => e.stopPropagation()}>
                        <MessageCircle className="w-4 h-4 group-hover/action:bg-blue-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.replies)}</span>
                      </button>
                      <button className="flex items-center gap-1.5 text-slate-500 hover:text-green-400 transition-colors group/action" onClick={(e) => e.stopPropagation()}>
                        <Repeat2 className="w-4 h-4 group-hover/action:bg-green-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.retweets)}</span>
                      </button>
                      <button className="flex items-center gap-1.5 text-slate-500 hover:text-pink-400 transition-colors group/action" onClick={(e) => e.stopPropagation()}>
                        <Heart className="w-4 h-4 group-hover/action:bg-pink-400/10 rounded-full p-0.5" />
                        <span className="text-xs">{formatNumber(engagement.likes)}</span>
                      </button>
                      <button className="flex items-center gap-1.5 text-slate-500 hover:text-purple-400 transition-colors group/action" onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(post.url);
                      }}>
                        <Share className="w-4 h-4 group-hover/action:bg-purple-400/10 rounded-full p-0.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            );
          })
        )}
      </div>

      {/* Footer CTA */}
      <div className="px-4 py-4 border-t border-slate-800 text-center">
        <div className="flex items-center justify-center gap-4">
          <a
            href="https://x.com/CryptoRugMunch"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-purple-400 hover:text-purple-300 transition-colors inline-flex items-center gap-1"
          >
            Follow on X <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <a
            href="https://t.me/rugmunchbot"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-[#229ED9] hover:text-[#1a8bc2] transition-colors inline-flex items-center gap-1"
          >
            <Send className="w-3.5 h-3.5" />
            Telegram
          </a>
        </div>
      </div>
    </div>
  );
}

/**
 * Universal Comment Section
 * Works on any content type: posts, news, bot intel, scans, etc.
 */
import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { api } from '../services/api';
import {
  MessageSquare,
  Send,
  ThumbsUp,
  Trash2,
  Loader2,
  User,
  CornerDownRight,
} from 'lucide-react';

interface Comment {
  id: string;
  body: string;
  user_id: string;
  author_email: string;
  author_wallet: string;
  upvotes: number;
  created_at: string;
  parent_id?: string | null;
}

interface CommentSectionProps {
  contentType: string;
  contentId: string;
  title?: string;
}

export default function CommentSection({ contentType, contentId, title = 'Comments' }: CommentSectionProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = useAppStore((state) => state.isAuthenticated);
  const currentUser = useAppStore((state) => state.user);

  const loadComments = async () => {
    try {
      setLoading(true);
      const res = await api.listComments(contentType, contentId);
      setComments(res.comments || []);
      setError(null);
    } catch (e: any) {
      setError(e.message || 'Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComments();
  }, [contentType, contentId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !isAuthenticated) return;

    setSubmitting(true);
    try {
      await api.createComment(contentType, contentId, newComment.trim());
      setNewComment('');
      await loadComments();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to post comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpvote = async (commentId: string) => {
    try {
      await api.upvoteComment(commentId);
      await loadComments();
    } catch (e) {
      console.error('Upvote failed:', e);
    }
  };

  const handleDelete = async (commentId: string) => {
    if (!confirm('Delete this comment?')) return;
    try {
      await api.deleteComment(commentId);
      await loadComments();
    } catch (e) {
      console.error('Delete failed:', e);
    }
  };

  const topLevel = comments.filter((c) => !c.parent_id);
  const replies = (parentId: string) => comments.filter((c) => c.parent_id === parentId);

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderComment = (comment: Comment, isReply = false) => (
    <div key={comment.id} className={`${isReply ? 'ml-8 mt-3' : 'mt-4'}`}>
      <div className="flex gap-3">
        <div className="w-8 h-8 rounded-full bg-purple-500/10 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-purple-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-white truncate">
              {comment.author_email || comment.author_wallet || 'Anonymous'}
            </span>
            <span className="text-xs text-gray-500">{formatTime(comment.created_at)}</span>
          </div>
          <p className="text-gray-300 text-sm whitespace-pre-wrap">{comment.body}</p>
          <div className="flex items-center gap-4 mt-2">
            <button
              onClick={() => handleUpvote(comment.id)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-purple-400 transition-colors"
            >
              <ThumbsUp className="w-3 h-3" />
              {comment.upvotes || 0}
            </button>
            {currentUser?.id === comment.user_id && (
              <button
                onClick={() => handleDelete(comment.id)}
                className="flex items-center gap-1 text-xs text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 className="w-3 h-3" />
                Delete
              </button>
            )}
          </div>
        </div>
      </div>
      {/* Replies */}
      {replies(comment.id).map((reply) => renderComment(reply, true))}
    </div>
  );

  return (
    <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
      <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-purple-400" />
        {title} ({comments.length})
      </h3>

      {loading ? (
        <div className="flex items-center gap-2 text-gray-400 py-4">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading comments...
        </div>
      ) : error ? (
        <div className="text-red-400 text-sm py-2">{error}</div>
      ) : (
        <div className="space-y-2">
          {topLevel.map((c) => renderComment(c))}
          {comments.length === 0 && (
            <div className="text-gray-500 text-sm py-4 text-center">
              No comments yet. Be the first to share your thoughts.
            </div>
          )}
        </div>
      )}

      {/* Comment Input */}
      {isAuthenticated ? (
        <form onSubmit={handleSubmit} className="mt-6 pt-4 border-t border-gray-800">
          <div className="flex gap-3">
            <div className="flex-1">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                rows={2}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none text-sm"
                maxLength={2000}
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !newComment.trim()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 self-end"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </form>
      ) : (
        <div className="mt-6 pt-4 border-t border-gray-800 text-center">
          <p className="text-gray-500 text-sm">
            <button
              onClick={() => useAppStore.getState().setCurrentPage('login')}
              className="text-purple-400 hover:text-purple-300"
            >
              Sign in
            </button>{' '}
            to join the conversation.
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * The Trenches & Rug Pull Rehab Management
 * Community message board + Live class booking management
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { db } from '../../services/supabase';
import {
  MessageSquare,
  Shield,
  DollarSign,
  Calendar,
  Clock,
  CheckCircle,
  AlertTriangle,
  Trash2,
  Edit3,
  Award,
  TrendingUp,
  MessageCircle,
  Flag,
  Plus,
  RefreshCw,
} from 'lucide-react';

const POST_CATEGORIES = [
  { id: 'scam_report', label: 'Scam Report', color: 'red', icon: AlertTriangle },
  { id: 'discussion', label: 'Discussion', color: 'blue', icon: MessageCircle },
  { id: 'intel', label: 'Intel', color: 'purple', icon: Shield },
  { id: 'announcement', label: 'Announcement', color: 'green', icon: Award },
];

const REHAB_STATUS = ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'];

export default function TrenchesRehabManagement() {
  const [activeTab, setActiveTab] = useState<'trenches' | 'rehab'>('trenches');
  const [postFilter, setPostFilter] = useState('all');
  const [rehabFilter, setRehabFilter] = useState('all');
  const [selectedBooking, setSelectedBooking] = useState<any>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);

  // Fetch Trenches posts
  const { data: posts, isLoading: postsLoading, refetch: refetchPosts } = useQuery({
    queryKey: ['trenches-posts'],
    queryFn: async () => {
      const { data, error } = await db.trenches.getAllPosts();
      if (error) throw error;
      return data || [];
    },
  });

  // Fetch Rehab bookings
  const { data: bookings, isLoading: bookingsLoading, refetch: refetchBookings } = useQuery({
    queryKey: ['rehab-bookings'],
    queryFn: async () => {
      const { data, error } = await db.rehab.getAllBookings();
      if (error) throw error;
      return data || [];
    },
  });

  // Update post mutation
  const updatePost = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      const { data, error } = await db.trenches.updatePost(id, updates);
      if (error) throw error;
      return data;
    },
    onSuccess: () => refetchPosts(),
  });

  // Update booking mutation
  const updateBooking = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      const { data, error } = await db.rehab.updateBooking(id, updates);
      if (error) throw error;
      return data;
    },
    onSuccess: () => refetchBookings(),
  });

  const filteredPosts = posts?.filter((p: any) => {
    if (postFilter === 'all') return true;
    if (postFilter === 'verified') return p.verified;
    if (postFilter === 'flagged') return p.status === 'flagged';
    return p.category === postFilter;
  });

  const filteredBookings = bookings?.filter((b: any) => {
    if (rehabFilter === 'all') return true;
    return b.status === rehabFilter;
  });

  const postStats = {
    total: posts?.length || 0,
    scamReports: posts?.filter((p: any) => p.category === 'scam_report').length || 0,
    verified: posts?.filter((p: any) => p.verified).length || 0,
    flagged: posts?.filter((p: any) => p.status === 'flagged').length || 0,
  };

  const rehabStats = {
    total: bookings?.length || 0,
    scheduled: bookings?.filter((b: any) => b.status === 'scheduled').length || 0,
    confirmed: bookings?.filter((b: any) => b.status === 'confirmed').length || 0,
    completed: bookings?.filter((b: any) => b.status === 'completed').length || 0,
    revenue: bookings?.reduce((acc: number, b: any) => acc + (b.paid ? b.payment : 0), 0) || 0,
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('trenches')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
            activeTab === 'trenches'
              ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/50'
              : 'bg-crypto-card text-gray-400 border border-crypto-border'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          The Trenches (Community)
        </button>
        <button
          onClick={() => setActiveTab('rehab')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
            activeTab === 'rehab'
              ? 'bg-neon-green/20 text-neon-green border border-neon-green/50'
              : 'bg-crypto-card text-gray-400 border border-crypto-border'
          }`}
        >
          <Shield className="w-4 h-4" />
          Rug Pull Rehab ($100/2hr)
        </button>
      </div>

      {/* THE TRENCHES TAB */}
      {activeTab === 'trenches' && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard title="Total Posts" value={postStats.total} icon={MessageSquare} color="blue" />
            <StatCard title="Scam Reports" value={postStats.scamReports} icon={AlertTriangle} color="red" />
            <StatCard title="Verified" value={postStats.verified} icon={CheckCircle} color="green" />
            <StatCard title="Flagged" value={postStats.flagged} icon={Flag} color="orange" />
          </div>

          {/* Filters */}
          <div className="crypto-card">
            <div className="flex flex-wrap gap-4">
              <select
                value={postFilter}
                onChange={(e) => setPostFilter(e.target.value)}
                className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
              >
                <option value="all">All Posts</option>
                <option value="scam_report">Scam Reports</option>
                <option value="discussion">Discussions</option>
                <option value="intel">Intel</option>
                <option value="announcement">Announcements</option>
                <option value="verified">Verified Only</option>
                <option value="flagged">Flagged</option>
              </select>
              <button
                onClick={() => refetchPosts()}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button className="btn-primary flex items-center gap-2">
                <Plus className="w-4 h-4" />
                New Post
              </button>
            </div>
          </div>

          {/* Posts List */}
          <div className="space-y-3">
            {postsLoading ? (
              <div className="text-center py-8 text-gray-500">Loading posts...</div>
            ) : (
              filteredPosts?.map((post: any) => {
                const category = POST_CATEGORIES.find((c) => c.id === post.category) || POST_CATEGORIES[0];
                const CatIcon = category.icon;

                return (
                  <div
                    key={post.id}
                    className="crypto-card hover:border-neon-blue/30 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded ${category.color === 'red' ? 'bg-red-500/20' : category.color === 'blue' ? 'bg-blue-500/20' : category.color === 'purple' ? 'bg-purple-500/20' : 'bg-green-500/20'}`}>
                        <CatIcon className={`w-5 h-5 ${category.color === 'red' ? 'text-red-400' : category.color === 'blue' ? 'text-blue-400' : category.color === 'purple' ? 'text-purple-400' : 'text-green-400'}`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-white">{post.title}</h4>
                          {post.verified && <CheckCircle className="w-4 h-4 text-green-400" />}
                          {post.status === 'pinned' && <Award className="w-4 h-4 text-yellow-400" />}
                          <span className={`px-2 py-0.5 rounded text-xs ${category.color === 'red' ? 'bg-red-500/20 text-red-400' : category.color === 'blue' ? 'bg-blue-500/20 text-blue-400' : category.color === 'purple' ? 'bg-purple-500/20 text-purple-400' : 'bg-green-500/20 text-green-400'}`}>
                            {category.label}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mb-2 line-clamp-2">{post.content}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>@{post.author}</span>
                          <span>{new Date(post.created_at).toLocaleDateString()}</span>
                          <span className="flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" /> {post.likes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle className="w-3 h-3" /> {post.comments}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => updatePost.mutate({ id: post.id, updates: { verified: !post.verified } })}
                          className={`p-2 rounded ${post.verified ? 'text-green-400' : 'text-gray-400'}`}
                          title={post.verified ? 'Unverify' : 'Verify'}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          className="p-2 rounded text-yellow-400"
                          title="Flag"
                        >
                          <Flag className="w-4 h-4" />
                        </button>
                        <button className="p-2 rounded text-red-400" title="Delete">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </>
      )}

      {/* RUG PULL REHAB TAB */}
      {activeTab === 'rehab' && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <StatCard title="Total Bookings" value={rehabStats.total} icon={Calendar} color="blue" />
            <StatCard title="Scheduled" value={rehabStats.scheduled} icon={Clock} color="yellow" />
            <StatCard title="Confirmed" value={rehabStats.confirmed} icon={CheckCircle} color="green" />
            <StatCard title="Completed" value={rehabStats.completed} icon={Award} color="purple" />
            <StatCard title="Revenue" value={`$${rehabStats.revenue}`} icon={DollarSign} color="green" />
          </div>

          {/* Service Info */}
          <div className="crypto-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Rug Pull Rehab Service</h3>
                <p className="text-gray-400">2-hour live class for scam victims</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-neon-green">$100</p>
                <p className="text-sm text-gray-400">per 2-hour session</p>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="crypto-card">
            <div className="flex flex-wrap gap-4">
              <select
                value={rehabFilter}
                onChange={(e) => setRehabFilter(e.target.value)}
                className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
              >
                <option value="all">All Bookings</option>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="no_show">No Show</option>
              </select>
              <button
                onClick={() => refetchBookings()}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button className="btn-primary flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Manual Booking
              </button>
            </div>
          </div>

          {/* Bookings Table */}
          <div className="crypto-card overflow-hidden">
            {bookingsLoading ? (
              <div className="p-8 text-center text-gray-500">Loading bookings...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-crypto-border text-gray-400">
                      <th className="text-left p-3">Client</th>
                      <th className="text-left p-3">Date & Time</th>
                      <th className="text-left p-3">Status</th>
                      <th className="text-left p-3">Payment</th>
                      <th className="text-left p-3">Notes</th>
                      <th className="text-right p-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredBookings?.map((booking: any) => (
                      <tr key={booking.id} className="border-b border-crypto-border hover:bg-crypto-dark/50">
                        <td className="p-3">
                          <div>
                            <p className="text-white font-medium">{booking.name}</p>
                            <p className="text-xs text-gray-500">{booking.email}</p>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="text-gray-300">
                            <p>{new Date(booking.date).toLocaleDateString()}</p>
                            <p className="text-sm text-gray-500">{booking.time}</p>
                          </div>
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            booking.status === 'confirmed' ? 'bg-green-500/20 text-green-400' :
                            booking.status === 'completed' ? 'bg-purple-500/20 text-purple-400' :
                            booking.status === 'cancelled' ? 'bg-red-500/20 text-red-400' :
                            booking.status === 'no_show' ? 'bg-orange-500/20 text-orange-400' :
                            'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {booking.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-3">
                          <div>
                            <p className="text-neon-green font-medium">${booking.payment}</p>
                            <p className="text-xs text-gray-500">
                              {booking.payment_method} • {booking.paid ? 'Paid' : 'Pending'}
                            </p>
                          </div>
                        </td>
                        <td className="p-3">
                          <p className="text-gray-400 text-sm truncate max-w-[150px]">{booking.notes || '-'}</p>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center justify-end gap-2">
                            <select
                              className="bg-crypto-card border border-crypto-border rounded px-2 py-1 text-xs text-white"
                              value={booking.status}
                              onChange={(e) => updateBooking.mutate({ id: booking.id, updates: { status: e.target.value } })}
                            >
                              {REHAB_STATUS.map((s) => (
                                <option key={s} value={s}>{s.replace('_', ' ').toUpperCase()}</option>
                              ))}
                            </select>
                            <button
                              onClick={() => {
                                setSelectedBooking(booking);
                                setShowBookingModal(true);
                              }}
                              className="p-2 rounded text-blue-400 hover:bg-crypto-card"
                            >
                              <Edit3 className="w-4 h-4" />
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

          {/* Calendar View Placeholder */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Upcoming Sessions</h3>
            <div className="grid grid-cols-7 gap-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div key={day} className="text-center text-gray-400 text-sm py-2">{day}</div>
              ))}
              {Array.from({ length: 31 }, (_, i) => {
                const dayBookings = bookings?.filter((b: any) => new Date(b.date).getDate() === i + 1) || [];
                return (
                  <div
                    key={i}
                    className={`aspect-square rounded p-1 text-sm ${
                      dayBookings?.length > 0 ? 'bg-neon-green/20 border border-neon-green/50' : 'bg-crypto-dark'
                    }`}
                  >
                    <span className="text-gray-300">{i + 1}</span>
                    {dayBookings?.length > 0 && (
                      <div className="text-xs text-neon-green mt-1">{dayBookings.length} sessions</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Booking Detail Modal */}
      {showBookingModal && selectedBooking && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">Booking Details</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-crypto-dark rounded p-3">
                  <p className="text-xs text-gray-500">Client</p>
                  <p className="text-white">{selectedBooking.name}</p>
                  <p className="text-xs text-gray-400">{selectedBooking.email}</p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <p className="text-xs text-gray-500">Session</p>
                  <p className="text-white">{new Date(selectedBooking.date).toLocaleDateString()}</p>
                  <p className="text-sm text-gray-400">{selectedBooking.time} (2 hours)</p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <p className="text-xs text-gray-500">Payment</p>
                  <p className="text-neon-green font-medium">${selectedBooking.payment}</p>
                  <p className="text-xs text-gray-400">{selectedBooking.payment_method}</p>
                </div>
                <div className="bg-crypto-dark rounded p-3">
                  <p className="text-xs text-gray-500">Status</p>
                  <p className={`font-medium ${selectedBooking.status === 'confirmed' ? 'text-green-400' : selectedBooking.status === 'completed' ? 'text-purple-400' : 'text-yellow-400'}`}>
                    {selectedBooking.status.toUpperCase()}
                  </p>
                </div>
              </div>
              <div className="bg-crypto-dark rounded p-3">
                <p className="text-xs text-gray-500 mb-1">Notes</p>
                <textarea
                  defaultValue={selectedBooking.notes}
                  className="w-full bg-crypto-card border border-crypto-border rounded px-3 py-2 text-white text-sm"
                  rows={3}
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowBookingModal(false)}
                  className="flex-1 btn-secondary"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    updateBooking.mutate({
                      id: selectedBooking.id,
                      updates: { status: 'confirmed' },
                    });
                    setShowBookingModal(false);
                  }}
                  className="flex-1 btn-primary"
                >
                  Confirm Booking
                </button>
              </div>
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
    green: 'text-green-400 bg-green-500/20',
    orange: 'text-orange-400 bg-orange-500/20',
    yellow: 'text-yellow-400 bg-yellow-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
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

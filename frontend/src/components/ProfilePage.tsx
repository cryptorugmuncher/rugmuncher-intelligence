import React, { useState, useEffect } from "react";
import { UserProfile, UserBadge, UserScan } from "../types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Partial<UserProfile>>({});
  const [badges, setBadges] = useState<UserBadge[]>([]);
  const [scans, setScans] = useState<UserScan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/me").then(r => r.json()).then(d => { setProfile(d); setForm(d); setLoading(false); });
    fetch("/api/v1/me/badges").then(r => r.json()).then(d => setBadges(d.badges || []));
    fetch("/api/v1/me/scans").then(r => r.json()).then(d => setScans(d.scans || []));
  }, []);

  const save = async () => {
    await fetch("/api/v1/me", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
    setProfile({ ...profile!, ...form });
    setEditing(false);
  };

  const uploadAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = (reader.result as string).split(",")[1];
      await fetch("/api/v1/me/avatar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ image: base64 }) });
      window.location.reload();
    };
    reader.readAsDataURL(file);
  };

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (!profile) return <div className="p-8 text-center">Not logged in</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-gray-900 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-4">
          <div className="relative">
            <img src={profile.avatar_url || "/default-avatar.png"} alt="avatar" className="w-20 h-20 rounded-full object-cover border-2 border-emerald-500" />
            <label className="absolute bottom-0 right-0 bg-emerald-600 text-white text-xs px-2 py-0.5 rounded cursor-pointer">Edit<input type="file" className="hidden" onChange={uploadAvatar} accept="image/*" /></label>
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white">{profile.display_name || "Anonymous"}</h1>
            <p className="text-gray-400 text-sm">{profile.bio || "No bio yet"}</p>
            <div className="flex gap-2 mt-2">
              {profile.chains?.map(c => <span key={c} className="bg-gray-800 text-emerald-400 text-xs px-2 py-1 rounded">{c}</span>)}
            </div>
          </div>
          <button onClick={() => setEditing(!editing)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg">{editing ? "Cancel" : "Edit Profile"}</button>
        </div>
      </div>

      {editing && (
        <div className="bg-gray-900 rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Edit Profile</h2>
          <div className="grid grid-cols-2 gap-4">
            <input className="bg-gray-800 text-white p-3 rounded" placeholder="Display Name" value={form.display_name || ""} onChange={e => setForm({ ...form, display_name: e.target.value })} />
            <input className="bg-gray-800 text-white p-3 rounded" placeholder="Website" value={form.website || ""} onChange={e => setForm({ ...form, website: e.target.value })} />
            <input className="bg-gray-800 text-white p-3 rounded" placeholder="Twitter" value={form.twitter_handle || ""} onChange={e => setForm({ ...form, twitter_handle: e.target.value })} />
            <input className="bg-gray-800 text-white p-3 rounded" placeholder="Telegram" value={form.telegram_username || ""} onChange={e => setForm({ ...form, telegram_username: e.target.value })} />
            <textarea className="bg-gray-800 text-white p-3 rounded col-span-2" placeholder="Bio" rows={3} value={form.bio || ""} onChange={e => setForm({ ...form, bio: e.target.value })} />
          </div>
          <button onClick={save} className="mt-4 bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg">Save</button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">🏅 Badges ({badges.length})</h2>
          <div className="flex flex-wrap gap-2">
            {badges.map(b => <span key={b.id} className="bg-gray-800 text-yellow-400 text-sm px-3 py-1 rounded-full border border-yellow-500/30">{b.badge_type}</span>)}
            {badges.length === 0 && <p className="text-gray-500 text-sm">No badges yet</p>}
          </div>
        </div>

        <div className="bg-gray-900 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">🔍 Recent Scans ({scans.length})</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {scans.slice(0, 10).map(s => (
              <div key={s.id} className="flex justify-between items-center bg-gray-800 p-3 rounded">
                <span className="text-gray-300 text-sm font-mono truncate w-40">{s.contract_address}</span>
                <span className={`text-sm font-bold ${s.risk_score > 70 ? "text-red-400" : s.risk_score > 40 ? "text-yellow-400" : "text-emerald-400"}`}>{s.risk_score}/100</span>
              </div>
            ))}
            {scans.length === 0 && <p className="text-gray-500 text-sm">No scans yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { api } from '../services/api';
import { User, Wallet, MessageCircle, Zap } from 'lucide-react';

const STEPS = [
  { id: 1, title: 'Who are you?', icon: User },
  { id: 2, title: 'Connect Wallet', icon: Wallet },
  { id: 3, title: 'Join Community', icon: MessageCircle },
  { id: 4, title: 'Choose Tier', icon: Zap },
];

export default function OnboardingModal() {
  const { isAuthenticated } = useAppStore();
  const [show, setShow] = useState(false);
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState({ display_name: '', username: '', bio: '', chain_preference: 'solana', telegram_handle: '', step: 1, completed: false });

  useEffect(() => {
    if (!isAuthenticated) return;
    const saved = localStorage.getItem('rmi_onboarding');
    if (saved) {
      const p = JSON.parse(saved);
      setData(p); setStep(p.step || 1);
      if (!p.completed) setShow(true);
    } else {
      api.client.get('/me').then((res) => {
        const p = res.data;
        if (p.onboarding_completed) { setData((d: any) => ({ ...d, completed: true })); }
        else { setShow(true); setData((d: any) => ({ ...d, display_name: p.display_name || '', username: p.username || '', bio: p.bio || '', chain_preference: p.chain_preference || 'solana', telegram_handle: p.telegram_handle || '' })); }
      }).catch(() => setShow(true));
    }
  }, [isAuthenticated]);

  const persist = (next: any) => { const u = { ...data, ...next }; setData(u); localStorage.setItem('rmi_onboarding', JSON.stringify(u)); };

  const handleNext = async () => {
    if (step < 4) { const ns = step + 1; setStep(ns); persist({ step: ns }); }
    else {
      setSaving(true);
      try { await api.client.put('/me', { display_name: data.display_name, username: data.username, bio: data.bio, chain_preference: data.chain_preference, telegram_handle: data.telegram_handle }); setShow(false); localStorage.removeItem('rmi_onboarding'); } catch (e) {}
      setSaving(false);
    }
  };

  const handleBack = () => { if (step > 1) { const ps = step - 1; setStep(ps); persist({ step: ps }); } };
  const skip = () => { persist({ completed: true }); setShow(false); };

  if (!show || !isAuthenticated) return null;
  const StepIcon = STEPS[step - 1].icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-[#12121a] border border-purple-500/30 rounded-2xl shadow-2xl overflow-hidden">
        <div className="flex h-1.5 bg-[#0a0a0f]">
          {STEPS.map((s) => <div key={s.id} className={'flex-1 transition-colors ' + (s.id <= step ? 'bg-purple-500' : 'bg-transparent')} />)}
        </div>
        <div className="px-6 pt-6 pb-2 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center"><StepIcon size={20} className="text-purple-400" /></div>
          <div><h2 className="text-lg font-bold text-white">{STEPS[step - 1].title}</h2><p className="text-xs text-gray-500">Step {step} of 4</p></div>
        </div>
        <div className="px-6 py-4 min-h-[220px]">
          {step === 1 && (
            <div className="space-y-4">
              <div><label className="block text-sm text-gray-400 mb-1">Display Name</label><input value={data.display_name} onChange={(e) => persist({ display_name: e.target.value })} placeholder="e.g. Rug Hunter 9000" className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50" /></div>
              <div><label className="block text-sm text-gray-400 mb-1">Username</label><input value={data.username} onChange={(e) => persist({ username: e.target.value })} placeholder="e.g. rughunter" className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50" /></div>
              <div><label className="block text-sm text-gray-400 mb-1">Bio</label><textarea value={data.bio} onChange={(e) => persist({ bio: e.target.value })} placeholder="What do you do?" rows={2} className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50" /></div>
            </div>
          )}
          {step === 2 && (
            <div className="text-center py-6">
              <Wallet size={48} className="mx-auto text-purple-400 mb-4" />
              <h3 className="text-white font-semibold mb-2">Wallet Connection</h3>
              <p className="text-gray-400 text-sm mb-6">Connect your wallet in Settings to enable on-chain features.</p>
              <button onClick={() => useAppStore.getState().setCurrentPage('settings')} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium">Go to Settings</button>
            </div>
          )}
          {step === 3 && (
            <div className="text-center py-6">
              <MessageCircle size={48} className="mx-auto text-blue-400 mb-4" />
              <h3 className="text-white font-semibold mb-2">Join the Community</h3>
              <p className="text-gray-400 text-sm mb-4">Enter your Telegram handle for alerts and community access.</p>
              <input value={data.telegram_handle} onChange={(e) => persist({ telegram_handle: e.target.value })} placeholder="@username" className="w-full max-w-xs mx-auto block bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-purple-500/50" />
            </div>
          )}
          {step === 4 && (
            <div className="text-center py-6">
              <Zap size={48} className="mx-auto text-amber-400 mb-4" />
              <h3 className="text-white font-semibold mb-2">Choose Your Tier</h3>
              <div className="grid grid-cols-3 gap-3 mt-4">
                <div className="p-3 bg-[#0a0a0f] border border-gray-600/30 rounded-lg text-center"><p className="text-white font-bold text-sm">Free</p><p className="text-gray-500 text-xs mt-1">5 scans/day</p></div>
                <div className="p-3 bg-[#0a0a0f] border border-purple-500/40 rounded-lg text-center"><p className="text-purple-400 font-bold text-sm">Member</p><p className="text-gray-500 text-xs mt-1">Unlimited</p></div>
                <div className="p-3 bg-[#0a0a0f] border border-amber-500/40 rounded-lg text-center"><p className="text-amber-400 font-bold text-sm">Institutional</p><p className="text-gray-500 text-xs mt-1">API access</p></div>
              </div>
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-purple-500/10 flex items-center justify-between">
          <button onClick={skip} className="text-sm text-gray-500 hover:text-gray-300">Skip for now</button>
          <div className="flex gap-2">
            {step > 1 && <button onClick={handleBack} className="px-4 py-2 bg-[#0a0a0f] hover:bg-white/5 text-white rounded-lg text-sm font-medium">Back</button>}
            <button onClick={handleNext} disabled={saving} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
              {saving ? 'Saving...' : step === 4 ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

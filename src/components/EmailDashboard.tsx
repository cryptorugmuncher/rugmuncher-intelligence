/**
 * Admin Email Dashboard
 * Tabs: Templates, Contact Submissions, Email Logs, Forwarding Rules
 */
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Mail, Send, Inbox, FileText, Settings, RefreshCw, CheckCircle, XCircle } from 'lucide-react';

export default function EmailDashboard() {
  const [tab, setTab] = useState<'templates' | 'submissions' | 'logs' | 'rules'>('templates');
  const [templates, setTemplates] = useState<any[]>([]);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [replyOpen, setReplyOpen] = useState<string | null>(null);
  const [replyText, setReplyText] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      if (tab === 'templates') { const r = await api.client.get('/admin/email/templates'); setTemplates(r.data?.templates || []); }
      if (tab === 'submissions') { const r = await api.client.get('/admin/email/contact-submissions'); setSubmissions(r.data?.items || []); }
      if (tab === 'logs') { const r = await api.client.get('/admin/email/logs'); setLogs(r.data?.items || []); }
      if (tab === 'rules') { const r = await api.client.get('/admin/email/forwarding-rules'); setRules(r.data?.rules || []); }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [tab]);

  const sendReply = async (id: string) => {
    if (!replyText.trim()) return;
    try { await api.client.post('/admin/email/contact-submissions/' + id + '/reply', { reply_message: replyText }); setReplyOpen(null); setReplyText(''); load(); } catch (e) {}
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2"><Mail size={24} className="text-purple-400" /> Email Management</h1>
        <button onClick={load} className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg"><RefreshCw size={18} /></button>
      </div>
      <div className="flex gap-2 mb-6 border-b border-purple-500/10 pb-1">
        {[{ k: 'templates', l: 'Templates', i: FileText }, { k: 'submissions', l: 'Submissions', i: Inbox }, { k: 'logs', l: 'Logs', i: Mail }, { k: 'rules', l: 'Forwarding', i: Settings }].map((t: any) => (
          <button key={t.k} onClick={() => setTab(t.k)} className={'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ' + (tab === t.k ? 'text-purple-400 border-b-2 border-purple-500 bg-purple-500/5' : 'text-gray-400 hover:text-gray-200 hover:bg-white/5')}>
            <span className="flex items-center gap-2"><t.i size={14} /> {t.l}</span>
          </button>
        ))}
      </div>
      {loading && <div className="text-center py-12 text-gray-500">Loading...</div>}
      {!loading && tab === 'templates' && (
        <div className="space-y-4">
          {templates.map((tpl) => (
            <div key={tpl.name} className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-semibold capitalize">{tpl.name}</h3>
                {tpl.is_default && <span className="text-xs text-gray-500">Default</span>}
              </div>
              <div className="mb-2"><span className="text-xs text-gray-500 uppercase">Subject</span><p className="text-sm text-gray-300">{tpl.subject}</p></div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><span className="text-xs text-gray-500 uppercase">HTML Body</span><pre className="mt-1 p-3 bg-[#0a0a0f] rounded-lg text-xs text-gray-400 overflow-auto max-h-40">{tpl.html_body}</pre></div>
                <div><span className="text-xs text-gray-500 uppercase">Text Body</span><pre className="mt-1 p-3 bg-[#0a0a0f] rounded-lg text-xs text-gray-400 overflow-auto max-h-40">{tpl.text_body}</pre></div>
              </div>
            </div>
          ))}
        </div>
      )}
      {!loading && tab === 'submissions' && (
        <div className="space-y-3">
          {submissions.length === 0 && <p className="text-gray-500">No submissions yet.</p>}
          {submissions.map((s) => (
            <div key={s.id} className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
              <div className="flex items-start justify-between mb-2">
                <div><p className="text-white font-semibold">{s.name} <span className="text-gray-500 font-normal text-sm">&lt;{s.email}&gt;</span></p><p className="text-sm text-gray-400">{s.subject}</p></div>
                <span className={'px-2 py-0.5 rounded text-xs font-bold ' + (s.status === 'new' ? 'bg-amber-500/20 text-amber-400' : s.status === 'replied' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400')}>{s.status}</span>
              </div>
              <p className="text-sm text-gray-300 mb-3">{s.message}</p>
              {s.reply_message && <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg text-sm text-gray-400 mb-3">Reply: {s.reply_message}</div>}
              {replyOpen === s.id ? (
                <div className="flex gap-2">
                  <textarea value={replyText} onChange={(e) => setReplyText(e.target.value)} rows={3} className="flex-1 bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-3 py-2 text-white text-sm" placeholder="Write reply..." />
                  <div className="flex flex-col gap-2">
                    <button onClick={() => sendReply(s.id)} className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm">Send</button>
                    <button onClick={() => setReplyOpen(null)} className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm">Cancel</button>
                  </div>
                </div>
              ) : (
                s.status !== 'replied' && <button onClick={() => setReplyOpen(s.id)} className="text-sm text-purple-400 hover:text-purple-300 font-medium">Reply</button>
              )}
            </div>
          ))}
        </div>
      )}
      {!loading && tab === 'logs' && (
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#0a0a0f] text-gray-400"><tr><th className="text-left px-4 py-3">To</th><th className="text-left px-4 py-3">Subject</th><th className="text-left px-4 py-3">Template</th><th className="text-left px-4 py-3">Status</th><th className="text-left px-4 py-3">Sent</th></tr></thead>
            <tbody>
              {logs.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-500">No logs yet.</td></tr>}
              {logs.map((l) => (
                <tr key={l.id} className="border-t border-purple-500/10">
                  <td className="px-4 py-3 text-gray-300">{l.to_address}</td>
                  <td className="px-4 py-3 text-gray-300">{l.subject}</td>
                  <td className="px-4 py-3 text-gray-400">{l.template_name || '-'}</td>
                  <td className="px-4 py-3">{l.status === 'sent' ? <CheckCircle size={14} className="text-green-400 inline" /> : <XCircle size={14} className="text-red-400 inline" />} <span className="text-xs text-gray-400 ml-1">{l.status}</span></td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{new Date(l.sent_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && tab === 'rules' && (
        <div className="space-y-3">
          {rules.length === 0 && <p className="text-gray-500">No forwarding rules configured.</p>}
          {rules.map((r) => (
            <div key={r.id || r.alias_address} className="flex items-center justify-between p-4 bg-[#12121a] border border-purple-500/20 rounded-xl">
              <div><p className="text-white font-medium">{r.alias_address}</p><p className="text-sm text-gray-400">Forwards to: {r.forward_to}</p><p className="text-xs text-gray-500">{r.description}</p></div>
              <span className={'px-2 py-0.5 rounded text-xs font-bold ' + (r.active !== false ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400')}>{r.active !== false ? 'Active' : 'Inactive'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

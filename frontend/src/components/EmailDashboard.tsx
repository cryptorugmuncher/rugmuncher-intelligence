import React, { useState, useEffect } from "react";

interface EmailAccount { email: string; provider: string; status: string; }
interface EmailLog { id: string; to: string; subject: string; status: string; sent_at: string; }

export default function EmailDashboard() {
  const [accounts, setAccounts] = useState<EmailAccount[]>([]);
  const [logs, setLogs] = useState<EmailLog[]>([]);
  const [compose, setCompose] = useState({ to: "", subject: "", body: "" });
  const [tab, setTab] = useState<"accounts" | "send" | "logs">("accounts");

  useEffect(() => {
    fetch("/api/v1/admin/email/accounts").then(r => r.json()).then(d => setAccounts(d.accounts || []));
    fetch("/api/v1/admin/email/logs").then(r => r.json()).then(d => setLogs(d.logs || []));
  }, []);

  const sendEmail = async () => {
    await fetch("/api/v1/admin/email/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(compose),
    });
    setCompose({ to: "", subject: "", body: "" });
    alert("Email sent!");
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-white mb-6">📧 Email Management</h1>
      <div className="flex gap-2 mb-6">
        {(["accounts", "send", "logs"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-lg capitalize ${tab === t ? "bg-emerald-600 text-white" : "bg-gray-800 text-gray-400"}`}>{t}</button>
        ))}
      </div>

      {tab === "accounts" && (
        <div className="bg-gray-900 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Managed Accounts</h2>
          {accounts.map(a => (
            <div key={a.email} className="flex justify-between items-center bg-gray-800 p-4 rounded-lg mb-2">
              <div>
                <p className="text-white font-medium">{a.email}</p>
                <p className="text-gray-400 text-sm">{a.provider}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm ${a.status === "active" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>{a.status}</span>
            </div>
          ))}
          {accounts.length === 0 && <p className="text-gray-500">No accounts configured</p>}
        </div>
      )}

      {tab === "send" && (
        <div className="bg-gray-900 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Compose</h2>
          <input className="w-full bg-gray-800 text-white p-3 rounded-lg mb-3" placeholder="To" value={compose.to} onChange={e => setCompose({ ...compose, to: e.target.value })} />
          <input className="w-full bg-gray-800 text-white p-3 rounded-lg mb-3" placeholder="Subject" value={compose.subject} onChange={e => setCompose({ ...compose, subject: e.target.value })} />
          <textarea className="w-full bg-gray-800 text-white p-3 rounded-lg mb-3" rows={6} placeholder="Message body..." value={compose.body} onChange={e => setCompose({ ...compose, body: e.target.value })} />
          <button onClick={sendEmail} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg">Send</button>
        </div>
      )}

      {tab === "logs" && (
        <div className="bg-gray-900 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Logs</h2>
          <div className="space-y-2">
            {logs.map(l => (
              <div key={l.id} className="flex justify-between items-center bg-gray-800 p-3 rounded">
                <div>
                  <p className="text-white text-sm">{l.subject}</p>
                  <p className="text-gray-500 text-xs">To: {l.to}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${l.status === "sent" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>{l.status}</span>
              </div>
            ))}
            {logs.length === 0 && <p className="text-gray-500">No logs yet</p>}
          </div>
        </div>
      )}
    </div>
  );
}

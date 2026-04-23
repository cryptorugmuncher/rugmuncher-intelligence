/**
 * Rug Munch Intelligence — Hero Chat Component
 * The crown jewel of the RMI frontend.
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import {
  Brain,
  Send,
  Sparkles,
  Zap,
  Shield,
  Lock,
  ChevronRight,
  X,
  Loader2,
  MessageSquare,
  TrendingUp,
  Search,
  Eye,
  AlertTriangle,
  BarChart3,
  Coins,
  Flame,
  Check,
} from 'lucide-react';
import { api } from '../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  formatted?: {
    text: string;
    structured?: any;
    risk_score?: number;
  };
}

interface Session {
  session_id: string;
  messages_used: number;
  messages_remaining: number;
  created_at: string;
}

const SUGGESTED_PROMPTS = [
  { icon: Shield, label: 'Scan a token', text: 'Analyze the security of token 0x... on Base' },
  { icon: Eye, label: 'Wallet forensics', text: 'Trace the funding sources of wallet 0x...' },
  { icon: TrendingUp, label: 'Whale watch', text: 'Show me recent whale activity for $CRM' },
  { icon: AlertTriangle, label: 'Rug check', text: 'Is this token a rug pull? Contract: ...' },
  { icon: BarChart3, label: 'Holder analysis', text: 'Analyze holder concentration for token ...' },
  { icon: Coins, label: 'Smart money', text: 'What are smart money wallets buying right now?' },
];

const WELCOME_MESSAGE = `Welcome to the RMI Terminal.

I process on-chain data in real-time. Ask about tokens, wallets, whales, or market patterns — and I'll surface what the noise hides.

Type a contract address, wallet, or question to begin.`;

export default function RugMunchIntelligence() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: WELCOME_MESSAGE,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [showPaywall, setShowPaywall] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<(() => void) | null>(null);

  // Init session
  useEffect(() => {
    const sid = localStorage.getItem('rmi_intel_session');
    api.initChatSession(sid || undefined).then((s) => {
      setSession(s);
      localStorage.setItem('rmi_intel_session', s.session_id);
    });
  }, []);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    const el = inputRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleSend = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;
      if (!session || session.messages_remaining <= 0) {
        setShowPaywall(true);
        return;
      }

      const userMsg: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput('');
      setIsLoading(true);
      setHasStarted(true);

      const assistantId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: 'assistant', content: '', timestamp: new Date(), isStreaming: true },
      ]);

      let fullText = '';

      abortRef.current = api.streamChatMessage(
        text.trim(),
        session.session_id,
        (token) => {
          fullText += token;
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content: fullText } : m))
          );
        },
        (sess) => {
          setSession(sess);
        },
        (full, formatted) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: full, isStreaming: false, formatted } : m
            )
          );
          setIsLoading(false);
        },
        () => {
          setShowPaywall(true);
          setIsLoading(false);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: '🔒 Free tier exhausted.', isStreaming: false }
                : m
            )
          );
        }
      );
    },
    [session, isLoading]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome-' + Date.now(),
        role: 'assistant',
        content: WELCOME_MESSAGE,
        timestamp: new Date(),
      },
    ]);
    setHasStarted(false);
  };

  return (
    <div className="flex flex-col h-full w-full bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/60 backdrop-blur-sm bg-slate-950/50">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-400 border-2 border-slate-950 animate-pulse" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 tracking-tight">
              Rug Munch Intelligence
            </h2>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <Zap className="w-3 h-3 text-amber-400" />
              RMI AI Terminal
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Free tier indicator */}
          {session && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs font-medium text-slate-300">
                {session.messages_remaining} free
              </span>
              <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all"
                  style={{
                    width: `${(session.messages_remaining / 5) * 100}%`,
                  }}
                />
              </div>
            </div>
          )}

          {hasStarted && (
            <button
              onClick={clearChat}
              className="p-2 rounded-lg hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 transition-colors"
              title="New conversation"
            >
              <MessageSquare className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/30 flex items-center justify-center mt-1">
                <Brain className="w-4 h-4 text-emerald-400" />
              </div>
            )}

            <div
              className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3.5 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-emerald-600 to-teal-700 text-white shadow-lg shadow-emerald-900/20'
                  : 'bg-slate-800/60 border border-slate-700/40 text-slate-200 backdrop-blur-sm'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {msg.content}
                {msg.isStreaming && (
                  <span className="inline-block w-1.5 h-4 ml-1 bg-emerald-400 animate-pulse rounded-sm" />
                )}
              </div>

              {/* Risk Score Badge */}
              {msg.formatted?.risk_score !== undefined && !msg.isStreaming && (
                <div className="mt-3 pt-3 border-t border-slate-700/40">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
                      Risk Score
                    </span>
                    <span className={`text-xs font-bold ${
                      msg.formatted.risk_score <= 30 ? 'text-emerald-400' :
                      msg.formatted.risk_score <= 70 ? 'text-amber-400' : 'text-rose-400'
                    }`}>
                      {msg.formatted.risk_score}/100
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        msg.formatted.risk_score <= 30 ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' :
                        msg.formatted.risk_score <= 70 ? 'bg-gradient-to-r from-amber-500 to-amber-400' :
                        'bg-gradient-to-r from-rose-500 to-rose-400'
                      }`}
                      style={{ width: `${msg.formatted.risk_score}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Structured Data Card */}
              {msg.formatted?.structured && !msg.isStreaming && (
                <div className="mt-3 pt-3 border-t border-slate-700/40">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-2">
                    Intelligence Data
                  </div>
                  <div className="bg-slate-900/60 rounded-lg border border-slate-700/30 p-3 overflow-x-auto">
                    <pre className="text-[11px] text-emerald-300 font-mono leading-relaxed">
                      {JSON.stringify(msg.formatted.structured, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-slate-700/50 border border-slate-600/30 flex items-center justify-center mt-1">
                <span className="text-xs font-bold text-slate-300">You</span>
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator when loading but no streaming message yet */}
        {isLoading && !messages.some((m) => m.isStreaming) && (
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/30 flex items-center justify-center">
              <Brain className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="bg-slate-800/60 border border-slate-700/40 rounded-2xl px-5 py-4 flex items-center gap-2">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="text-xs text-slate-500 ml-2">Analyzing chain data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested prompts (only before first message) */}
      {!hasStarted && (
        <div className="px-6 pb-4">
          <p className="text-xs text-slate-500 mb-3 flex items-center gap-1.5">
            <Flame className="w-3 h-3 text-amber-500" />
            Popular inquiries
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {SUGGESTED_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt.text)}
                className="flex items-center gap-2.5 px-4 py-3 rounded-xl bg-slate-800/40 border border-slate-700/30 hover:border-emerald-500/40 hover:bg-slate-800/60 transition-all group text-left"
              >
                <prompt.icon className="w-4 h-4 text-slate-400 group-hover:text-emerald-400 transition-colors flex-shrink-0" />
                <span className="text-xs text-slate-300 group-hover:text-slate-100 truncate">
                  {prompt.label}
                </span>
                <ChevronRight className="w-3 h-3 text-slate-600 group-hover:text-emerald-400 ml-auto flex-shrink-0 opacity-0 group-hover:opacity-100 transition-all" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4 pt-2">
        <form
          onSubmit={handleSubmit}
          className="relative flex items-end gap-2 bg-slate-800/60 border border-slate-700/50 rounded-2xl p-2 backdrop-blur-sm focus-within:border-emerald-500/50 focus-within:shadow-lg focus-within:shadow-emerald-500/5 transition-all"
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              session?.messages_remaining === 0
                ? 'Upgrade to continue...'
                : 'Ask the Terminal about tokens, wallets, or market intelligence...'
            }
            disabled={isLoading || session?.messages_remaining === 0}
            rows={1}
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 resize-none px-3 py-2.5 max-h-[200px] outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || session?.messages_remaining === 0}
            className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 disabled:opacity-40 disabled:shadow-none transition-all"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
        <p className="text-[10px] text-slate-600 text-center mt-2">
          RMI Terminal provides security analysis only. Not financial advice.
        </p>
      </div>

      {/* Paywall Modal */}
      {showPaywall && (
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700/50 rounded-2xl p-8 max-w-md w-full shadow-2xl shadow-emerald-500/5">
            <div className="flex items-center justify-between mb-6">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <Lock className="w-6 h-6 text-white" />
              </div>
              <button
                onClick={() => setShowPaywall(false)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <h3 className="text-xl font-bold text-slate-100 mb-2">
              Unlock RMI Pro
            </h3>
            <p className="text-sm text-slate-400 mb-6">
              You've used your free messages. Upgrade for unlimited access to forensic-grade crypto intelligence.
            </p>

            <div className="space-y-3 mb-6">
              {[
                'Unlimited AI conversations',
                'Real-time token forensics',
                'Wallet tracing & clustering',
                'Whale & smart money alerts',
                'Priority response speed',
              ].map((feat, i) => (
                <div key={i} className="flex items-center gap-2.5 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-emerald-400" />
                  {feat}
                </div>
              ))}
            </div>

            <button
              onClick={() => {
                setShowPaywall(false);
                // TODO: Wire to payment flow
                alert('Payment integration coming soon');
              }}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold text-sm hover:shadow-lg hover:shadow-emerald-500/20 transition-all"
            >
              Upgrade Now — $9/mo
            </button>
            <p className="text-xs text-slate-500 text-center mt-3">
              Cancel anytime. Powered by multi-provider AI mesh.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}


/**
 * Advisor Agent
 * =============
 * Persistent AI copilot for the Darkroom Control Center.
 * Always visible, ready to chat, suggest actions, and execute commands.
 */
import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  Bot,
  X,
  Send,
  Sparkles,
  ChevronRight,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  Terminal,
  Target,
  TrendingUp,
  MessageSquare,
} from 'lucide-react';

interface Message {
  role: 'user' | 'advisor';
  content: string;
  actions?: { label: string; action: string; target?: string }[];
  suggestions?: string[];
  timestamp: Date;
}

export default function AdvisorAgent({ adminKey }: { adminKey: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'advisor',
      content: "I'm your Advisor Agent. I can help you scan wallets, manage content, post to Telegram, check system health, or coordinate the AI mesh. What would you like to do?",
      suggestions: ['Show project status', 'Scan a wallet', 'Draft content', 'Post to Telegram'],
      timestamp: new Date(),
    },
  ]);
  const [sessionId] = useState(`adv-${Date.now()}`);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  // Proactive suggestions
  const { data: suggestions } = useQuery({
    queryKey: ['advisor-suggest', adminKey],
    queryFn: () => api.advisorSuggest(adminKey),
    enabled: !!adminKey && isOpen,
    refetchInterval: 30000,
  });

  const chatMutation = useMutation({
    mutationFn: (message: string) => api.advisorChat(adminKey, message, sessionId),
    onSuccess: (data) => {
      const resp = data.response;
      setMessages((prev) => [
        ...prev,
        {
          role: 'advisor',
          content: resp.content,
          actions: resp.actions || [],
          suggestions: resp.suggestions || [],
          timestamp: new Date(),
        },
      ]);
    },
  });

  const actMutation = useMutation({
    mutationFn: ({ action, params }: { action: string; params?: any }) =>
      api.advisorAct(adminKey, action, params, true),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'advisor',
          content: `✅ ${data.message}`,
          timestamp: new Date(),
        },
      ]);
    },
  });

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return;
    const msg = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: msg, timestamp: new Date() }]);
    setInput('');
    chatMutation.mutate(msg);
  };

  const handleSuggestion = (text: string) => {
    setMessages((prev) => [...prev, { role: 'user', content: text, timestamp: new Date() }]);
    chatMutation.mutate(text);
  };

  const handleAction = (action: { label: string; action: string; target?: string }) => {
    if (action.action === 'navigate') {
      // Emit custom event for DarkRoomControl to handle navigation
      window.dispatchEvent(new CustomEvent('advisor-navigate', { detail: action.target }));
      setMessages((prev) => [
        ...prev,
        { role: 'advisor', content: `Navigating to ${action.label}...`, timestamp: new Date() },
      ]);
    } else {
      actMutation.mutate({ action: action.action });
    }
  };

  const proactive = suggestions?.suggestions || [];

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center shadow-2xl shadow-purple-900/50 hover:scale-110 transition-transform group"
        >
          <Bot className="w-7 h-7 text-white" />
          {proactive.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 rounded-full text-[10px] text-white flex items-center justify-center font-bold animate-bounce">
              {proactive.length}
            </span>
          )}
          <div className="absolute right-full mr-3 px-3 py-2 rounded-xl bg-white/10 border border-white/10 text-sm text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none backdrop-blur-sm">
            Advisor Agent
          </div>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[420px] max-w-[calc(100vw-2rem)] h-[600px] max-h-[calc(100vh-4rem)] rounded-2xl bg-[#0a0a0a]/95 border border-white/10 shadow-2xl flex flex-col overflow-hidden backdrop-blur-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-white">Advisor Agent</h4>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs text-gray-400">Online • AI Ready</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Proactive Alerts */}
          {proactive.length > 0 && (
            <div className="px-4 pt-3 space-y-2">
              {proactive.slice(0, 2).map((s: any, i: number) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border text-sm ${
                    s.priority === 'high'
                      ? 'bg-rose-500/10 border-rose-500/20'
                      : s.priority === 'medium'
                      ? 'bg-yellow-500/10 border-yellow-500/20'
                      : 'bg-white/5 border-white/10'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {s.priority === 'high' ? (
                      <AlertTriangle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                    ) : s.priority === 'medium' ? (
                      <Clock className="w-4 h-4 text-yellow-400 mt-0.5 shrink-0" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    )}
                    <div>
                      <p className="text-gray-200 font-medium">{s.title}</p>
                      <p className="text-gray-500 text-xs mt-0.5">{s.description}</p>
                      {s.action && (
                        <button
                          onClick={() => handleAction(s.action)}
                          className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                        >
                          {s.action.label} <ChevronRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'advisor' && (
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-5 h-5 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                        <Sparkles className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-[10px] text-gray-500">Advisor</span>
                    </div>
                  )}
                  <div
                    className={`px-4 py-2.5 rounded-2xl text-sm ${
                      msg.role === 'user'
                        ? 'bg-purple-500/20 text-purple-100 border border-purple-500/20 rounded-br-md'
                        : 'bg-white/[0.05] text-gray-200 border border-white/[0.06] rounded-bl-md'
                    }`}
                  >
                    {msg.content}
                  </div>

                  {/* Action buttons */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {msg.actions.map((action, j) => (
                        <button
                          key={j}
                          onClick={() => handleAction(action)}
                          className="px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-xs hover:bg-cyan-500/20 transition-colors flex items-center gap-1"
                        >
                          <Zap className="w-3 h-3" />
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Suggestion chips */}
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {msg.suggestions.map((s, j) => (
                        <button
                          key={j}
                          onClick={() => handleSuggestion(s)}
                          className="px-3 py-1 rounded-full bg-white/5 text-gray-400 border border-white/10 text-xs hover:bg-white/10 hover:text-white transition-colors"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {chatMutation.isPending && (
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <div className="w-5 h-5 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center animate-pulse">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span>Advisor is thinking...</span>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white/5 bg-white/[0.02]">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask Advisor anything..."
                className="flex-1 bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || chatMutation.isPending}
                className="p-2.5 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-600 text-white hover:opacity-90 transition-opacity disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-3 mt-2 px-1">
              <button onClick={() => handleSuggestion('Show project status')} className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
                <Target className="w-3 h-3" /> Status
              </button>
              <button onClick={() => handleSuggestion('Scan a wallet')} className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> Scan
              </button>
              <button onClick={() => handleSuggestion('Draft content')} className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
                <MessageSquare className="w-3 h-3" /> Content
              </button>
              <button onClick={() => handleSuggestion('Post to Telegram')} className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1">
                <Terminal className="w-3 h-3" /> Post
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

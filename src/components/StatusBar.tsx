/**
 * Bottom Status Bar
 */
import { Zap, Database, Server, Activity } from 'lucide-react';

interface StatusBarProps {
  health: {
    status: string;
    dragonfly: boolean;
    supabase: boolean;
  } | undefined;
}

export default function StatusBar({ health }: StatusBarProps) {
  return (
    <footer className="h-8 bg-[#12121a] border-t border-purple-500/20 flex items-center justify-between px-4 text-xs">
      <div className="flex items-center gap-4">
        {/* Backend Status */}
        <div className="flex items-center gap-1.5">
          <Server size={12} />
          <span className={health?.status === 'healthy' ? 'text-green-400' : 'text-yellow-400'}>
            {health?.status === 'healthy' ? 'Backend: Online' : 'Backend: Connecting...'}
          </span>
        </div>

        {/* Dragonfly Cache */}
        <div className="flex items-center gap-1.5">
          <Zap size={12} className={health?.dragonfly ? 'text-yellow-400' : 'text-gray-500'} />
          <span className={health?.dragonfly ? 'text-green-400' : 'text-gray-500'}>
            Dragonfly: {health?.dragonfly ? 'Connected' : 'Offline'}
          </span>
        </div>

        {/* Supabase */}
        <div className="flex items-center gap-1.5">
          <Database size={12} className={health?.supabase ? 'text-green-400' : 'text-gray-500'} />
          <span className={health?.supabase ? 'text-green-400' : 'text-gray-500'}>
            Supabase: {health?.supabase ? 'Connected' : 'Offline'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-gray-500">
        <div className="flex items-center gap-1.5">
          <Activity size={12} />
          <span>v2.0.0-beta</span>
        </div>
        <span>© 2025 Rug Munch Intel</span>
      </div>
    </footer>
  );
}

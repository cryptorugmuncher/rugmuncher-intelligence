/**
 * Sidebar Navigation with Keyboard Support
 * Features: Up/down/enter navigation, focus management, ARIA accessibility
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { useAppStore } from '../store/appStore';
import {
  LayoutDashboard,
  Search,
  FolderOpen,
  FileText,
  Wallet,
  Settings,
  ChevronLeft,
  ChevronRight,
  Network,
  Terminal,
  CreditCard,
  MessageSquare,
  GraduationCap,
  Globe,
  Shield,
  Database,
  Lock,
  Activity,
  HardDrive,
  RefreshCw,
  Cpu,
  Cloud,
  Code,
  Bot,
  Newspaper,
  Brain,
  Flame,
  Eye,
  Skull,
  Server,
  Users,
  ChevronDown,
  Trophy,
  Gem,
} from 'lucide-react';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number | string }>;
  badge?: string;
  category: 'main' | 'public' | 'admin' | 'ai' | 'security' | 'data' | 'monitoring' | 'tools' | 'payments';
}

const mainMenuItems: MenuItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, category: 'main' },
  { id: 'rundown', label: 'Daily Rundown', icon: Newspaper, category: 'main' },
  { id: 'scanner', label: 'Wallet Scanner', icon: Search, category: 'main' },
  { id: 'token-scan', label: 'Token Scanner', icon: Shield, category: 'main' },
  { id: 'intel-terminal', label: 'Token Intel', icon: Brain, category: 'main' },
  { id: 'meme-radar', label: 'Meme Radar', icon: Flame, category: 'main' },
  { id: 'whale-watch', label: 'Whale Watch', icon: Eye, category: 'main' },
  { id: 'autopsy', label: "Butcher's Block", icon: Skull, category: 'main' },
  { id: 'analytics', label: 'Muncher Maps', icon: Network, category: 'main' },
  { id: 'trenches', label: 'The Trenches', icon: MessageSquare, category: 'main' },
  { id: 'investigations', label: 'Investigations', icon: FolderOpen, category: 'main' },
  { id: 'evidence', label: 'Evidence', icon: FileText, category: 'main' },
  { id: 'rehab', label: 'Rug Pull Rehab', icon: GraduationCap, category: 'main' },
  { id: 'wallets', label: 'My Wallets', icon: Wallet, category: 'main' },
  { id: 'gamification', label: 'Agent Profile', icon: Trophy, category: 'main' },
  { id: 'telegram-dashboard', label: 'Telegram Bot', icon: Bot, category: 'main' },
];

const aiMenuItems: MenuItem[] = [
  { id: 'ai-agents', label: 'AI Agents', icon: Bot, category: 'ai' },
  { id: 'swarm', label: 'Agent Swarm', icon: Users, category: 'ai' },
  { id: 'llm-router', label: 'LLM Router', icon: Cpu, category: 'ai' },
];

const securityMenuItems: MenuItem[] = [
  { id: 'security', label: 'Security Center', icon: Shield, category: 'security' },
  { id: 'threat-intel', label: 'Threat Intel', icon: Eye, category: 'security' },
  { id: 'scam-detector', label: 'Scam Detector', icon: Shield, category: 'security' },
];

const dataMenuItems: MenuItem[] = [
  { id: 'openaleph', label: 'OpenAleph', icon: Database, category: 'data' },
  { id: 'databases', label: 'Databases', icon: Database, category: 'data' },
];

const monitoringMenuItems: MenuItem[] = [
  { id: 'cloudflare', label: 'Cloudflare Monitor', icon: Cloud, category: 'monitoring' },
  { id: 'system-health', label: 'System Health', icon: Activity, category: 'monitoring' },
  { id: 'logs', label: 'Logs & Events', icon: FileText, category: 'monitoring' },
];

const toolsMenuItems: MenuItem[] = [
  { id: 'journalism', label: 'Journalism', icon: Newspaper, category: 'tools' },
  { id: 'bots', label: 'Bot Management', icon: Bot, category: 'tools' },
  { id: 'infrastructure', label: 'Infrastructure', icon: Server, category: 'tools' },
];

const paymentsMenuItems: MenuItem[] = [
  { id: 'payment-hub', label: 'Monetization Hub', icon: Gem, category: 'payments' },
  { id: 'tier-checkout', label: 'Upgrade Tier', icon: CreditCard, category: 'payments' },
  { id: 'rehab-checkout', label: 'Book Rehab', icon: GraduationCap, category: 'payments' },
  { id: 'newsletter-subscribe', label: 'Newsletter', icon: Newspaper, category: 'payments' },
];

const publicMenuItems: MenuItem[] = [
  { id: 'pricing', label: 'Pricing', icon: CreditCard, category: 'public' },
  { id: 'landing', label: 'Website', icon: Globe, category: 'public' },
];

const adminMenuItems: MenuItem[] = [
  { id: 'admin', label: 'Dev Console', icon: Terminal, badge: 'ADMIN', category: 'admin' },
];

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar, currentPage, setCurrentPage, user } = useAppStore();
  const isAdmin = user?.role === 'ADMIN';
  
  const allMenuItems = [
    ...mainMenuItems,
    ...paymentsMenuItems,
    ...aiMenuItems,
    ...securityMenuItems,
    ...dataMenuItems,
    ...monitoringMenuItems,
    ...toolsMenuItems,
    ...(sidebarOpen ? publicMenuItems : []),
    ...(isAdmin && sidebarOpen ? adminMenuItems : []),
  ];
  
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    payments: true,
    ai: true,
    security: true,
    data: true,
    monitoring: true,
    tools: true,
  });
  
  const navRef = useRef<HTMLElement>(null);
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);

  useEffect(() => {
    setFocusedIndex(-1);
  }, [sidebarOpen]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!allMenuItems.length) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex((prev) => {
          const next = prev < allMenuItems.length - 1 ? prev + 1 : prev;
          buttonRefs.current[next]?.focus();
          return next;
        });
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex((prev) => {
          const next = prev > 0 ? prev - 1 : 0;
          buttonRefs.current[next]?.focus();
          return next;
        });
        break;
      case 'Enter':
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < allMenuItems.length) {
          setCurrentPage(allMenuItems[focusedIndex].id);
        }
        break;
      case 'Home':
        event.preventDefault();
        setFocusedIndex(0);
        buttonRefs.current[0]?.focus();
        break;
      case 'End':
        event.preventDefault();
        const lastIndex = allMenuItems.length - 1;
        setFocusedIndex(lastIndex);
        buttonRefs.current[lastIndex]?.focus();
        break;
      case 'Escape':
        if (!sidebarOpen) {
          toggleSidebar();
        }
        break;
    }
  }, [allMenuItems, focusedIndex, setCurrentPage, sidebarOpen, toggleSidebar]);

  useEffect(() => {
    if (sidebarOpen && buttonRefs.current[0]) {
      buttonRefs.current[0]?.focus();
      setFocusedIndex(0);
    }
  }, [sidebarOpen]);

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const renderMenuItem = (item: MenuItem, index: number, totalBefore: number) => {
    const Icon = item.icon;
    const isActive = currentPage === item.id;
    const isFocused = focusedIndex === totalBefore + index;
    const itemIndex = totalBefore + index;

    return (
      <button
        key={item.id}
        ref={(el) => {
          buttonRefs.current[itemIndex] = el;
        }}
        onClick={() => setCurrentPage(item.id)}
        onFocus={() => setFocusedIndex(itemIndex)}
        onKeyDown={handleKeyDown}
        tabIndex={isFocused ? 0 : -1}
        aria-current={isActive ? 'page' : undefined}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
          isActive
            ? 'bg-purple-600/20 text-purple-300 border-l-2 border-purple-500'
            : isFocused
            ? 'bg-white/10 text-white ring-2 ring-purple-500/50'
            : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
        } ${sidebarOpen ? '' : 'justify-center'}`}
      >
        <Icon size={20} />
        {sidebarOpen && (
          <span className="text-sm font-medium flex items-center gap-2">
            {item.label}
            {item.badge && (
              <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 text-[10px] rounded">
                {item.badge}
              </span>
            )}
          </span>
        )}
      </button>
    );
  };

  const renderSection = (
    title: string,
    items: MenuItem[],
    sectionKey: string,
    startIndex: number
  ) => {
    if (!sidebarOpen) return null;
    
    const isExpanded = expandedSections[sectionKey];
    
    return (
      <div className="mt-4" key={sectionKey}>
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide hover:text-gray-300 transition-colors"
        >
          <span>{title}</span>
          <ChevronDown
            size={14}
            className={`transition-transform duration-200 ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </button>
        {isExpanded && (
          <div className="mt-1 space-y-1">
            {items.map((item, idx) => renderMenuItem(item, idx, startIndex))}
          </div>
        )}
      </div>
    );
  };

  let itemCounter = 0;

  return (
    <aside
      ref={navRef}
      role="navigation"
      aria-label="Main navigation"
      className={`fixed left-0 top-0 h-full bg-[#12121a] border-r border-purple-500/20 z-50 transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-16'
      }`}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-purple-500/20">
        {sidebarOpen ? (
          <>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">RMI</span>
              </div>
              <span className="font-semibold text-white">Rug Munch</span>
            </div>
            <button
              onClick={toggleSidebar}
              className="p-1 rounded hover:bg-white/10 text-gray-400"
              aria-label="Collapse sidebar"
            >
              <ChevronLeft size={20} />
            </button>
          </>
        ) : (
          <button
            onClick={toggleSidebar}
            className="p-1 rounded hover:bg-white/10 text-gray-400 mx-auto"
            aria-label="Expand sidebar"
          >
            <ChevronRight size={20} />
          </button>
        )}
      </div>

      {/* User Info */}
      {sidebarOpen && user && (
        <div className="px-4 py-3 border-b border-purple-500/10">
          <p className="text-sm text-gray-400">Signed in as</p>
          <p className="text-sm font-medium text-white truncate">
            {user.wallet_address
              ? `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}`
              : user.email}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300">
              {user.tier}
            </span>
            {user.wallet_address && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-300">
                Web3
              </span>
            )}
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="p-2 space-y-1 overflow-y-auto h-[calc(100%-12rem)]">
        {/* Main Items */}
        <div className="space-y-1">
          {mainMenuItems.map((item, idx) => {
            const rendered = renderMenuItem(item, idx, itemCounter);
            itemCounter += 1;
            return rendered;
          })}
        </div>

        {/* Payments Section */}
        {sidebarOpen && (
          <>
            {renderSection('Payments', paymentsMenuItems, 'payments', itemCounter)}
            {itemCounter += paymentsMenuItems.length}
          </>
        )}

        {/* AI Section */}
        {sidebarOpen && (
          <>
            {renderSection('AI & Agents', aiMenuItems, 'ai', itemCounter)}
            {itemCounter += aiMenuItems.length}
            
            {renderSection('Security', securityMenuItems, 'security', itemCounter)}
            {itemCounter += securityMenuItems.length}
            
            {renderSection('Data & Analytics', dataMenuItems, 'data', itemCounter)}
            {itemCounter += dataMenuItems.length}
            
            {renderSection('Monitoring', monitoringMenuItems, 'monitoring', itemCounter)}
            {itemCounter += monitoringMenuItems.length}
            
            {renderSection('Tools', toolsMenuItems, 'tools', itemCounter)}
            {itemCounter += toolsMenuItems.length}
          </>
        )}

        {/* Public Links */}
        {sidebarOpen && (
          <div className="mt-4 pt-4 border-t border-gray-800">
            <p className="px-3 text-xs text-gray-500 mb-2 font-semibold tracking-wide uppercase">
              Resources
            </p>
            {publicMenuItems.map((item, idx) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              const itemIdx = itemCounter + idx;
              
              return (
                <button
                  key={item.id}
                  ref={(el) => {
                    buttonRefs.current[itemIdx] = el;
                  }}
                  onClick={() => setCurrentPage(item.id)}
                  onFocus={() => setFocusedIndex(itemIdx)}
                  onKeyDown={handleKeyDown}
                  tabIndex={focusedIndex === itemIdx ? 0 : -1}
                  aria-current={isActive ? 'page' : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-green-600/20 text-green-300 border-l-2 border-green-500'
                      : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                  }`}
                >
                  <Icon size={20} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
            {(() => { itemCounter += publicMenuItems.length; return null; })()}
          </div>
        )}

        {/* Admin Section */}
        {isAdmin && sidebarOpen && (
          <div className="mt-4 pt-4 border-t border-red-500/20">
            <p className="px-3 text-xs text-red-400 mb-2 font-semibold tracking-wide">
              DEVELOPER
            </p>
            {adminMenuItems.map((item, idx) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              const itemIdx = itemCounter + publicMenuItems.length + idx;
              
              return (
                <button
                  key={item.id}
                  ref={(el) => {
                    buttonRefs.current[itemIdx] = el;
                  }}
                  onClick={() => setCurrentPage(item.id)}
                  onFocus={() => setFocusedIndex(itemIdx)}
                  onKeyDown={handleKeyDown}
                  tabIndex={focusedIndex === itemIdx ? 0 : -1}
                  aria-current={isActive ? 'page' : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-red-600/20 text-red-300 border-l-2 border-red-500'
                      : 'text-red-400/70 hover:bg-red-500/10 hover:text-red-300'
                  } ${sidebarOpen ? '' : 'justify-center'}`}
                >
                  <Icon size={20} />
                  {sidebarOpen && (
                    <span className="text-sm font-medium flex items-center gap-2">
                      {item.label}
                      <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 text-[10px] rounded">
                        {item.badge}
                      </span>
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* Settings */}
        <div className="mt-4 pt-4 border-t border-gray-800">
          {renderMenuItem(
            { id: 'settings', label: 'Settings', icon: Settings, category: 'main' },
            0,
            itemCounter + publicMenuItems.length + adminMenuItems.length
          )}
        </div>
      </nav>

      {/* Bottom Section */}
      {sidebarOpen && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-purple-500/20">
          <div className="bg-gradient-to-r from-purple-600/10 to-blue-600/10 rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-1">API Status</p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs text-green-400">Operational</span>
            </div>
          </div>
          
          {/* Keyboard navigation hint */}
          <div className="mt-2 text-[10px] text-gray-500 text-center">
            ↑↓ Navigate • Enter Select
          </div>
        </div>
      )}
    </aside>
  );
}

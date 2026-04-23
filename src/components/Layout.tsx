/**
 * Main Layout Component
 */
import { useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { useHealthCheck } from '../hooks/useBackend';
import Sidebar from './Sidebar';
import Header from './Header';
import StatusBar from './StatusBar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const setBackendStatus = useAppStore((state) => state.setBackendStatus);
  const error = useAppStore((state) => state.error);
  const clearError = useAppStore((state) => state.clearError);

  const { data: health, isError } = useHealthCheck();

  useEffect(() => {
    if (health) {
      setBackendStatus('connected');
    } else if (isError) {
      setBackendStatus('disconnected');
    }
  }, [health, isError, setBackendStatus]);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <Header />

        {/* Error Banner */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 mx-4 mt-4 rounded-lg flex items-center justify-between">
            <span>{error}</span>
            <button onClick={clearError} className="text-red-300 hover:text-red-100">
              ✕
            </button>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>

        {/* Status Bar */}
        <StatusBar health={health} />
      </div>
    </div>
  );
}

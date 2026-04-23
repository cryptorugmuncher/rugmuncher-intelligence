/**
 * WebSocket Hook for Real-Time Updates
 * =====================================
 * Manages WebSocket connection, subscriptions, and message handling.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAppStore } from '../store/appStore';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onConnect,
    onDisconnect,
    onMessage,
    onError,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [subscribedChannels, setSubscribedChannels] = useState<Set<string>>(new Set());
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const token = useAppStore((state) => state.authToken) || localStorage.getItem('access_token');

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    if (isConnecting) {
      return;
    }

    setIsConnecting(true);

    // Build URL with auth token
    const url = token ? `${WS_BASE_URL}?token=${token}` : WS_BASE_URL;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0;
        onConnect?.();

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          ws.send(JSON.stringify({ action: 'ping' }));
        }, 30000);

        // Resubscribe to previous channels
        subscribedChannels.forEach(channel => {
          ws.send(JSON.stringify({ action: 'subscribe', channel }));
        });
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setIsConnecting(false);
        onDisconnect?.();

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval * Math.min(reconnectAttemptsRef.current, 5)); // Exponential backoff
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setIsConnecting(false);
    }
  }, [token, isConnecting, onConnect, onDisconnect, onMessage, onError, reconnectInterval, maxReconnectAttempts, subscribedChannels]);

  // Disconnect
  const disconnect = useCallback(() => {
    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Clear heartbeat
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    // Close connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  // Subscribe to channel
  const subscribe = useCallback((channel: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', channel }));
    }

    setSubscribedChannels(prev => new Set([...prev, channel]));
  }, []);

  // Unsubscribe from channel
  const unsubscribe = useCallback((channel: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe', channel }));
    }

    setSubscribedChannels(prev => {
      const next = new Set(prev);
      next.delete(channel);
      return next;
    });
  }, []);

  // Send message
  const sendMessage = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    lastMessage,
    subscribedChannels: Array.from(subscribedChannels),
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    sendMessage
  };
}

// Specialized hook for alerts
export function useAlerts() {
  const [alerts, setAlerts] = useState<any[]>([]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'alert') {
      setAlerts(prev => [message.data, ...prev].slice(0, 100)); // Keep last 100
    }
  }, []);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    onMessage: handleMessage
  });

  useEffect(() => {
    if (isConnected) {
      subscribe('alerts');
      subscribe('whale_alerts');
      subscribe('scam_alerts');
    }

    return () => {
      unsubscribe('alerts');
      unsubscribe('whale_alerts');
      unsubscribe('scam_alerts');
    };
  }, [isConnected, subscribe, unsubscribe]);

  return { alerts, isConnected };
}

// Specialized hook for Muncher Map real-time updates
export function useMuncherMapRealtime(graphId: string | null) {
  const [updates, setUpdates] = useState<any[]>([]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'graph_update' && message.graph_id === graphId) {
      setUpdates(prev => [...prev, message]);
    }
  }, [graphId]);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    onMessage: handleMessage
  });

  useEffect(() => {
    if (isConnected && graphId) {
      subscribe('network_graph_updates');
    }

    return () => {
      unsubscribe('network_graph_updates');
    };
  }, [isConnected, graphId, subscribe, unsubscribe]);

  return { updates, isConnected, clearUpdates: () => setUpdates([]) };
}

// Hook for price updates
export function usePriceUpdates(tokens: string[]) {
  const [prices, setPrices] = useState<Record<string, { price: number; change24h: number }>>({});

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'price_update') {
      setPrices(prev => ({
        ...prev,
        [message.token]: {
          price: message.price,
          change24h: message.change_24h
        }
      }));
    }
  }, []);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    onMessage: handleMessage
  });

  useEffect(() => {
    if (isConnected && tokens.length > 0) {
      subscribe('price_updates');
    }

    return () => {
      unsubscribe('price_updates');
    };
  }, [isConnected, tokens, subscribe, unsubscribe]);

  return { prices, isConnected };
}

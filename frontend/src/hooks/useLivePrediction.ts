import { useState, useEffect, useRef, useCallback } from 'react';
import { PredictionResponse } from '../types';

export type ConnectionStatus = 'CONNECTING' | 'LIVE' | 'STALE' | 'DISCONNECTED';
export type StreamMode = 'fast_demo' | 'live_market';

interface UseLivePredictionReturn {
  livePrediction: PredictionResponse | null;
  connectionStatus: ConnectionStatus;
  lastUpdatedSecondsAgo: number;
  streamMode: StreamMode;
  setStreamMode: (mode: StreamMode) => void;
  priceDelta: number;
  priceDeltaPct: number;
  lastTickTimestamp: string | null;
  reconnect: () => void;
}

export function useLivePrediction(
  symbol: string,
  initialPrediction: PredictionResponse | null = null,
  enabled: boolean = true
): UseLivePredictionReturn {
  const [livePrediction, setLivePrediction] = useState<PredictionResponse | null>(initialPrediction);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('CONNECTING');
  const [lastUpdatedSecondsAgo, setLastUpdatedSecondsAgo] = useState<number>(0);
  const [streamMode, setStreamModeState] = useState<StreamMode>('fast_demo');
  const [priceDelta, setPriceDelta] = useState<number>(0);
  const [priceDeltaPct, setPriceDeltaPct] = useState<number>(0);
  const [lastTickTimestamp, setLastTickTimestamp] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastReceivedTimeRef = useRef<number>(Date.now());
  const retryAttemptRef = useRef<number>(0);

  // Update initial prediction state if symbol changes
  useEffect(() => {
    if (initialPrediction) {
      setLivePrediction(initialPrediction);
    }
  }, [symbol, initialPrediction]);

  // Second-by-second "updated Xs ago" counter & staleness detector
  useEffect(() => {
    const interval = setInterval(() => {
      const elapsedSec = Math.floor((Date.now() - lastReceivedTimeRef.current) / 1000);
      setLastUpdatedSecondsAgo(elapsedSec);

      if (elapsedSec > 35 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        setConnectionStatus('STALE');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const connectWebSocket = useCallback(() => {
    if (!enabled || !symbol) return;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionStatus('CONNECTING');

    // Build WS URL
    const isHttps = window.location.protocol === 'https:';
    const wsProto = isHttps ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? `${window.location.hostname}:8000`
      : window.location.host;

    const wsUrl = `${wsProto}//${wsHost}/api/v1/ws/live/${symbol.toUpperCase()}?mode=${streamMode}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus('LIVE');
        lastReceivedTimeRef.current = Date.now();
        setLastUpdatedSecondsAgo(0);
        retryAttemptRef.current = 0; // Reset exponential backoff on successful connection
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'PONG') return;

          if (data.type === 'PREDICTION_UPDATE' || data.type === 'INITIAL_SNAPSHOT') {
            setLivePrediction(data as PredictionResponse);
            setConnectionStatus('LIVE');
            lastReceivedTimeRef.current = Date.now();
            setLastUpdatedSecondsAgo(0);
            setLastTickTimestamp(new Date().toLocaleTimeString());

            if (typeof data.price_change === 'number') {
              setPriceDelta(data.price_change);
              setPriceDeltaPct(data.price_change_pct || 0);
            }
          }
        } catch (e) {
          console.error('Error parsing live WebSocket message:', e);
        }
      };

      ws.onerror = (err) => {
        console.warn(`WebSocket error for ${symbol}:`, err);
        setConnectionStatus('DISCONNECTED');
      };

      ws.onclose = () => {
        setConnectionStatus('DISCONNECTED');
        // Exponential backoff reconnect: 1s, 2s, 4s, 8s, 16s, max 30s
        const attempt = retryAttemptRef.current;
        const delayMs = Math.min(1000 * Math.pow(2, attempt), 30000);
        retryAttemptRef.current = attempt + 1;

        if (enabled) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delayMs);
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setConnectionStatus('DISCONNECTED');
    }
  }, [symbol, enabled, streamMode]);

  useEffect(() => {
    connectWebSocket();

    // Heartbeat PING every 20 seconds
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ action: 'PING' }));
        } catch (e) {
          // ignore
        }
      }
    }, 20000);

    return () => {
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connectWebSocket]);

  const setStreamMode = (mode: StreamMode) => {
    setStreamModeState(mode);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'SET_MODE', mode }));
    }
  };

  const reconnect = () => {
    connectWebSocket();
  };

  return {
    livePrediction,
    connectionStatus,
    lastUpdatedSecondsAgo,
    streamMode,
    setStreamMode,
    priceDelta,
    priceDeltaPct,
    lastTickTimestamp,
    reconnect,
  };
}

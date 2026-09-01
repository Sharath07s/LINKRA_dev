"use client";
import React, { createContext, useContext, useEffect, useState, useRef } from "react";
import { useAuthStore } from "@/store/authStore";

interface KCIAEvent {
  event_id: string;
  event_type: string;
  source: string;
  timestamp: number;
  payload: any;
}

interface RealtimeContextProps {
  events: KCIAEvent[];
  lastEvent: KCIAEvent | null;
  isConnected: boolean;
  channel: string;
}

const RealtimeContext = createContext<RealtimeContextProps>({
  events: [],
  lastEvent: null,
  isConnected: false,
  channel: ""
});

export const RealtimeProvider = ({ children, channel }: { children: React.ReactNode, channel: string }) => {
  const [events, setEvents] = useState<KCIAEvent[]>([]);
  const [lastEvent, setLastEvent] = useState<KCIAEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const connect = () => {
      if (ws.current?.readyState === WebSocket.OPEN) return;
      
      // In production, use wss:// and handle dynamic hosts
      const token = useAuthStore.getState().token;
      const wsUrl = `ws://localhost:8000/api/v1/realtime/ws/${channel}${token ? `?token=${token}` : ''}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        console.log(`[Realtime] Connected to ${channel}`);
        if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      };

      ws.current.onmessage = (event) => {
        try {
          const data: KCIAEvent = JSON.parse(event.data);
          setLastEvent(data);
          setEvents(prev => [data, ...prev].slice(0, 50)); // Keep last 50
          
          // Dispatch global window event for components that prefer direct listeners
          window.dispatchEvent(new CustomEvent('kcia-realtime-event', { detail: data }));
        } catch (err) {
          console.warn("Failed to parse websocket message", err);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log(`[Realtime] Disconnected from ${channel}. Reconnecting...`);
        reconnectTimeout.current = setTimeout(connect, 3000);
      };
      
      ws.current.onerror = (err) => {
        console.warn(`[Realtime] WebSocket error on ${channel}:`, err);
        ws.current?.close();
      };
    };

    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (ws.current) {
        ws.current.onclose = null; // Prevent reconnect loop on unmount
        ws.current.close();
      }
    };
  }, [channel]);

  return (
    <RealtimeContext.Provider value={{ events, lastEvent, isConnected, channel }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => useContext(RealtimeContext);

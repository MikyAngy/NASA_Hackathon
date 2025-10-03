import { useState, useEffect, useRef } from 'react';

// Definimos el tipo de retorno del hook para mayor claridad
interface WebSocketHook {
  lastMessage: MessageEvent | null;
  sendMessage: (data: string) => void;
  readyState: number;
}

export const useWebSocket = (url: string): WebSocketHook => {
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!url) return;

    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      console.log('WebSocket Connected');
      setReadyState(WebSocket.OPEN);
    };

    socket.onmessage = (event: MessageEvent) => {
      setLastMessage(event);
    };

    socket.onclose = () => {
      console.log('WebSocket Disconnected');
      // Cuando la conexión se cierra, podemos considerar que "terminó de cargar"
      // Podrías manejar el estado de 'isLoading' aquí si lo necesitaras
      setReadyState(WebSocket.CLOSED);
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    return () => {
      socket.close();
    };
  }, [url]);

  const sendMessage = (data: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(data);
    }
  };

  return { lastMessage, sendMessage, readyState };
};
import { useState, useEffect, useRef, useCallback } from "react";

const WEBSOCKET_URL = `ws://${window.location.host}/ws`;

export function useTranslationWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const webSocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WEBSOCKET_URL);
    webSocketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
      setLastMessage("Connected. Hold button to record.");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("WebSocket message received:", message);
      if (message.translated_text) {
        setLastMessage(message.translated_text);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setLastMessage("Connection Error.");
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
      setLastMessage("Disconnected.");
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendData = useCallback((data: Blob | ArrayBuffer) => {
    if (webSocketRef.current?.readyState === WebSocket.OPEN) {
      webSocketRef.current.send(data);
    } else {
      console.error("WebSocket is not connected. Cannot send data.");
    }
  }, []);

  return { isConnected, lastMessage, sendData };
}

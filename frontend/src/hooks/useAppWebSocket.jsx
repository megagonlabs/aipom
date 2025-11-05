import useWebSocket from "react-use-websocket";

import config from "../config";

export const useAppWebSocket = (sessionId) => {
  // Convert HTTP URL to WebSocket URL
  const wsUrl = config.backendBaseUrl
    ? config.backendBaseUrl.replace("http", "ws")
    : window.location.origin.replace("http", "ws");

  const socketUrl = sessionId ? `${wsUrl}/ws/${sessionId}` : null;

  return useWebSocket(socketUrl, {
    shouldReconnect: () => true,
    reconnectAttempts: 10,
  });
};

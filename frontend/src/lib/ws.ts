/** WebSocket connection manager with reconnect backoff. */
type MessageHandler = (topic: string, type: string, payload: any) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private topics: string[];
  private handlers: MessageHandler[] = [];
  private reconnectAttempt = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private connected = false;

  constructor(topics: string[] = ["incidents", "health", "sos", "events"]) {
    const base = process.env.NEXT_PUBLIC_API_URL?.replace("http", "ws") || "ws://localhost:8000";
    this.url = `${base}/api/v1/ws?topics=${topics.join(",")}`;
    this.topics = topics;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log("[WS] Connected");
        this.connected = true;
        this.reconnectAttempt = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this.handlers.forEach((h) => h(msg.topic, msg.type, msg.payload));
        } catch (e) {
          console.error("[WS] Parse error", e);
        }
      };

      this.ws.onclose = () => {
        this.connected = false;
        console.log("[WS] Disconnected, reconnecting...");
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.error("[WS] Error", err);
        if (!this.connected) reject(err);
      };
    });
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

    if (this.reconnectAttempt >= this.maxReconnectAttempts) {
      console.error("[WS] Max reconnect attempts reached");
      return;
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempt),
      this.maxReconnectDelay
    );
    this.reconnectAttempt++;

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(console.error);
    }, delay);
  }

  onMessage(handler: MessageHandler) {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.connected = false;
  }

  isConnected() {
    return this.connected;
  }
}

// Singleton instance
let wsInstance: WSClient | null = null;

export function getWSClient(topics?: string[]): WSClient {
  if (!wsInstance) {
    wsInstance = new WSClient(topics);
  }
  return wsInstance;
}
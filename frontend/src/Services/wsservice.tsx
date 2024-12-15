class WebSocketService {
    private static instance: WebSocketService;
    private websocket: WebSocket | null = null;
  
    private constructor() {}
  
    public static getInstance(): WebSocketService {
      if (!WebSocketService.instance) {
        WebSocketService.instance = new WebSocketService();
      }
      return WebSocketService.instance;
    }
  
    public connect(url: string): void {
      if (this.websocket) return; // Если WebSocket уже существует, не подключаем повторно
  
      this.websocket = new WebSocket(url);
      this.websocket.onopen = () => console.log("WebSocket соединение установлено");
      this.websocket.onmessage = (event) =>
        console.log("Получено сообщение от WebSocket:", JSON.parse(event.data));
      this.websocket.onerror = (error) =>
        console.error("WebSocket ошибка:", error);
      this.websocket.onclose = () => {
        console.log("WebSocket соединение закрыто");
        this.websocket = null;
      };
    }
  
    public send(message: object): void {
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify(message));
      } else {
        console.error("WebSocket не подключён.");
      }
    }
  
    public close(): void {
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
    }
  
    public getSocket(): WebSocket | null {
      return this.websocket;
    }
  }
  
  export default WebSocketService.getInstance();
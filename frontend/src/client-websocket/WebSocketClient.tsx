export const WebSocketUrl = "ws://localhost:8000/api/v1/machines/ws";

class WebSocketClient {
    private socket: WebSocket;
    private url: string;
    private onMessageCallback: (data: any) => void;
    private shouldReconnect: boolean;

    constructor(url: string, onMessageCallback: (data: any) => void) {
        this.url = url;
        this.onMessageCallback = onMessageCallback;
        this.shouldReconnect = true;
        this.socket = new WebSocket(url);
        this.socket.onmessage = this.handleMessage.bind(this);
        this.socket.onclose = this.handleClose.bind(this);
    }

    private handleMessage(event: MessageEvent) {
        const data = JSON.parse(event.data);
        this.onMessageCallback(data);
    }

    private handleClose() {
        if (this.shouldReconnect) {
            console.log("WebSocket connection closed, reconnecting...");
            setTimeout(() => this.connect(), 1000);
        } else {
            console.log("WebSocket connection closed intentionally.");
        }
    }

    private connect() {
        console.log("WebSocket connection connect.");
        this.socket = new WebSocket(this.url);
        this.socket.onmessage = this.handleMessage.bind(this);
        this.socket.onclose = this.handleClose.bind(this);
    }

    public sendMessage(message: any) {
        this.socket.send(JSON.stringify(message));
    }

    public close() {
        this.shouldReconnect = false;
        this.socket.close();
    }
}

export default WebSocketClient;


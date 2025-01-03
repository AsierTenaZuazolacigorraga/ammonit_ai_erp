import React, { useEffect, useState } from "react";
import WebSocketClient, { WebSocketUrl } from "../../client-websocket/WebSocketClient";

const CounterDisplay: React.FC = () => {
    const [counter, setCounter] = useState<number>(0);

    useEffect(() => {
        console.log("Oppening WebSocket connection");
        const wsClient = new WebSocketClient(WebSocketUrl, (data) => {
            setCounter(data.counter);
        });

        return () => {
            console.log("Closing WebSocket connection");
            wsClient.close();
        };
    }, []);

    return (
        <div>
            <h1>Counter: {counter}</h1>
        </div>
    );
};

export default CounterDisplay;
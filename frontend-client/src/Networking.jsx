export async function chatLogin(username, password) {
    const result = await fetch("/api/chat/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "username": username, "password": password
        })
    });
    
    return result.json();
}

export function createWebSocket(token)
{
    const socket = new WebSocket("ws://localhost:8000/api/chat/ws");

    socket.onopen = () => { // send our auth token to confirm we are connecting
        socket.send(JSON.stringify({"token": token}));
    }

    return socket;
}
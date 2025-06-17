
function generateUUID() {
    return crypto.randomUUID();
}

function createwsconnection() {
    const ws = new WebSocket(`ws://${location.host}/startchat/ws`);

    ws.onopen = () => {
        console.log("Connected!");

        const payload = {
            type: "greeting",
            name: "Mani",
            message: "Hello from client"
        };

        ws.send(JSON.stringify(payload));
    };

    ws.onmessage = (event) => {
        console.log("Message from server:", event.data);
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };
}

document.getElementById('startChatBtn').onclick = async () => {
    const name = document.getElementById('username').value

    try {
        const res = await fetch(`/startchat?name=${encodeURIComponent(name)}&id=dummy`);
        if (!res.ok) throw new Error("Network response was not ok");
        const data = await res.json();
        alert(`Server response: ${data.message}`);
        // Next step: open websocket connection, etc.
        createwsconnection()
    } catch (err) {
        alert("Error: " + err.message);
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerText = 'Loaded (but not connected yet)';
    }
});

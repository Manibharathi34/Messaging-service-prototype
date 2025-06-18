
let ws = null;
let heartbeatInterval = null;

function generateUUID() {
    return crypto.randomUUID();
}

function enableChat() {
    const startSection = document.getElementById("startSection");
    const chatSection = document.getElementById("chatSection");
    const statusSpan = document.getElementById("status");
    statusSpan.textContent = "Connected";
    statusSpan.classList.remove("text-danger");
    statusSpan.classList.add("text-success");

    // Show chat section, hide start section
    startSection.style.display = "none";
    chatSection.style.display = "block";

}

const messageHandlers = {
    search_results: (data) => {
        const users = data.matches || [];
        const userList = document.getElementById("userList");
        userList.innerHTML = "";

        if (users.length === 0) {
            userList.innerHTML = "<li>No matching users found</li>";
            return;
        }

        users.forEach(username => {
            const li = document.createElement("li");
            li.textContent = username;
            li.style.cursor = "pointer";
            li.onclick = () => selectUser(username);
            userList.appendChild(li);
        });
    },

    direct_message: (data) => {
        // handle direct messages here
        // e.g., showMessage(data.from, data.message);
    },

    system: (data) => {
        console.log(data)
    },

};

let selectedUser = null;

function processMessage(data) {
    const handler = messageHandlers[data.type];
    if (handler) {
        handler(data);
    } else {
        console.warn("Unknown message type:", data.type);
    }
}

function selectUser(username) {
    selectedUser = username;
    document.getElementById("chatWith").innerText = username;
    document.getElementById("chatBox").style.display = "block";
    document.getElementById("chatMessages").innerHTML = "";
}



function createwsconnection(data) {

    ws = new WebSocket(`ws://${location.host}/startchat/ws?clientId=${data.id}`);

    ws.onopen = () => {
        sessionStorage.setItem("client_id", data.id)
        enableChat()
        ws.send(JSON.stringify({ type: "register", ...data }));
        // Start heartbeats every 30 seconds
        heartbeatInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "heartbeat" }));
                console.log("Heartbeat sent");
            }
        }, 90000);
    };

    ws.onmessage = (event) => {
        processMessage(event.data)
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
        const res = await fetch(`/startchat?name=${encodeURIComponent(name)}`);
        if (!res.ok) throw new Error("Network response was not ok");
        const data = await res.json();
        createwsconnection(data)
    } catch (err) {
        alert("Error: " + err.message);
    }
};

document.getElementById('searchBtn').onclick = async () => {
    const user = document.getElementById('searchInput').value;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: "search_users",
            client_id: sessionStorage.getItem("client_id"),
            id: user
        }));
    } else {
        console.warn("WebSocket is not open.");
    }

}

document.addEventListener("DOMContentLoaded", function () {
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerText = 'Loaded (but not connected yet)';
    }
});

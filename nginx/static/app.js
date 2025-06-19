
let ws = null;
let heartbeatInterval = null;

function generateUUID() {
    return crypto.randomUUID();
}

const getName = () => sessionStorage.getItem("name");

function enableChat() {
    const startSection = document.getElementById("startSection");
    const chatSection = document.getElementById("chatSection");
    const statusSpan = document.getElementById("status");
    const loginAs = document.getElementById("login-as")
    statusSpan.textContent = "Connected";
    statusSpan.classList.remove("text-danger");
    statusSpan.classList.add("text-success");

    // Show chat section, hide start section
    startSection.style.display = "none";
    chatSection.style.display = "block";
    document.getElementById("login-as").innerHTML = "Logged in as " + getName()

}

function displayUsers(data) {
    const users = data.matches || [];
    const userListBox = document.getElementById('userListBox');
    userListBox.innerHTML = '';

    if (users.length === 0) {
        userListBox.innerHTML = '<p class="text-muted p-3">No users found</p>';
        return;
    }

    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.textContent = user;
        userDiv.className = 'p-3 border-bottom user-row';
        userDiv.style.cursor = 'pointer';
        userDiv.onclick = () => selectUser(user);
        userListBox.appendChild(userDiv);
    });
}

let selectedUser = null;
function selectUser(username) {
    selectedUser = username;
    document.getElementById("chatWith").innerText = username;
    document.getElementById("chatBox").style.display = "block";
    document.getElementById("chatBox").innerHTML = "";
}

const messageHandlers = {
    search_results: (data) => displayUsers(data),

    direct_message: (data) => {
        console.log(data)
        addMessage(data.message, true);
    },

    system: (data) => {
        console.log(data)
    },

};

function processMessage(data) {
    server_msg = JSON.parse(data)
    const handler = messageHandlers[server_msg.type];
    if (handler) {
        handler(server_msg);
    } else {
        console.warn("Unknown message type:", server_msg.type);
    }
}

function addMessage(text, isSentByUser) {
    const chatBox = document.getElementById("chatBox");

    const msgElem = document.createElement("div");
    msgElem.classList.add("message", isSentByUser ? "sent" : "received");
    msgElem.textContent = text;

    chatBox.appendChild(msgElem);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
}



function createwsconnection(data, name) {

    ws = new WebSocket(`ws://${location.host}/startchat/ws?name=${data.id}`);

    ws.onopen = () => {
        sessionStorage.setItem("name", data.id)
        enableChat()
        ws.send(JSON.stringify({ type: "register", name: data.id }));
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

const sendServeMessage = (data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
    } else {
        console.warn("WebSocket is not open.");
    }
}

document.getElementById('startChatBtn').onclick = async () => {
    const name = document.getElementById('username').value

    try {
        const res = await fetch(`/startchat?name=${encodeURIComponent(name)}`);
        if (!res.ok) throw new Error("Network response was not ok");
        const data = await res.json();
        createwsconnection(data, name)
    } catch (err) {
        alert("Error: " + err.message);
    }
};

document.getElementById('searchBtn').onclick = async () => {
    const user = document.getElementById('searchInput').value;
    sendServeMessage({
        type: "search_users",
        name: getName(),
        term: user
    })

}

document.addEventListener("DOMContentLoaded", function () {
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerText = 'Loaded (but not connected yet)';
    }
});

document.getElementById("sendBtn").addEventListener("click", () => {
    const message = document.getElementById("messageInput").value.trim();
    const recipient = selectedUser
    const sender = getName()

    if (!message || !recipient || recipient === "Select a user to chat") {
        alert("Please enter a message and select a user to chat with.");
        return;
    }

    const payload = {
        type: "direct_message",
        to: recipient,
        from: sender,
        text: message,
        timestamp: Date.now()
    };
    ws.send(JSON.stringify(payload));
    addMessage(message, true);
    document.getElementById("messageInput").value = "";
});

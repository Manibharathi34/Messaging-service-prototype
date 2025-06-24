
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
    loginAs.innerHTML = "Logged in as " + getName()

}

function displayUsers(data, unreadSenders = []) {
    const users = data.matches || unreadSenders;
    const userListBox = document.getElementById('userListBox');
    userListBox.innerHTML = '';



    if (users.length === 0) {
        userListBox.innerHTML = '<p class="text-muted p-3">No users found</p>';
        return;
    }


    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.textContent = user;

        userDiv.className = 'p-3 border-bottom user-row d-flex justify-content-between align-items-center';
        userDiv.style.cursor = 'pointer';
        userDiv.onclick = () => selectUser(user);

        if (unreadSenders.includes(user)) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-danger';
            badge.textContent = 'New';
            userDiv.appendChild(badge);
        }

        userListBox.appendChild(userDiv);
    });
}


let selectedUser = null;
function selectUser(username) {
    selectedUser = username;
    chatWith.innerHTML = `Chatting with <span class="text-primary fw-bold">${username}</span>`;
    document.getElementById("chatBox").style.display = "block";
    document.getElementById("chatBox").innerHTML = "";
}

const messageHandlers = {
    search_results: (data) => displayUsers(data),
    direct_message: (data) => processDirectMessage(data),
    unread_messages: (data) => showUnreadMessages(data),
    system: (data) => {
        console.log(data)
    },

};

const processDirectMessage = (data) => {
    const sender = data.from;
    const message = data.message;
    addMessage(`${sender}: ${message}`, false);
    const userList = document.getElementById("userListBox");
    const existingUser = Array.from(userList.children).find(
        li => li.dataset.username === sender
    );
    if (!existingUser) {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.dataset.username = sender;
        li.textContent = sender;
        selectedUser = sender;
        document.getElementById("chatWith").innerHTML = chatWith.innerHTML = `Chatting with <span class="text-primary fw-bold">${sender}</span>`;;
        userList.appendChild(li);
    }
}

const showUnreadMessages = (data) => {
    const messages = data.messages || []
    const senders = new Set();
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML = "";
    messages.forEach((message) => {
        const { sender, text, time } = message;
        senders.add(sender);
        const localTime = new Date(time + " UTC").toLocaleString();
        const msgElement = document.createElement("div");
        msgElement.className = "mb-2";
        msgElement.innerHTML = `<strong>${sender}</strong> <small class="text-muted">[${localTime}]</small>: ${text}`;
        chatBox.appendChild(msgElement);
    })
    displayUsers({}, [...senders]);
}

const updateUserListWithSenders = (senders) => {
    const userList = document.getElementById("userList");
    senders.forEach((sender) => {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-warning";
        li.innerText = `New message from ${sender}`;
        userList.appendChild(li);
    });
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
    chatBox.scrollTop = chatBox.scrollHeight;
}



function createwsconnection(data) {

    ws = new WebSocket(`ws://${location.host}/startchat/ws?name=${getName()}`);

    ws.onopen = () => {
        enableChat()
        ws.send(JSON.stringify({ type: "register", name: getName() }));
        // Start heartbeats every 30 seconds
        heartbeatInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "heartbeat", name: getName() }));
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

    ws.onclose = (event) => {
        if (event.code !== 1000 && event.wasClean === false) {
            console.warn('WebSocket closed abnormally. Reloading page...');
            location.reload();
        } else {
            console.log('WebSocket closed cleanly. Attempting to reconnect (or not, depending on logic).');
            setTimeout(createwsconnection, 60000);
        }
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
        sessionStorage.setItem("name", name)
        createwsconnection()
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

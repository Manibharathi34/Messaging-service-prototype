
function generateUUID() {
    return crypto.randomUUID();
}

document.getElementById('startChatBtn').onclick = async () => {
    const name = prompt("Enter your name:");
    if (!name) {
        alert("Name is required!");
        return;
    }
    const uuid = generateUUID();

    try {
        const res = await fetch(`/startchat?name=${encodeURIComponent(name)}&id=${uuid}`);
        if (!res.ok) throw new Error("Network response was not ok");
        const data = await res.json();
        alert(`Server response: ${data.message}`);
        // Next step: open websocket connection, etc.
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

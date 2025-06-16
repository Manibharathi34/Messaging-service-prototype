document.addEventListener("DOMContentLoaded", function () {
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerText = 'Loaded (but not connected yet)';
    }
});

document.getElementById('saveBtn').addEventListener('click', () => {
    const url = document.getElementById('serverUrl').value;
    chrome.storage.local.set({ serverUrl: url }, () => {
        document.getElementById('status').textContent = 'Settings saved!';
        setTimeout(() => {
            document.getElementById('status').textContent = 'Connected';
        }, 1000);
    });
});

chrome.storage.local.get(['serverUrl'], (result) => {
    if (result.serverUrl) {
        document.getElementById('serverUrl').value = result.serverUrl;
    }
    
    fetch(result.serverUrl || 'http://localhost:8080', { method: 'OPTIONS' })
        .then(() => {
            document.getElementById('status').textContent = 'Connected to server';
        })
        .catch(() => {
            document.getElementById('status').textContent = 'Server not running';
        });
});


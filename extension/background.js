chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message || message.type !== 'forward' || !message.url) {
        return false;
    }

    fetch(message.url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(message.payload)
    }).then(response => {
        sendResponse({ ok: response.ok });
    }).catch(err => {
        sendResponse({ ok: false, error: String(err) });
    });

    return true;
});

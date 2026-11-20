let lastTrack = null;
let serverUrl = 'http://localhost:8080';
let observer = null;
let noTrackCount = 0;
const CLEAR_THRESHOLD = 5;

console.log('[YMD] injected on', location.hostname);


function findTrackInWindow() {
    try {
        if (window.__INITIAL_STATE__) {
            const state = window.__INITIAL_STATE__;
            if (state.track || state.currentTrack || state.player?.track) {
                const track = state.track || state.currentTrack || state.player?.track;
                if (track.title) {
                    return {
                        title: track.title,
                        artist: track.artists?.map(a => a.name || a).join(', ') || 'Unknown Artist',
                        album: track.albums?.[0]?.title || '',
                        cover: track.coverUri ? `https://${track.coverUri.replace('%%', '200x200')}` : null
                    };
                }
            }
        }
        
        if (window.__REDUX_STATE__) {
            const state = window.__REDUX_STATE__;
            if (state.player?.currentTrack) {
                const track = state.player.currentTrack;
                if (track.title) {
                    return {
                        title: track.title,
                        artist: track.artists?.map(a => a.name || a).join(', ') || 'Unknown Artist',
                        album: track.albums?.[0]?.title || '',
                        cover: track.coverUri ? `https://${track.coverUri.replace('%%', '200x200')}` : null
                    };
                }
            }
        }
    } catch (e) {
        console.error('Error reading window state:', e);
    }
    return null;
}

function isVisible(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;
    const style = window.getComputedStyle(el);
    return style.visibility !== 'hidden' && style.display !== 'none';
}

function isPlaying() {
    const audios = Array.from(document.querySelectorAll('audio'));
    if (audios.length === 0) {
        return true;
    }
    return audios.some(a => !a.paused);
}

function getPlayerBar() {
    const selectors = [
        '[class*="PlayerBar"]',
        'footer',
        '[class*="Footer"]',
        '[data-test-id*="player"]',
        '[data-test-id*="Player"]'
    ];
    for (const sel of selectors) {
        for (const el of document.querySelectorAll(sel)) {
            if (isVisible(el) && el.querySelector('a[href*="/track/"]')) {
                return el;
            }
        }
    }

    const trackLinks = document.querySelectorAll('a[href*="/track/"]');
    for (const link of trackLinks) {
        if (!isVisible(link)) continue;
        const bar = link.closest('footer, [class*="PlayerBar"], [class*="player"]');
        if (bar && isVisible(bar) && bar.querySelector('a[href*="/artist/"]')) {
            return bar;
        }
    }
    return null;
}

function getTrackFromPlayerBar(bar) {
    let titleEl = null;
    for (const link of bar.querySelectorAll('a[href*="/track/"]')) {
        if (!isVisible(link)) continue;
        const text = (link.textContent || '').trim();
        const titleAttr = (link.getAttribute('title') || '').trim();
        if (text || titleAttr) {
            titleEl = link;
            break;
        }
    }
    if (!titleEl) return null;

    const title = (titleEl.getAttribute('title') || titleEl.textContent || '').trim();
    if (!title) return null;

    const artists = [];
    for (const el of bar.querySelectorAll('a[href*="/artist/"]')) {
        if (!isVisible(el)) continue;
        const name = (el.getAttribute('title') || el.textContent || '').trim();
        if (name && !artists.includes(name)) {
            artists.push(name);
        }
    }

    let cover = null;
    for (const img of bar.querySelectorAll('img')) {
        const raw = img.currentSrc || img.src || img.getAttribute('srcset') || '';
        if (raw && raw.includes('avatars.yandex.net')) {
            cover = raw.replace(/\/\d+x\d+$/, '/200x200');
            break;
        }
    }

    return {
        title,
        artist: artists.length ? artists.join(', ') : 'Unknown Artist',
        album: '',
        cover
    };
}

function getCurrentTrack() {
    const windowTrack = findTrackInWindow();
    if (windowTrack) {
        return windowTrack;
    }

    try {
        const bar = getPlayerBar();
        if (bar) {
            const track = getTrackFromPlayerBar(bar);
            if (track) {
                return track;
            }
        }
    } catch (e) {
        console.error('[YMD] Error getting track:', e);
    }
    return null;
}

function sendTrackToServer(track) {
    const trackKey = normalizeTrackKey(track);
    if (!trackKey) return;

    // Не отправляем, если это тот же трек, что уже был отправлен
    if (sendTrackToServer.lastSent === trackKey) {
        return; // Трек не изменился, не отправляем на сервер
    }

    // Отмечаем, что этот трек уже отправлен
    sendTrackToServer.lastSent = trackKey;

    chrome.runtime.sendMessage({
        type: 'forward',
        url: serverUrl,
        payload: track
    }, (response) => {
        if (!response || !response.ok) {
            // При ошибке сбрасываем, чтобы можно было повторить
            sendTrackToServer.lastSent = null;
        }
    });
}

function normalizeTrackKey(track) {
    if (!track) return null;
    const title = (track.title || '').trim().toLowerCase();
    const artist = (track.artist || '').trim().toLowerCase();
    return `${title}|${artist}`;
}

function checkTrack() {
    const track = isPlaying() ? getCurrentTrack() : null;
    if (track) {
        noTrackCount = 0;
        const trackKey = normalizeTrackKey(track);
        const lastTrackKey = normalizeTrackKey(lastTrack);

        if (trackKey !== lastTrackKey && trackKey) {
            lastTrack = track;
            console.log('Track:', track.title, '-', track.artist, 'Cover:', track.cover);
            sendTrackToServer(track);
        }
    } else {
        if (lastTrack) {
            noTrackCount++;
            if (noTrackCount >= CLEAR_THRESHOLD) {
                console.log('No track playing');
                lastTrack = null;
                sendTrackToServer.lastSent = null;
                noTrackCount = 0;
                chrome.runtime.sendMessage({
                    type: 'forward',
                    url: serverUrl,
                    payload: { clear: true }
                });
            }
        }
    }
}

chrome.storage.local.get(['serverUrl'], (result) => {
    if (result.serverUrl) {
        serverUrl = result.serverUrl;
    }
});

function startObserver() {
    if (observer) return;

    let checkTimeout = null;
    observer = new MutationObserver(() => {
        // Debounce: проверяем трек не чаще раза в секунду
        if (checkTimeout) {
            clearTimeout(checkTimeout);
        }
        checkTimeout = setTimeout(() => {
            checkTrack();
        }, 1000);
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false
    });

}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        startObserver();
        setInterval(checkTrack, 1000);
        checkTrack();
    });
} else {
    startObserver();
    setInterval(checkTrack, 1000);
    checkTrack();
}

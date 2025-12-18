let lastTrack = null;
let serverUrl = 'http://localhost:8080';
let observer = null;
let noTrackCount = 0;
const CLEAR_THRESHOLD = 5;


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

function isPlayerPlaying() {
    const playPauseButtons = document.querySelectorAll('button, [role="button"]');
    let hasPauseButton = false;
    
    for (const btn of playPauseButtons) {
        const rect = btn.getBoundingClientRect();
        const ariaLabel = btn.getAttribute('aria-label') || '';
        const className = btn.className || '';
        const text = btn.textContent || '';
        
        if (rect.bottom > window.innerHeight - 200 && 
            rect.width > 0 && rect.height > 0 &&
            (ariaLabel.toLowerCase().includes('pause') || 
             className.includes('pause') ||
             className.includes('Pause') ||
             text.includes('⏸') ||
             text.includes('||'))) {
            hasPauseButton = true;
            break;
        }
    }
    
    if (!hasPauseButton) {
        const playerBarCheck = document.querySelector('[class*="PlayerBar"], footer, [class*="Footer"]');
        if (playerBarCheck) {
            const rect = playerBarCheck.getBoundingClientRect();
            if (rect.bottom > window.innerHeight - 100) {
                return true;
            }
        }
    }
    
    return hasPauseButton;
}

function getCurrentTrack() {
    const windowTrack = findTrackInWindow();
    if (windowTrack) {
        return windowTrack;
    }
    
    try {
        const playerBarSelectors = [
            '[class*="PlayerBar"]',
            'footer',
            '[class*="Footer"]'
        ];
        
        let playerBar = null;
        for (const sel of playerBarSelectors) {
            const candidate = document.querySelector(sel);
            if (candidate) {
                const rect = candidate.getBoundingClientRect();
                if (rect.bottom > window.innerHeight - 80 && rect.top < window.innerHeight) {
                    playerBar = candidate;
                    break;
                }
            }
        }
        
        if (!playerBar) {
            return null;
        }
        
        let cover = null;
        const coverImg = document.querySelector('img[class*="PlayerBarDesktopWithBackgroundProgressBar_cover"], img[class*="PlayerBarMobile_cover"]');
        if (coverImg) {
            if (coverImg.src && coverImg.src.includes('avatars.yandex.net')) {
                cover = coverImg.src.replace(/\/\d+x\d+$/, '/200x200');
            } else if (coverImg.srcset) {
                const srcset = coverImg.getAttribute('srcset');
                if (srcset && srcset.includes('avatars.yandex.net')) {
                    const urls = srcset.split(',').map(s => s.trim().split(' ')[0]);
                    cover = urls.find(url => url.includes('200x200')) || urls[0];
                }
            }
        }
        
        const titleSelectors = [
            '[class*="Meta_title"]'
        ];
        
        const artistSelectors = [
            '[class*="Meta_artists"]'
        ];
        
        let titleEl = null;
        let artistEl = null;
        
        for (const sel of titleSelectors) {
            const candidates = playerBar.querySelectorAll(sel);
            for (const candidate of candidates) {
                const text = candidate.textContent.trim();
                const rect = candidate.getBoundingClientRect();
                if (text.length > 0 && 
                    rect.bottom > window.innerHeight - 80 && 
                    rect.top < window.innerHeight &&
                    rect.left < window.innerWidth * 0.6) {
                    titleEl = candidate;
                    break;
                }
            }
            if (titleEl) break;
        }
        
        for (const sel of artistSelectors) {
            const candidates = playerBar.querySelectorAll(sel);
            for (const candidate of candidates) {
                const text = candidate.textContent.trim();
                const rect = candidate.getBoundingClientRect();
                if (text.length > 0 && 
                    rect.bottom > window.innerHeight - 80 && 
                    rect.top < window.innerHeight &&
                    rect.left < window.innerWidth * 0.6) {
                    artistEl = candidate;
                    break;
                }
            }
            if (artistEl) break;
        }
        
        if (titleEl) {
            const title = titleEl.textContent.trim();
            let artist = '';
            
            if (artistEl) {
                artist = artistEl.textContent.trim();
            } else {
                const parent = titleEl.closest('[class*="Meta"], [class*="PlayerBar"]');
                if (parent) {
                    const artistCandidates = parent.querySelectorAll('[class*="Meta_artists"], [class*="artists"]');
                    for (const candidate of artistCandidates) {
                        const text = candidate.textContent.trim();
                        const rect = candidate.getBoundingClientRect();
                        if (text.length > 0 && 
                            text !== title &&
                            rect.bottom > window.innerHeight - 80 &&
                            rect.left < window.innerWidth * 0.6) {
                            artist = text;
                            break;
                        }
                    }
                }
            }
            
            if (title && title.length > 0 && 
                title.length < 100 &&
                !title.toLowerCase().includes('listen') &&
                !title.toLowerCase().includes('favorite') &&
                !title.toLowerCase().includes('mistake') &&
                !title.toLowerCase().includes('1booth') &&
                !title.toLowerCase().includes('player') &&
                !title.toLowerCase().includes('slang') &&
                !title.toLowerCase().includes('улыбка') &&
                !title.toLowerCase().includes('aarne') &&
                title !== lastTrack?.title) {
                return {
                    title,
                    artist: artist || 'Unknown Artist',
                    album: '',
                    cover: cover
                };
            }
        }
    } catch (e) {
        console.error('Error getting track:', e);
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
    
    fetch(serverUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(track)
    }).then(() => {
        // Успешно отправлено
    }).catch(err => {
        console.error('Error sending track:', err);
        // При ошибке сбрасываем, чтобы можно было повторить
        sendTrackToServer.lastSent = null;
    });
}

function normalizeTrackKey(track) {
    if (!track) return null;
    const title = (track.title || '').trim().toLowerCase();
    const artist = (track.artist || '').trim().toLowerCase();
    return `${title}|${artist}`;
}

function checkTrack() {
    const track = getCurrentTrack();
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
                fetch(serverUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ clear: true })
                }).catch(() => {});
            }
        }
    }
    
    if (!track) {
        const player = document.querySelector('[class*="player"], [class*="Player"], [data-bem*="player"]');
        if (player) {
            const allLinks = player.querySelectorAll('a');
            const trackLinks = Array.from(allLinks).filter(a => {
                const href = a.getAttribute('href') || '';
                return href.includes('/track/');
            });
            
            if (trackLinks.length > 0) {
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




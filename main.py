import time
from pypresence import Presence
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class YandexMusicDiscord:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = Presence(client_id)
        self.rpc.connect()
        self.session = requests.Session()
        self.current_track = None
    
    def _get_cookies(self):
        cookie_file = os.path.expanduser('~/.yandex_music_cookies.json')
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r') as f:
                    cookies_dict = json.load(f)
                    return {k: v for k, v in cookies_dict.items()}
            except:
                pass
        return None
    
    def get_current_track(self):
        try:
            cookies = self._get_cookies()
            if not cookies:
                print("Debug: No cookies found")
                return None
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'X-Retpath-Y': 'https://music.yandex.ru',
                'Referer': 'https://music.yandex.ru',
            }
            
            self.session.headers.update(headers)
            self.session.cookies.update(cookies)
            
            endpoints = [
                'https://music.yandex.ru/handlers/track-now-playing.jsx',
                'https://music.yandex.ru/api/v2.1/handlers/track-now-playing',
                'https://music.yandex.ru/handlers/player.jsx',
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=5)
                    print(f"Debug: Trying {endpoint} - status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"Debug: API response data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                            
                            if 'track' in data and data['track']:
                                track = data['track']
                                artists = [a.get('name', '') for a in track.get('artists', [])]
                                cover_uri = track.get('coverUri', '')
                                if cover_uri:
                                    cover = f"https://{cover_uri.replace('%%', '200x200')}"
                                else:
                                    cover = None
                                
                                return {
                                    'title': track.get('title', 'Unknown'),
                                    'artist': ', '.join(artists) if artists else 'Unknown Artist',
                                    'album': track.get('albums', [{}])[0].get('title', '') if track.get('albums') else '',
                                    'cover': cover
                                }
                            elif 'entity' in data and data.get('entity'):
                                entity = data['entity']
                                if 'track' in entity:
                                    track = entity['track']
                                    artists = [a.get('name', '') for a in track.get('artists', [])]
                                    cover_uri = track.get('coverUri', '')
                                    if cover_uri:
                                        cover = f"https://{cover_uri.replace('%%', '200x200')}"
                                    else:
                                        cover = None
                                    
                                    return {
                                        'title': track.get('title', 'Unknown'),
                                        'artist': ', '.join(artists) if artists else 'Unknown Artist',
                                        'album': track.get('albums', [{}])[0].get('title', '') if track.get('albums') else '',
                                        'cover': cover
                                    }
                        except json.JSONDecodeError:
                            continue
                except:
                    continue
            
            print("Debug: All endpoints failed, trying queue API...")
            
            try:
                response = self.session.get('https://music.yandex.ru/api/v2.1/handlers/queue', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'queue' in data and data['queue']:
                        current_track_id = data['queue'].get('currentIndex')
                        tracks = data['queue'].get('tracks', [])
                        if current_track_id is not None and tracks:
                            track_data = tracks[current_track_id] if current_track_id < len(tracks) else None
                            if track_data and 'track' in track_data:
                                track = track_data['track']
                                artists = [a.get('name', '') for a in track.get('artists', [])]
                                cover_uri = track.get('coverUri', '')
                                if cover_uri:
                                    cover = f"https://{cover_uri.replace('%%', '200x200')}"
                                else:
                                    cover = None
                                
                                return {
                                    'title': track.get('title', 'Unknown'),
                                    'artist': ', '.join(artists) if artists else 'Unknown Artist',
                                    'album': track.get('albums', [{}])[0].get('title', '') if track.get('albums') else '',
                                    'cover': cover
                                }
            except:
                pass
            
            print("Debug: All API methods failed")
        except requests.exceptions.RequestException as e:
            print(f"Debug: Request error: {e}")
        except Exception as e:
            print(f"Debug: Error: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    def update_discord_presence(self, track_info):
        if not track_info:
            return
            
        try:
            details = f"{track_info['title']}"
            state = f"by {track_info['artist']}" if track_info['artist'] else ""
            
            presence_data = {
                'details': details,
                'state': state,
                'large_text': track_info.get('album', '') or details,
            }
            
            if track_info.get('cover'):
                presence_data['large_image'] = track_info['cover']
            else:
                presence_data['large_image'] = 'yandex_music'
            
            presence_data['small_image'] = 'yandex_music'
            presence_data['small_text'] = 'Yandex Music'
            
            self.rpc.update(**presence_data)
        except Exception as e:
            print(f"Error updating presence: {e}")
    
    def run(self):
        print("Yandex Music Discord Rich Presence started")
        print("Make sure you're logged into Yandex Music in your browser")
        print("Press Ctrl+C to stop\n")
        
        cookies = self._get_cookies()
        if not cookies:
            print("ERROR: Cookies file not found or empty!")
            print(f"Expected location: {os.path.expanduser('~/.yandex_music_cookies.json')}")
            return
        
        print(f"Debug: Loaded {len(cookies)} cookies")
        print("Debug: Checking for current track...\n")
        
        while True:
            try:
                track_info = self.get_current_track()
                
                if track_info:
                    if track_info != self.current_track:
                        self.current_track = track_info
                        self.update_discord_presence(track_info)
                        print(f"Now playing: {track_info['title']} - {track_info['artist']}")
                else:
                    print("Debug: No track detected (make sure music is playing in browser)")
                
                time.sleep(5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)
        
        self.rpc.close()

if __name__ == '__main__':
    CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
    if not CLIENT_ID:
        print("Error: DISCORD_CLIENT_ID environment variable not set")
        print("Get your Discord Application ID from https://discord.com/developers/applications")
        exit(1)
    
    ymd = YandexMusicDiscord(CLIENT_ID)
    ymd.run()


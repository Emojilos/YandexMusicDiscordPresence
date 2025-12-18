import time
from pypresence import Presence
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import sys

class TrackHandler(BaseHTTPRequestHandler):
    current_track = None
    last_sent_track = None
    track_start_time = None
    rpc = None
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        status = {
            'status': 'ok',
            'connected': TrackHandler.rpc is not None,
            'current_track': TrackHandler.current_track
        }
        self.wfile.write(json.dumps(status).encode('utf-8'))
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
        except:
            return
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            if 'title' in data and data.get('title'):
                title = data.get('title', '').strip()
                artist = data.get('artist', '').strip()
                
                if not title or title.lower() in ['unknown', 'player', '']:
                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b'{"status": "ignored"}')
                    except (BrokenPipeError, OSError):
                        pass
                    return
                
                normalized_title = title.strip().lower()
                normalized_artist = artist.strip().lower()
                track_key = f"{normalized_title}|{normalized_artist}"
                
                last_track_key = None
                if TrackHandler.last_sent_track:
                    last_title = TrackHandler.last_sent_track.get('title', '').strip().lower()
                    last_artist = TrackHandler.last_sent_track.get('artist', '').strip().lower()
                    last_track_key = f"{last_title}|{last_artist}"
                
                current_time = time.time()
                track_changed = track_key != last_track_key
                
                if not track_changed:
                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b'{"status": "same_track"}')
                    except (BrokenPipeError, OSError):
                        pass
                    return
                
                if track_changed:
                    if not TrackHandler.track_start_time:
                        TrackHandler.track_start_time = int(current_time)
                    
                    TrackHandler.last_sent_track = {'title': title, 'artist': artist}
                    
                    if TrackHandler.rpc:
                        try:
                            details = title
                            state = f"by {artist}" if artist else ""
                            
                            presence_data = {
                                'details': details,
                                'state': state,
                                'start': TrackHandler.track_start_time,
                            }
                            
                            cover = data.get('cover')
                            print(f"📦 Received cover: {cover}")
                            if cover:
                                presence_data['large_image'] = cover
                                presence_data['large_text'] = data.get('album', '') or title
                                print(f"🖼️  Sending cover to Discord: {cover}")
                            
                            TrackHandler.rpc.update(**presence_data)
                            print(f"✅ Трек обновлен: {details} - {artist}")
                        except ConnectionRefusedError:
                            print(f"⚠️  Discord отклонил подключение. Проверьте, что Discord запущен.")
                        except Exception as e:
                            print(f"⚠️  Ошибка обновления Discord: {e}")
                            try:
                                if TrackHandler.rpc:
                                    TrackHandler.rpc.close()
                            except:
                                pass
                            try:
                                CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
                                if CLIENT_ID:
                                    TrackHandler.rpc = Presence(CLIENT_ID)
                                    TrackHandler.rpc.connect()
                                    print("✅ Переподключено к Discord")
                            except Exception as reconnect_error:
                                print(f"⚠️  Не удалось переподключиться: {reconnect_error}")
                                TrackHandler.rpc = None
                
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok"}')
                except (BrokenPipeError, OSError):
                    pass
            elif 'clear' in data and data.get('clear'):
                pass
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'{"status": "cleared"}')
                except (BrokenPipeError, OSError):
                    pass
            else:
                try:
                    self.send_response(400)
                    self.end_headers()
                except (BrokenPipeError, OSError):
                    pass
        except Exception as e:
            print(f"⚠️  Ошибка обработки запроса: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "error"}')
            except (BrokenPipeError, OSError):
                pass
            except Exception as send_error:
                print(f"⚠️  Ошибка отправки ответа: {send_error}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server(port=8080):
    server = HTTPServer(('localhost', port), TrackHandler)
    print(f"Server started on http://localhost:{port}")
    server.serve_forever()

if __name__ == '__main__':
    CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
    if not CLIENT_ID:
        print("Error: DISCORD_CLIENT_ID environment variable not set")
        exit(1)
    
    print(f"Discord Client ID: {CLIENT_ID}")
    print("Подключаюсь к Discord...")
    
    try:
        rpc = Presence(CLIENT_ID)
        print("Попытка подключения к Discord RPC...")
        rpc.connect()
        TrackHandler.rpc = rpc
        print("✅ Успешно подключено к Discord!")
        
        # Тестовое обновление для проверки
        try:
            rpc.update(details="Тест подключения", state="Проверка работы")
            print("✅ Тестовое обновление отправлено в Discord")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  Предупреждение при тестовом обновлении: {e}")
    except FileNotFoundError:
        print("❌ Ошибка: Discord не найден!")
        print("   Discord должен быть запущен перед запуском сервера")
        print("   Убедитесь, что используете десктопную версию Discord (не веб-версию)")
        sys.exit(1)
    except ConnectionRefusedError:
        print("❌ Ошибка: Discord отклонил подключение!")
        print("   Возможные причины:")
        print("   1. Discord не запущен")
        print("   2. Discord запущен, но RPC отключен")
        print("   Решение: Перезапустите Discord и попробуйте снова")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка подключения к Discord: {e}")
        print("\nВозможные причины:")
        print("1. Discord не запущен - убедитесь, что Discord открыт")
        print("2. Неправильный Client ID - проверьте DISCORD_CLIENT_ID")
        print("3. Discord не поддерживает RPC - убедитесь, что используете десктопную версию Discord")
        print("\nПопробуйте:")
        print("- Перезапустить Discord")
        print("- Проверить, что Discord запущен (не веб-версия)")
        print("- Убедиться, что Client ID правильный")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("Yandex Music Discord Rich Presence started")
    print("Install browser extension and make sure it's connected")
    print("Press Ctrl+C to stop\n")
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nStopping...")
        if TrackHandler.rpc:
            try:
                TrackHandler.rpc.close()
            except:
                pass


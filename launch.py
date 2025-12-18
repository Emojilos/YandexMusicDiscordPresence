import os
import sys
import subprocess
import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def install_dependencies():
    try:
        import pypresence
        import requests
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️  Устанавливаю зависимости...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Зависимости установлены")
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки зависимостей")
            sys.exit(1)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    client_id = os.getenv('DISCORD_CLIENT_ID')
    if not client_id:
        print("❌ Ошибка: переменная окружения DISCORD_CLIENT_ID не установлена")
        print("")
        print("Установите её:")
        print("")
        print("Windows (PowerShell):")
        print('  $env:DISCORD_CLIENT_ID="ваш_client_id"')
        print("")
        print("Windows (CMD):")
        print('  set DISCORD_CLIENT_ID=ваш_client_id')
        print("")
        print("Linux/macOS:")
        print('  export DISCORD_CLIENT_ID="ваш_client_id"')
        print("")
        print("Или создайте файл .env с содержимым:")
        print('  DISCORD_CLIENT_ID=ваш_client_id')
        sys.exit(1)
    
    if check_port(8080):
        print("⚠️  Сервер уже запущен на порту 8080")
        print("Остановите его перед запуском нового экземпляра")
        sys.exit(1)
    
    install_dependencies()
    
    print("🚀 Запускаю Yandex Music Discord Rich Presence сервер...")
    print("📡 Сервер будет доступен на http://localhost:8080")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("")
    
    try:
        subprocess.run([sys.executable, 'server.py'])
    except KeyboardInterrupt:
        print("\nОстановка...")

if __name__ == '__main__':
    main()


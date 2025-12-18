#!/usr/bin/env python3
"""Тестовый скрипт для проверки подключения к Discord"""

import os
import time
from pypresence import Presence

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
if not CLIENT_ID:
    print("❌ Ошибка: DISCORD_CLIENT_ID не установлен")
    print("Установите: export DISCORD_CLIENT_ID=\"ваш_id\"")
    exit(1)

print(f"Discord Client ID: {CLIENT_ID}")
print("Попытка подключения к Discord...")

try:
    rpc = Presence(CLIENT_ID)
    rpc.connect()
    print("✅ Успешно подключено к Discord!")
    
    print("\nОтправляю тестовое обновление в Discord...")
    rpc.update(
        details="Тест подключения",
        state="Если вы видите это, всё работает!",
        start=int(time.time())
    )
    print("✅ Обновление отправлено!")
    print("\n" + "="*50)
    print("ВАЖНО: Проверьте Discord прямо сейчас!")
    print("="*50)
    print("\nГде искать статус:")
    print("1. В списке друзей - ваш профиль должен показывать активность")
    print("2. В профиле - наведите на свой аватар")
    print("3. В настройках: Настройки → Активность")
    print("\nЕсли ничего не видно:")
    print("- Откройте Discord → Settings → Activity Privacy")
    print("  (Настройки → Конфиденциальность активности)")
    print("- Включите 'Display current activity as a status message'")
    print("  (Отображать активность в качестве статуса)")
    print("- Включите 'Allow access to game activity'")
    print("  (Разрешить доступ к активности игры)")
    print("\nНажмите Enter для выхода...")
    try:
        input()
    except:
        pass
    
    rpc.close()
    print("Отключено от Discord")
    
except FileNotFoundError:
    print("❌ Ошибка: Discord не найден!")
    print("   Запустите Discord перед запуском этого скрипта")
except ConnectionRefusedError:
    print("❌ Ошибка: Discord отклонил подключение!")
    print("   Перезапустите Discord и попробуйте снова")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()


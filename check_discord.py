#!/usr/bin/env python3
"""Расширенная проверка Discord Rich Presence"""

import os
import time
from pypresence import Presence

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
if not CLIENT_ID:
    print("❌ Ошибка: DISCORD_CLIENT_ID не установлен")
    print("Установите: export DISCORD_CLIENT_ID=\"1450951913175519366\"")
    exit(1)

print("="*60)
print("ПРОВЕРКА DISCORD RICH PRESENCE")
print("="*60)
print(f"\nDiscord Client ID: {CLIENT_ID}")

try:
    print("\n1. Подключение к Discord...")
    rpc = Presence(CLIENT_ID)
    rpc.connect()
    print("   ✅ Успешно подключено!")
    
    print("\n2. Отправка тестового обновления...")
    rpc.update(
        details="🎵 Тест Yandex Music",
        state="Проверка работы Rich Presence",
        start=int(time.time()),
        large_image="yandex_music",
        large_text="Yandex Music",
        small_image="yandex_music",
        small_text="Слушает музыку"
    )
    print("   ✅ Обновление отправлено!")
    
    print("\n" + "="*60)
    print("ГДЕ ИСКАТЬ СТАТУС В DISCORD:")
    print("="*60)
    print("\n1. В списке друзей (левая панель):")
    print("   - Найдите свой профиль в списке")
    print("   - Должен быть зелёный индикатор и статус активности")
    
    print("\n2. В профиле пользователя:")
    print("   - Наведите курсор на свой аватар")
    print("   - Должен появиться popup с активностью")
    
    print("\n3. В настройках Discord:")
    print("   - Settings → Activity Privacy")
    print("   - (Настройки → Конфиденциальность активности)")
    print("   - Должна быть видна активность 'Тест Yandex Music'")
    
    print("\n" + "="*60)
    print("ЕСЛИ НИЧЕГО НЕ ВИДНО:")
    print("="*60)
    print("\n1. Откройте Discord → Settings → Activity Privacy")
    print("   (Настройки → Конфиденциальность активности)")
    print("\n2. Убедитесь, что включено:")
    print("   ✅ 'Display current activity as a status message'")
    print("      (Отображать активность в качестве статуса)")
    print("   ✅ 'Allow access to game activity'")
    print("      (Разрешить доступ к активности игры)")
    print("\n3. Перезапустите Discord")
    print("4. Запустите этот скрипт снова")
    
    print("\n" + "="*60)
    print("Ожидание 10 секунд для проверки...")
    print("="*60)
    time.sleep(10)
    
    print("\nОтправка второго обновления...")
    rpc.update(
        details="🎵 Yandex Music работает!",
        state="Если вы видите это - всё работает",
        start=int(time.time())
    )
    print("✅ Второе обновление отправлено!")
    
    print("\nНажмите Enter для выхода...")
    try:
        input()
    except:
        pass
    
    rpc.close()
    print("\n✅ Отключено от Discord")
    
except FileNotFoundError:
    print("\n❌ ОШИБКА: Discord не найден!")
    print("\nРешение:")
    print("1. Убедитесь, что Discord запущен (десктопная версия)")
    print("2. Не используйте Discord в браузере - нужна десктопная версия")
    print("3. Перезапустите Discord")
    exit(1)
    
except ConnectionRefusedError:
    print("\n❌ ОШИБКА: Discord отклонил подключение!")
    print("\nРешение:")
    print("1. Перезапустите Discord")
    print("2. Убедитесь, что Discord полностью загрузился")
    print("3. Попробуйте снова")
    exit(1)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    exit(1)


# Yandex Music Discord Rich Presence

Кросс-платформенное приложение для отображения текущего трека из Яндекс.Музыки в Discord Rich Presence.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

### 1. Создайте Discord Application

- Перейдите на https://discord.com/developers/applications
- Нажмите "New Application"
- Введите название (например, "Yandex Music")
- Нажмите "Create"
- В разделе "General Information" найдите "Application ID"
- Скопируйте Application ID (это и есть Client ID)

### 2. Настройте переменную окружения

**Вариант 1: Файл .env (рекомендуется для всех платформ)**

Создайте файл `.env` в корне проекта:
```
DISCORD_CLIENT_ID=ваш_application_id
```

**Вариант 2: Переменная окружения**

**Windows (PowerShell):**
```powershell
$env:DISCORD_CLIENT_ID="ваш_application_id"
```

**Windows (CMD):**
```cmd
set DISCORD_CLIENT_ID=ваш_application_id
```

**Linux/macOS:**
```bash
export DISCORD_CLIENT_ID="ваш_application_id"
```

Для постоянной установки на macOS/Linux добавьте в `~/.zshrc` или `~/.bashrc`:
```bash
export DISCORD_CLIENT_ID="ваш_application_id"
```

Затем выполните:
```bash
source ~/.zshrc
```

### 3. Установите расширение браузера

- Откройте Chrome/Edge
- Перейдите на `chrome://extensions/` (или `edge://extensions/`)
- Включите "Режим разработчика" (Developer mode)
- Нажмите "Загрузить распакованное расширение" (Load unpacked)
- Выберите папку `extension` из этого проекта

## Запуск

**Важно:** Убедитесь, что Discord запущен перед запуском сервера.

### Кросс-платформенный запуск (рекомендуется)

```bash
python launch.py
```

или

```bash
python3 launch.py
```

Скрипт автоматически:
- Проверит наличие `DISCORD_CLIENT_ID`
- Проверит, не занят ли порт 8080
- Установит зависимости (если нужно)
- Запустит сервер

### Альтернативный запуск

**Linux/macOS:**
```bash
./launch.sh
```

**Windows:**
```cmd
python server.py
```

### Использование

1. Запустите сервер (см. выше)
2. Откройте https://music.yandex.ru
3. Начните воспроизведение музыки

Расширение будет автоматически отправлять информацию о текущем треке на локальный сервер (localhost:8080), который обновит ваш статус в Discord.

## Устранение проблем

### Статус не отображается в Discord

**Шаг 1: Проверьте подключение к Discord**

Запустите тестовый скрипт:
```bash
python3 test_discord.py
```

Если видите ошибку "Discord не найден" или "Discord отклонил подключение":
- **Убедитесь, что Discord запущен** (десктопная версия, не веб)
- Перезапустите Discord
- Убедитесь, что используете правильный Client ID

**Шаг 2: Проверьте настройки Discord**

1. Откройте Discord
2. Перейдите в **Settings** → **Activity Privacy** (или **Настройки** → **Конфиденциальность активности**)
3. Убедитесь, что включено:
   - ✅ **"Display current activity as a status message"** (Отображать активность в качестве статуса)
   - ✅ **"Allow access to game activity"** (Разрешить доступ к активности игры)

**Шаг 3: Проверьте сервер**

1. **Проверьте статус сервера:**
   
   **Windows (PowerShell):**
   ```powershell
   Invoke-WebRequest http://localhost:8080
   ```
   
   **Linux/macOS:**
   ```bash
   curl http://localhost:8080
   ```
   
   Должен вернуться JSON с информацией о текущем треке

2. **Проверьте логи сервера:**
   - При запуске должно быть: "✅ Успешно подключено к Discord!"
   - При обновлении трека должно быть: "✅ Трек обновлен: [название] - [исполнитель]"

**Шаг 4: Проверьте расширение браузера**

1. Откройте DevTools (F12) на странице music.yandex.ru
2. Во вкладке Console должны быть сообщения: "Track: [название] - [исполнитель]"
3. Если сообщений нет, перезагрузите расширение в `chrome://extensions/`

**Шаг 5: Перезапустите всё**

1. Остановите сервер (Ctrl+C в терминале)
2. Убедитесь, что Discord запущен
3. Запустите сервер снова: `python launch.py`
4. Обновите страницу music.yandex.ru

## Поддерживаемые платформы

- ✅ Windows 10/11
- ✅ macOS
- ✅ Linux

## Требования

- Python 3.7+
- Discord Desktop (не веб-версия)
- Chrome/Edge браузер

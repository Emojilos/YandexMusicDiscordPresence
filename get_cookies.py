import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def get_yandex_cookies():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get('https://music.yandex.ru')
        print("Откройте браузер и войдите в Yandex Music")
        print("Нажмите Enter после входа...")
        input()
        
        cookies = driver.get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        cookie_file = os.path.expanduser('~/.yandex_music_cookies.json')
        with open(cookie_file, 'w') as f:
            json.dump(cookies_dict, f)
        
        print(f"Cookies сохранены в {cookie_file}")
        return cookies_dict
    finally:
        driver.quit()

if __name__ == '__main__':
    get_yandex_cookies()


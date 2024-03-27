from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--excludeSwitches=enable-automation")
options.add_argument("--useAutomationExtension=false")


def download_album(band_link):
    # Получаем название папки из ссылки
    folder_name = band_link.split('/')[-1]

    # Создаем папку, если она не существует
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)



    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()

    wait = WebDriverWait(driver, timeout=40)

    driver.get('https://www.tubeninja.net/ru/welcome')
    time.sleep(6)

    find_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/form/div[1]/input')))
    find_button.send_keys(band_link)
    time.sleep(5)
    click_find = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/form/div[1]/div')))
    click_find.click()
    time.sleep(8)

    # Находим все кнопки на странице
    buttons = driver.find_elements(By.CSS_SELECTOR, ".list-group-item.playlist")

    time.sleep(8)

    for button in buttons:
        # Нажимаем на кнопку
        button.click()
        time.sleep(2)  # Пауза для загрузки списка аудиофайлов

    time.sleep(5)

    # Формируем XPath для нахождения элементов с аудиофайлами
    audio_xpath = "//a[starts-with(@href, 'https://t4.bcbits.com/stream/')]"

    print(f"XPath for audio files: {audio_xpath}")

    # Находим элемент с картинкой
    image_element = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/img")))
    # Получаем URL картинки
    image_url = image_element.get_attribute("src")
    # Скачиваем картинку
    image_response = requests.get(image_url)
    # Задаем имя файла для сохранения
    image_file_name = "album_image.jpg"
    # Записываем картинку на диск
    with open(os.path.join(folder_name, image_file_name), "wb") as image_file:
        image_file.write(image_response.content)

    print("Image downloaded.")

    # Находим все элементы с аудиофайлами по ссылке "https://t4.bcbits.com/stream/"
    audio_files = driver.find_elements(By.XPATH, audio_xpath)

    # Проходимся по каждому аудиофайлу
    for index, audio_file in enumerate(audio_files, start=1):
        # Получаем URL аудиофайла
        audio_url = audio_file.get_attribute("href")
        time.sleep(2)
        print("Downloading audio file...")
        # Скачиваем аудиофайл (используем библиотеку requests)
        response = requests.get(audio_url)
        time.sleep(2)

        # Получаем заголовок альбома
        div_number = index  # Устанавливаем div_number равным индексу, так как он зависит от индекса
        album_title_element = wait.until(EC.visibility_of_element_located((By.XPATH, f"/html/body/div[2]/div[1]/div[{div_number}]/div[2]/h1")))
        album_title = album_title_element.text

        # Генерируем имя файла на основе заголовка альбома и индекса
        file_name = f"{album_title}.mp3"
        # Записываем аудиофайл на диск
        file_path = os.path.join(folder_name, file_name)
        # Записываем аудиофайл на диск
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Audio file downloaded.{index}")

        time.sleep(2)

    driver.quit()


with open("links.txt", "r") as file:
    band_links = [link.strip() for link in file.readlines()]

for band_link in band_links:
    download_album(band_link)

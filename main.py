import os
import random
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv

from bs4 import BeautifulSoup

INSTAGRAM_URL = "https://www.instagram.com/"
REELS_URL = "https://www.instagram.com/reels/"

# Environment variables
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


def login(driver, user, password) -> None:
    def input_creds(d, user, password) -> None:
        user_form = WebDriverWait(d, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        user_form.send_keys(user)
        password_form = WebDriverWait(d, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_form.clear()
        password_form.send_keys(password)

    def submit(d) -> None:
        WebDriverWait(d, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()  # Login

        try:
            WebDriverWait(d, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(text(), "Not Now")]')
                )
            ).click()  # Not now

            WebDriverWait(d, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(text(), "Not Now")]')
                )
            ).click()  # Not now 2
        except Exception as _:
            pass  # dont care

    input_creds(driver, user, password)
    submit(driver)


def video_duration(d, video_index) -> Optional[float]:
    """Finds the duration of the video on screen and returns it in seconds"""
    v = d.find_elements(By.TAG_NAME, "video")[video_index]

    if not v:
        return None
    return float(v.get_attribute("duration"))


def next_reel(d):
    """Scroll to the next reel using the down arrow key"""
    body = d.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.ARROW_DOWN)


def main():
    def create_driver() -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(options=options)

    d = create_driver()
    d.get(INSTAGRAM_URL)
    login(d, email, password)
    d.get(REELS_URL)

    video_index = 0
    while True:
        WebDriverWait(d, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
        )
        if (duration := video_duration(d, video_index)) is None:
            print("ERR: No duration found")
            continue
        print(f"Duration: {duration}")
        time.sleep(duration)
        next_reel(d)
        video_index += 1
        print("Next reel")


if __name__ == "__main__":
    main()

import os
import random
import threading
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

INSTAGRAM_URL = "https://www.instagram.com/"
REELS_URL = "https://www.instagram.com/reels/"

# Environment variables
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


class ThreadSafeWebDriver:
    @staticmethod
    def __create_driver() -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(options=options)

    def __init__(self):
        self.driver = ThreadSafeWebDriver.__create_driver()
        self.lock = threading.Lock()
        self.video_index = 0

    def __enter__(self) -> webdriver.Chrome:
        self.lock.acquire()
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()


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

        time.sleep(10)  # Wait for login

    input_creds(driver, user, password)
    submit(driver)


def video_duration(d, video_index) -> Optional[float]:
    """Finds the duration of the video on screen and returns it in seconds"""
    videos = d.find_elements(By.TAG_NAME, "video")
    print(f"Length of videos:{len(videos)}; Index {video_index}")
    v = None
    try:
        v = videos[video_index]
    finally:
        return None if not v else float(v.get_attribute("duration"))


def next_reel(d):
    body = d.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.ARROW_DOWN)


def like_reel(d, video_index):
    like_svgs = d.find_elements(By.CSS_SELECTOR, 'svg[aria-label="Like"]')
    try:
        svg = like_svgs[video_index]
        actions = ActionChains(d)
        actions.move_to_element(svg).click().perform()

    except Exception as e:
        print(e)


def follow_user(d, video_index):
    follow_buttons = d.find_elements(By.XPATH, "//*[normalize-space(text())='Follow']")
    try:
        follow_button = follow_buttons[video_index]
        actions = ActionChains(d)
        actions.move_to_element(follow_button).click().perform()
    except Exception as e:
        print(e)


def reel_scroller(driver: ThreadSafeWebDriver):
    while True:
        duration = None
        with driver as d:
            WebDriverWait(d, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )
            duration = video_duration(d, driver.video_index)

        if duration is None:
            time.sleep(1)  # Instagram is fetching new video
            continue

        skip_reel.wait(duration)
        skip_reel.clear()

        with driver as d:
            next_reel(d)
        driver.video_index += 1


def input_listener(driver: ThreadSafeWebDriver):
    # TODO: voice input
    while True:
        inp = input()
        if inp == "s":
            skip_reel.set()
            print("Skipping")
        elif inp == "l":
            with driver as d:
                like_reel(d, driver.video_index)
            print("Liking")
        elif inp == "f":
            with driver as d:
                follow_user(d, driver.video_index)
            print("Following")


skip_reel = threading.Event()

if __name__ == "__main__":
    driver = ThreadSafeWebDriver()
    with driver as d:
        d.get(INSTAGRAM_URL)
        login(d, email, password)
        d.get(REELS_URL)

    threading.Thread(target=reel_scroller, args=(driver,)).start()
    threading.Thread(target=input_listener, args=(driver,)).start()

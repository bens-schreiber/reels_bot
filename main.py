import logging
import os
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

skip_reel = threading.Event()

# Environment variables
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# Logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


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


def reel_scroller(tswd: ThreadSafeWebDriver):
    def video_duration(driver: webdriver.Chrome, video_index: int) -> Optional[float]:
        """Finds the duration of the video on screen and returns it in seconds"""
        videos = driver.find_elements(By.TAG_NAME, "video")
        v: Optional[float] = None
        try:
            v = videos[video_index]
        finally:
            return None if not v else float(v.get_attribute("duration"))

    def next_reel(driver: webdriver.Chrome):
        # TODO: Arrow down doesnt always register until page is manually scrolled
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ARROW_DOWN)

    while True:
        duration: Optional[float] = None
        with tswd as driver:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )
            duration = video_duration(driver, tswd.video_index)

        if duration is None:
            time.sleep(1)  # Instagram is fetching new video
            continue

        skip_reel.wait(duration)
        skip_reel.clear()

        with tswd as driver:
            next_reel(driver)

        tswd.video_index += 1


def get_user_input():
    return input()  # TODO: Voice command input


def input_listener(tswd: ThreadSafeWebDriver):
    """Runs commands based on some user input"""

    def follow_user(driver: webdriver.Chrome, video_index: int):
        follow_buttons = driver.find_elements(
            By.XPATH, "//*[normalize-space(text())='Follow']"
        )
        try:
            follow_button = follow_buttons[video_index]
            actions = ActionChains(driver)
            actions.move_to_element(follow_button).click().perform()
        except Exception as e:
            logging.error(e)

    def like_reel(driver: webdriver.Chrome, video_index: int):
        like_svgs = driver.find_elements(By.CSS_SELECTOR, 'svg[aria-label="Like"]')
        try:
            svg = like_svgs[video_index]
            actions = ActionChains(driver)
            actions.move_to_element(svg).click().perform()
        except Exception as e:
            logging.error(e)

    while True:
        inp = get_user_input()
        if inp == "s":
            skip_reel.set()
            logging.log(logging.INFO, "Skipping")
        elif inp == "l":
            with tswd as driver:
                like_reel(driver, tswd.video_index)
            logging.log(logging.INFO, "Liking")
        elif inp == "f":
            with tswd as driver:
                follow_user(driver, tswd.video_index)
            logging.log(logging.INFO, "Following")


def login(driver: webdriver.Chrome, user: str, password: str):
    def input_creds():
        user_form = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        user_form.send_keys(user)
        password_form = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_form.clear()
        password_form.send_keys(password)

    def submit():
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()  # Login

        time.sleep(6)  # Wait for login

    input_creds()
    submit()


if __name__ == "__main__":
    tswd = ThreadSafeWebDriver()
    with tswd as driver:
        driver.get(INSTAGRAM_URL)
        login(driver, email, password)
        driver.get(REELS_URL)

    threading.Thread(target=reel_scroller, args=(tswd,)).start()
    threading.Thread(target=input_listener, args=(tswd,)).start()

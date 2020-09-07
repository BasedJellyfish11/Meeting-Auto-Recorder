import string
import time
import datetime
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from win32api import GetSystemMetrics


class Meeting(ABC):

    def __init__(self, start_time: datetime, duration: float):
        self.startTime = start_time
        self.duration = duration
        self.chrome = None

    # Make the comparison operators work and compare start times so that we can sort the meetings by first to join
    def __eq__(self, other):
        return self.startTime == other.startTime and type(self) == type(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.startTime <= other.startTime

    def __lt__(self, other):
        return self.startTime < other.startTime

    def __ge__(self, other):
        return self.startTime >= other.startTime

    def __gt__(self, other):
        return self.startTime > other.startTime

    # Abstract start and end functions so that we can implement them in the child classes
    @abstractmethod
    def start_meeting(self):
        pass

    @abstractmethod
    def end_meeting(self):
        pass

    @staticmethod
    def __initialize_chrome(start_url: string):

        # Chrome because Firefox gives me issues with audio in teams apparently? Bruh
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('ignore-certificate-errors')
        chrome_options.add_argument('ignore-ssl-errors')
        chrome_options.add_argument("--use-fake-ui-for-media-stream")

        # Actually start Chrome, set the window to fullscreen for better recording
        chrome = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=chrome_options)
        chrome.set_window_size(GetSystemMetrics(0), GetSystemMetrics(1))
        chrome.set_window_position(0, 0)
        chrome.get(start_url)

        # Return the webdriver
        return chrome

    def __wait_until_found(self, element: string, timeout: float):

        # A utility method for selenium to wait for logins / page loads etc.
        try:
            element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, element))
            WebDriverWait(self.chrome, timeout).until(element_present)

            return self.chrome.find_element_by_css_selector(element)
        except exceptions.TimeoutException:
            print(f"Timeout waiting for element: {element}")
            return None

    def __input_keys_in_field_of_type(self, keys: string, field_type: string):
        field = self.__wait_until_found(f"input[type= '{field_type}']", 30)
        if field is not None:
            field.send_keys(keys)
            time.sleep(1)
        else:
            raise ValueError(f"The field {field_type} wasn't found")

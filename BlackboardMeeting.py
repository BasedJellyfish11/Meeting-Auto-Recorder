import string
import time
from datetime import datetime
from random import randrange
from Meeting import Meeting
from selenium.common.exceptions import ElementNotInteractableException


class BlackboardMeeting(Meeting):

    def __init__(self, start_time: datetime, duration: float, url: string, class_name: string):
        self.className = class_name
        self.url = url
        super().__init__(start_time, duration)

    def __login(self, url: string):
        # Blackboard login is as easy as getting the url given lol. Here's hoping the tokens don't expire else this will become a mess
        self.chrome = self.initialize_chrome(url)
        if self.wait_until_found("ul[class = 'item-list session-list']", 60*5) is None:
            raise ValueError("Login failed, or there's no session list!")

    def __find_classroom(self, name: string):
        # Gets the classroom that contains the name given and clicks it. If multiple have the same name, the top one will get clicked
        classroom_list = self.chrome.find_elements_by_css_selector("button[ng-click='sessionListItemContent.sessionClicked()']")
        self.find_correct_element(classroom_list, "aria-label", name)

    def __join_session(self):
        # Hits the big "Join Session" button, then switches the active selenium tab to the new one that opens upon clicking said button
        button = self.wait_until_found("bb-loading-button[on-click='launchSessionButton.launchSessionClicked()']", self.duration * 60 * 60)
        time.sleep(randrange(30, 120))  # Wait a bit so we don't instantly join the session the second it exists as that's weird
        try:
            button.click()
        except ElementNotInteractableException:
            self.click_if_exists("button[ng-click='launchSessionButton.getLaunchLinkClick()'", 5)
            time.sleep(1)
            self.click_if_exists("bb-loading-button[on-click='launchSessionButton.launchSessionClicked()']", 5)  # Purposefully not using click_if_exists so that it raises an exception if we can't join (mostly because of the class being expired or not yet available)
        time.sleep(0.5)
        self.chrome.switch_to.window(self.chrome.window_handles[-1])

    def __skip_tech_check(self):
        # Skips the audio test
        self.click_if_exists("button[ng-click='techCheck.cancelTechCheck()']", 60)

    def __skip_tutorial(self):
        # Skips the tutorial
        self.click_if_exists("button[ng-click='announcementModal.closeModal()']", 60)

    def __open_chat(self):
        self.click_if_exists("#side-panel-open", 60)
        self.click_if_exists("bb-channel-list-item[channel='channelSelector.getEveryoneChannel()']", 60)
        self.click_if_exists("button[analytics-id='guidance.chat-input.chat-input-focus-action']", 60)

    def start_meeting(self):
        self.__login(self.url)
        self.__find_classroom(self.className)
        self.__join_session()
        self.__skip_tech_check()
        self.__skip_tutorial()
        self.__open_chat()

    def end_meeting(self):
        self.chrome.quit()

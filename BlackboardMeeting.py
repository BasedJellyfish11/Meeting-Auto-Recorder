import string
import time
from datetime import datetime
from Meeting import Meeting


class BlackboardMeeting(Meeting):

    def __init__(self, start_time: datetime, duration: float, url: string, class_name: string):
        self.className = class_name
        self.url = url
        super().__init__(start_time, duration)

    def __login(self, url: string):
        # Blackboard login is as easy as getting the url given lol. Here's hoping the tokens don't expire else this will become a mess
        self.chrome = self.initialize_chrome(url)
        if self.wait_until_found("ul[class = 'item-list session-list'", 60*5) is None:
            raise ValueError("Login failed, or there's no session list!")

    def __find_classroom(self, name: string):
        # Gets the classroom that contains the name given and clicks it.
        classroom_list = self.chrome.find_elements_by_css_selector("#body-content > div.full-width-content--small > ul > li > div[bb-session-list-item-content = 'session'] > button[class = 'item-list__item session-list-item-content item-list__item--active']")
        self.find_correct_element(classroom_list, "aria-label", name)

    def __join_session(self):
        # Hits the big "Join Session" button, then switches the active selenium tab to the new one that opens upon clicking said button
        self.wait_until_found("#offcanvas-wrap > div.bb-offcanvas-panel.bb-offcanvas-right.peek.active.ng-scope > div > div > div > div > div:nth-child(3) > div", 10).click()
        time.sleep(0.5)
        self.chrome.switch_to.window(self.chrome.window_handles[-1])

    def __skip_audio_test(self):
        # Skips the audio test
        self.click_if_exists("#dialog-description-audio > div.techcheck-audio-skip.ng-scope > button", 60)

    def __skip_video_test(self):
        # Skips the video test
        self.click_if_exists("#fullcheck-skip-video", 60)

    def __skip_tutorial(self):
        # Skips the tutorial
        self.click_if_exists("#announcement-modal-page-wrap > div > div.announcement-later-tutorial.ng-scope > button", 60)

    def __close_tutorial_reminder(self):
        # Yeets the tutorial once and for all
        self.click_if_exists("#tutorial-dialog-tutorials-menu-learn-about-tutorials-menu-close", 60)

    def start_meeting(self):
        self.__login(self.url)
        self.__find_classroom(self.className)
        self.__join_session()
        self.__skip_audio_test()
        self.__skip_video_test()
        self.__skip_tutorial()
        self.__close_tutorial_reminder()

    def end_meeting(self):
        self.chrome.quit()

import string
from selenium.common.exceptions import NoSuchElementException
from Meeting import Meeting
import json
import random
import re
import time
from datetime import datetime
from threading import Timer

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType


# Most of this is taken from or inspired by https://github.com/TobiasPankner/Teams-Auto-Joiner , forcing this project to be GPL-3

class TeamsMeeting(Meeting):

    def __init__(self, start_time: datetime, duration: float, team_name: string, channel_name: string, email: string, password: string):
        self.email = email
        self.password = password
        self.teamName = team_name
        self.channelName = channel_name
        super().__init__(start_time, duration)

    def __login(self):
        self.chrome = self.initialize_chrome("https://teams.microsoft.com")  # Start chrome and send it to the teams main page
        self.input_keys_in_field_of_type(self.email + Keys.ENTER, "email")  # Input the email, hit enter to advance

        time.sleep(5)
        try:
            self.input_keys_in_field_of_type(self.email, "email")  # Do it again in case of organization login service
        except ValueError:
            print("The second email wasn't found. Continuing assuming the organization does not have an own login page")

        self.input_keys_in_field_of_type(self.password + Keys.ENTER, "password")  # Input the password

        time.sleep(1)  # idk why these sleep exist because the next one are always wait until found anyway but it was failing without them iirc
        self.click_if_exists("input[id='idBtn_Back']", 30)

        time.sleep(1)
        self.click_if_exists(".use-app-lnk", 10)  # Ignore the use app thing because it's stupid (and because automating it is harder than Selenium)

        time.sleep(1)
        self.click_if_exists("button.app-bar-link > ng-include > svg.icons-teams", 5)

        if self.wait_until_found("div[data-tid='team-channel-list']", 60 * 5) is None:
            raise ValueError("Login seems to have failed, as there's no teams list to be found (or is teams in not list mode?)")

    def __find_team(self, team_name: string):
        # Get all the teams
        teams = self.chrome.find_elements_by_css_selector("ul>li[role='treeitem']>div[sv-element]")
        # Return and click the good one
        return self.find_correct_element(teams, "data-tid", team_name)

    def __find_channel(self, team, channel_name: string):
        # Get all the channels
        try:
            channels = team.find_element_by_class_name("channels").find_elements_by_css_selector("ul[role='group']>ng-include>li[role='treeitem']")
        except NoSuchElementException:  # If it isn't found it's possible we clicked the team when it was already expanded, and collapsed the channel list
            team.click()
            time.sleep(1)
            channels = team.find_element_by_class_name("channels").find_elements_by_css_selector("ul[role='group']>ng-include>li[role='treeitem']")

        # Return and click the good one
        return self.find_correct_element(channels, "data-tid", channel_name)

    def start_meeting(self):
        self.__login()
        self.__find_channel(self.__find_team(self.teamName), self.channelName)

    def end_meeting(self):
        self.chrome.quit()



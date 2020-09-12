import subprocess
from TeamsMeeting import TeamsMeeting
from BlackboardMeeting import BlackboardMeeting
from MeetingJSONParser import MeetingJSONParser
import time
import datetime
from pathlib import Path
from tkinter import W, E, Label, Button, Entry, END, Tk, StringVar
from tkinter.filedialog import askopenfilename, sys


def enqueue_next_week_meeting(meeting_list: list, old_meeting):
    meeting_list.remove(old_meeting)
    next_week = old_meeting.startTime + datetime.timedelta(days=7)
    if type(old_meeting) is BlackboardMeeting:
        new_meeting = BlackboardMeeting(next_week, old_meeting.duration, old_meeting.url, old_meeting.className)
    else:
        new_meeting = TeamsMeeting(next_week, old_meeting.duration, old_meeting.teamName, old_meeting.channelName,
                                   old_meeting.email, old_meeting.password)

    meeting_list.append(new_meeting)
    meeting_list.sort()
    MeetingJSONParser.serialize_meeting_array(meeting_list)


def main_loop(obs_path: Path, obs_profile, obs_scene_collection, obs_scene):
    meeting_list = MeetingJSONParser.deserialize_teams()
    meeting_list.extend(MeetingJSONParser.deserialize_blackboard())
    meeting_list.sort()

    while True:
        current_meeting = meeting_list[0]
        wait_time = current_meeting.startTime - datetime.datetime.now()

        if wait_time.total_seconds() + current_meeting.duration * 60 * 60 < 0:
            print("The first meeting seems to be over already, skipping")
            enqueue_next_week_meeting(meeting_list, current_meeting)
            continue

        elif wait_time.total_seconds() > 0:
            print(f"Waiting for {wait_time.total_seconds()} seconds")
            time.sleep(wait_time.total_seconds())

        try:
            current_meeting.start_meeting()
        except Exception as e:
            print(f"{e} meeting start time was {current_meeting.startTime} type was {type(current_meeting)}")
            enqueue_next_week_meeting(meeting_list, current_meeting)
            continue  # Something bad happened with this meeting, but we can't really afford to halt execution in any one case, because then the next ones won't get joined either
            # Usually this would be WebDriver exception, ElementNotFoundException, and other similar selenium exceptions

        obs = subprocess.Popen(
            f"{obs_path} --profile \"{obs_profile}\" --startrecording --minimize-to-tray -m --collection \"{obs_scene_collection}\" --scene \"{obs_scene}\"",
            cwd=obs_path.parent)
        meeting_end_wait = current_meeting.startTime - datetime.datetime.now() + datetime.timedelta(hours=current_meeting.duration)  # Parameter order is a bit weird but PyCharm won't shut up about types otherwise
        print(f"Waiting for {meeting_end_wait.total_seconds()}")
        time.sleep(meeting_end_wait.total_seconds())

        try:
            current_meeting.end_meeting()
        except Exception as e:
            print(f"{e} meeting start time was {current_meeting.startTime} type was {type(current_meeting)}")

        obs.kill()
        enqueue_next_week_meeting(meeting_list, current_meeting)


# GUI stuff follows

class GUI:

    def __init__(self):
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title("Meeting auto recorder")

        self.obs_path = None
        self.obs_profile = StringVar()
        self.obs_scene = StringVar()
        self.obs_collection = StringVar()

        Label(self.root, text="Please select your OBS path").grid(sticky=W + E, row=0, column=0, columnspan=2, padx=0, pady=(8, 0))
        self.pathlabel = Entry(self.root, state="readonly")
        self.pathlabel.grid(sticky=E, row=1, column=0, columnspan=1, padx=10, pady=(2, 0))
        Button(self.root, text="Browse", command=self.browsefunc, bg="#cccccc").grid(sticky=W, row=1, column=1, columnspan=1, padx=10, pady=(2, 0))

        Label(self.root, text="OBS Scene Collection name").grid(sticky=W + E, row=2, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_collection).grid(sticky = W + E, row = 3, columnspan = 2, padx = 10, pady = 2)

        Label(self.root, text="OBS Scene name").grid(sticky=W + E, row=4, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_scene).grid(sticky = W + E, row = 5, columnspan = 2, padx = 10, pady = 2)

        Label(self.root, text="OBS Profile name").grid(sticky=W + E, row=6, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_profile).grid(sticky = W + E, row = 7, columnspan=2, padx=10, pady=2)

        self.start_button = Button(self.root, text="Start", command=self.start, bg="#cccccc", state="disabled")
        self.start_button.grid(sticky=W + E, row=8, column=0, columnspan=2, padx=20, pady=(20, 0))
        Button(self.root, text="Exit", command=self.exit, bg="#cccccc").grid(sticky=W + E, row=9, column=0, columnspan=2, padx=20, pady=(0, 10))

        self.root.mainloop()

    def browsefunc(self):
        self.obs_path = askopenfilename()
        self.pathlabel.config(state="normal")
        self.pathlabel.delete(0, END)
        self.pathlabel.insert(0, self.obs_path)
        self.pathlabel.config(state="readonly")
        self.start_button.config(state="normal")

    def start(self):
        if self.obs_path is None:
            print("OBS path wasn't set!")
            return
        self.root.withdraw()
        print("Running script, press CTRL + C to exit")
        main_loop(self.obs_path, self.obs_profile.get(), self.obs_collection.get(), self.obs_scene.get())

    @staticmethod
    def exit():
        sys.exit(0)


# Launch the GUI and let it do work
GUI()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

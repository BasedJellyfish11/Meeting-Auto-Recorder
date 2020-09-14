import os
import subprocess
from TeamsMeeting import TeamsMeeting
from BlackboardMeeting import BlackboardMeeting
from MeetingJSONParser import MeetingJSONParser
import time
import datetime
import threading
from pathlib import Path
from tkinter import W, E, Label, Button, Entry, END, Tk, StringVar, PhotoImage
from tkinter.filedialog import askopenfilename, sys


class main:

    stop = threading.Event()  # We don't want the GUI to become unresponsive, so the main should run in an extra thread. This will be the stop flag for said thread since kill() doesn't exist

    @staticmethod
    def __enqueue_next_week_meeting(meeting_list: list, old_meeting):
        """Once a meeting is over, it is assumed it repeats again next week on a schedule (classes-like). This will remove the meeting that just ended and enqueue it again next week"""
        meeting_list.remove(old_meeting)
        next_week = old_meeting.startTime + datetime.timedelta(days=7)
        if type(old_meeting) is BlackboardMeeting:
            new_meeting = BlackboardMeeting(next_week, old_meeting.duration, old_meeting.url, old_meeting.className, username=old_meeting.username, password=old_meeting.password)
        else:
            new_meeting = TeamsMeeting(next_week, old_meeting.duration, old_meeting.teamName, old_meeting.channelName,
                                       old_meeting.email, old_meeting.password)

        meeting_list.append(new_meeting)
        meeting_list.sort()
        MeetingJSONParser.serialize_meeting_array(meeting_list)

    @staticmethod
    def main_loop(obs_path: Path, obs_profile, obs_scene_collection, obs_scene):
        """The actual script you get me. Waits until a meeting is happening, joins it, records it, leaves it, then does the same thing again."""

        # Setup. Clears the thread flag, gets a list with all the meetings and sorts them by first to be joined
        main.stop.clear()
        meeting_list = MeetingJSONParser.deserialize_teams()
        meeting_list.extend(MeetingJSONParser.deserialize_blackboard())
        meeting_list.sort()

        while not main.stop.isSet():  # Pretty much while(true) except we have the thread flag to be set from the GUI when we want to stop
            current_meeting = meeting_list[0]  # Honestly, this is queue behaviour. It gets sorted every meeting though so I didn't want to make it an actual queue
            wait_time = current_meeting.startTime - datetime.datetime.now()

            if wait_time.total_seconds() + current_meeting.duration * 60 * 60 < 0:  # Meeting is over, skip
                print("The first meeting seems to be over already, skipping")
                main.__enqueue_next_week_meeting(meeting_list, current_meeting)
                continue

            elif wait_time.total_seconds() > 0:  # Wait until meeting time
                print(f"Waiting for {wait_time.total_seconds()} seconds")
                main.stop.wait(wait_time.total_seconds())

            if main.stop.isSet():  # If we didn't actually wait until meeting time, and instead the stop flag got set, we exit the loop.
                return  # Return seemed better (read: more readable) than continue into letting the loop handle it, because we're literally just exiting

            try:
                current_meeting.start_meeting()  # Actually start the meeting
            except Exception as e:
                print(f"{e} meeting start time was {current_meeting.startTime} type was {type(current_meeting)}. Exception was on starting the meeting")
                main.__enqueue_next_week_meeting(meeting_list, current_meeting)
                continue  # Something bad happened with this meeting, but we can't really afford to halt execution in any one case, because then the next ones won't get joined either
                # Usually this would be WebDriver exception, ElementNotFoundException, and other similar selenium exceptions

            obs = subprocess.Popen(
                f"{obs_path} --profile \"{obs_profile}\" --startrecording --minimize-to-tray -m --collection \"{obs_scene_collection}\" --scene \"{obs_scene}\"",
                cwd=obs_path.parent)  # Start obs with the profile, scene collection, and scene given, recording, minimized, and regardless of if there's another instance running
            meeting_end_wait = current_meeting.startTime - datetime.datetime.now() + datetime.timedelta(hours=current_meeting.duration)  # Parameter order is a bit weird but PyCharm won't shut up about types otherwise
            print(f"Waiting for {meeting_end_wait.total_seconds()}")
            main.stop.wait(meeting_end_wait.total_seconds())  # Wait until the meeting is over (or the script gets stopped I guess)

            try:
                current_meeting.end_meeting()  # End the meeting
            except Exception as e:
                print(f"{e} meeting start time was {current_meeting.startTime} type was {type(current_meeting)}")

            obs.kill()  # Exit obs. There's no way to tell OBS to stop recording (without like pressing a previously configured in OBS keybind I guess) so killing it and hoping it's recorded in .mkv or other recoverable video formats is the best option
            main.__enqueue_next_week_meeting(meeting_list, current_meeting)  # Enqueue next week's


# GUI stuff follows

class GUI:

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def __init__(self):
        self.root = Tk()
        self.root.resizable(False, False)  # Bro I literally do not know how to make it resizable good
        self.root.protocol("WM_DELETE_WINDOW", self.exit)  # We want to actually run the exit protocol on closing the GUI, instead of it just destroying the tkinter widget and leaving the main running
        # Vanity stuff because I am vane sis
        self.root.title("Meeting auto recorder")
        self.root.iconphoto(True, PhotoImage(file=GUI.resource_path("icon.png")))

        # Input variables
        self.obs_path = None
        self.obs_profile = StringVar()
        self.obs_scene = StringVar()
        self.obs_collection = StringVar()

        # Actual GUI stuff.
        Label(self.root, text="Please select your OBS path").grid(sticky=W + E, row=0, column=0, columnspan=2, padx=0, pady=(8, 0))
        self.pathlabel = Entry(self.root, state="readonly")
        self.pathlabel.grid(sticky=E, row=1, column=0, columnspan=1, padx=10, pady=(2, 0))
        Button(self.root, text="Browse", command=self.__browsefunc, bg="#cccccc").grid(sticky=W, row=1, column=1, columnspan=1, padx=10, pady=(2, 0))

        Label(self.root, text="OBS Scene Collection name").grid(sticky=W + E, row=2, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_collection).grid(sticky=W + E, row=3, columnspan=2, padx=10, pady=2)

        Label(self.root, text="OBS Scene name").grid(sticky=W + E, row=4, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_scene).grid(sticky=W + E, row=5, columnspan=2, padx=10, pady=2)

        Label(self.root, text="OBS Profile name").grid(sticky=W + E, row=6, column=0, columnspan=2, padx=0, pady=(8, 0))
        Entry(self.root, textvariable=self.obs_profile).grid(sticky=W + E, row=7, columnspan=2, padx=10, pady=2)

        self.start_button = Button(self.root, text="Start", command=self.start, bg="#cccccc", state="disabled")
        self.start_button.grid(sticky=W + E, row=8, column=0, columnspan=2, padx=20, pady=(20, 0))
        Button(self.root, text="Exit", command=self.exit, bg="#cccccc").grid(sticky=W + E, row=9, column=0, columnspan=2, padx=20, pady=(0, 10))

        # Start the GUI
        self.root.mainloop()

    def __browsefunc(self):
        """Allows the user to find a path, displays it on the pathlabel, then enables the start button"""
        self.obs_path = Path(askopenfilename())
        self.pathlabel.config(state="normal")
        self.pathlabel.delete(0, END)  # These two are what displays it on the pathlabel
        self.pathlabel.insert(0, self.obs_path)
        self.pathlabel.config(state="readonly")
        if self.obs_path != Path("."):  # Nothing was selected
            self.start_button.config(state="normal")
        else:
            self.start_button.config(state="disabled")

    def start(self):
        """Starts the main loop in another thread so that the GUI does not become unresponsive"""
        main.stop.clear()
        self.start_button.config(text="Running!", command=self.stop)  # User feedback is important ig
        threading.Thread(target=main.main_loop, args=(self.obs_path, self.obs_profile.get(), self.obs_collection.get(), self.obs_scene.get())).start()

    def stop(self):
        """Stops the main loop"""
        main.stop.set()  # Set the flag so that the loop thread returns and ends
        time.sleep(0.1)  # Makes sure the main thread stops correctly. If my concurrency teachers saw me solving race conditions like these with sleeps they'd kill me I am so sorry.
                         # I just don't think GUI responsiveness is a priority at all, and the 0.1 doesn't make it unresponsive anyway
        self.start_button.config(text="Start", command=self.start)  # Set the button back to start

    @staticmethod
    def exit():
        """ Close the application"""
        main.stop.set()   # Stop the thread
        sys.exit(0)  # Goodbye


# Launch the GUI and let it do work
GUI()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

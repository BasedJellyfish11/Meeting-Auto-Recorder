from TeamsMeeting import TeamsMeeting
from BlackboardMeeting import BlackboardMeeting
from MeetingJSONParser import MeetingJSONParser
import time
import datetime


def enqueue_next_week_meeting(meeting_list: list, old_meeting):
    meeting_list.remove(old_meeting)
    next_week = old_meeting.startTime + datetime.timedelta(days=7)
    if type(old_meeting) is BlackboardMeeting:
        new_meeting = BlackboardMeeting(next_week, old_meeting.duration, old_meeting.url, old_meeting.className)
    else:
        new_meeting = TeamsMeeting(next_week, old_meeting.duration, old_meeting.teamName, old_meeting.channelName, old_meeting.email, old_meeting.password)

    meeting_list.append(new_meeting)
    meeting_list.sort()
    MeetingJSONParser.serialize_meeting_array(meeting_list)


meeting_list = MeetingJSONParser.deserialize_teams()
meeting_list.extend(MeetingJSONParser.deserialize_blackboard())
meeting_list.sort()

while True:

    current_meeting = meeting_list[0]
    next_date = current_meeting.startTime + datetime.timedelta(days=7)
    wait_time = current_meeting.startTime - datetime.datetime.now()

    if wait_time.total_seconds() + current_meeting.duration * 60 * 60 < 0:
        print("The first meeting seems to be over already, skipping")
        enqueue_next_week_meeting(meeting_list, current_meeting)
        continue

    elif wait_time.total_seconds() > 0:
        print(f"Waiting for {wait_time.total_seconds()} seconds")
        time.sleep(wait_time.total_seconds())

    current_meeting.start_meeting()

    meeting_end_wait = current_meeting.startTime + datetime.timedelta(hours=current_meeting.duration) - datetime.datetime.now()
    print(f"Waiting for {meeting_end_wait.total_seconds()}")
    time.sleep(meeting_end_wait.total_seconds())

    current_meeting.end_meeting()
    enqueue_next_week_meeting(meeting_list, current_meeting)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

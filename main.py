from TeamsMeeting import TeamsMeeting
from MeetingJSONParser import MeetingJSONParser
import time
from BlackboardMeeting import BlackboardMeeting
import datetime


meeting_list = MeetingJSONParser.deserialize_teams()
meeting_list.extend(MeetingJSONParser.deserialize_blackboard())
meeting_list.sort()

while True:

    current_meeting = meeting_list[0]
    next_date = current_meeting.startTime + datetime.timedelta(days=7)

    wait_time = current_meeting.startTime - datetime.datetime.now()

    if wait_time.total_seconds() + current_meeting.duration * 60 * 60 < 0:
        print("The first meeting of the array seems to be over already, skipping")
        meeting_list.pop(0)
        MeetingJSONParser.serialize_meeting_array(meeting_list)
        continue

    elif wait_time.total_seconds() > 0:
        print(f"Waiting for {wait_time.total_seconds()} seconds")
        time.sleep(wait_time.total_seconds())

    if type(current_meeting) is TeamsMeeting:
        next_meeting = TeamsMeeting(next_date, current_meeting.duration, current_meeting.teamName, current_meeting.channelName, current_meeting.email, current_meeting.password)
    else:
        next_meeting = BlackboardMeeting(next_date, current_meeting.duration, current_meeting.url, current_meeting.className)

    meeting_list.pop(0)
    meeting_list.append(next_meeting)
    meeting_list.sort()
    MeetingJSONParser.serialize_meeting_array(meeting_list)

    current_meeting.start_meeting()
    meeting_end_wait = current_meeting.startTime + datetime.timedelta(hours=current_meeting.duration) - datetime.datetime.now()
    print(f"Waiting for {meeting_end_wait.total_seconds()}")
    time.sleep(meeting_end_wait.total_seconds())
    current_meeting.end_meeting()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

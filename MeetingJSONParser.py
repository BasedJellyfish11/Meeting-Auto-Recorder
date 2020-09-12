from datetime import datetime
import json
import string
from pathlib import Path
from BlackboardMeeting import BlackboardMeeting
from TeamsMeeting import TeamsMeeting


class MeetingJSONParser:

    blackboard_path = Path(__file__).parent.absolute().joinpath("JSONs").joinpath("Blackboard Meetings.json")
    teams_path = Path(__file__).parent.absolute().joinpath("JSONs").joinpath("Teams Meetings.json")

    @staticmethod
    def serialize_datetime(to_serialize: datetime):
        if isinstance(to_serialize, datetime):
            return to_serialize.isoformat()
        return to_serialize.__str__()  # Honestly maybe this should just throw but idk, just in case you get me?

    @staticmethod
    def serialize_meeting_array(array: list):

        # Wipe the files
        open(MeetingJSONParser.blackboard_path, "w").close()
        open(MeetingJSONParser.teams_path, "w").close()

        for meeting in array:
            if type(meeting) is BlackboardMeeting:
                MeetingJSONParser.serialize_blackboard(meeting)
            elif type(meeting) is TeamsMeeting:
                MeetingJSONParser.serialize_teams(meeting)

    @staticmethod
    def serialize_teams(meeting: TeamsMeeting):
        with open(MeetingJSONParser.teams_path, "a") as file:
            json.dump(meeting.__dict__, file, indent=2, default=MeetingJSONParser.serialize_datetime)
            file.close()

    @staticmethod
    def serialize_blackboard(meeting: BlackboardMeeting):
        with open(MeetingJSONParser.blackboard_path, "a") as file:
            json.dump(meeting.__dict__, file, indent=2, default=MeetingJSONParser.serialize_datetime)
            file.close()

    @staticmethod
    def deserialize_teams():  # TODO: Remember to reformat this when I'm not tired and on a timer because it's ugly
        teams_list = []
        with open(MeetingJSONParser.teams_path, "r") as file:
            for line in file:
                if "email" in line:
                    email = MeetingJSONParser.get_json_value(line)
                elif "password" in line:
                    password = MeetingJSONParser.get_json_value(line)
                elif "teamName" in line:
                    teamName = MeetingJSONParser.get_json_value(line)
                elif "channelName" in line:
                    channelName = MeetingJSONParser.get_json_value(line)
                elif "startTime" in line:
                    startTime = datetime.fromisoformat(f"{MeetingJSONParser.get_json_value(line)}")
                elif "duration" in line:
                    duration = float(MeetingJSONParser.get_json_value(line))
                elif "}" in line:
                    meeting = TeamsMeeting(startTime, duration, teamName, channelName, email, password)
                    teams_list.append(meeting)
            file.close()
        return teams_list

    @staticmethod
    def deserialize_blackboard():  # TODO: Same as above
        blackboard_list = []
        username = None
        password = None
        with open(MeetingJSONParser.blackboard_path, "r") as file:
            for line in file:
                if "className" in line:
                    className = MeetingJSONParser.get_json_value(line)
                elif "url" in line:
                    url = MeetingJSONParser.get_json_value(line)
                elif "startTime" in line:
                    startTime = datetime.fromisoformat(f"{MeetingJSONParser.get_json_value(line)}")
                elif "duration" in line:
                    duration = float(MeetingJSONParser.get_json_value(line))
                elif "username" in line:
                    username = MeetingJSONParser.get_json_value(line)
                elif "password" in line:
                    password = MeetingJSONParser.get_json_value(line)
                elif "}" in line:
                    meeting = BlackboardMeeting(startTime, duration, url, className, username=username, password=password)
                    blackboard_list.append(meeting)
            file.close()
            return blackboard_list

    @staticmethod
    def get_json_value(value: string):
        return_value = value
        trimmed_start = False
        for(ind, character) in enumerate(value):
            if character == ':' and not trimmed_start:
                return_value = return_value[ind+1:]
                trimmed_start = True

        return_value = return_value.strip(" \"\n,")
        return return_value

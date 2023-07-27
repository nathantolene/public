#!/usr/bin/python3

# import urllib.parse
# import json
# import syslog
# from zoom_rooms import list_rooms
from datetime import datetime
# from zoomus import ZoomClient
# import zoom_api
import tool_box
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
# client = ZoomClient(api_key, api_sec)
year = "2022"
day = "01"
month = "01"
convert_time = datetime.fromisoformat(year + "-" + month + '-' + day)
debug = os.environ.get('debug')
date_format_str = '%Y-%m-%dT%H:%M:%SZ'
za = tool_box.ZoomApi()
zu = tool_box.ZoomUsers
rf = tool_box.RecordingFiles
zr = tool_box.ZoomRecordings
zm = tool_box.ZoomMeetings


def delete_zoom_recording(meeting_id):
    print("Meeting ID " + meeting_id)
    # if '/' in meeting_id:
    #     encoded = urllib.parse.quote(meeting_id, safe='')
    #     meeting_id = urllib.parse.quote(encoded, safe='')
    # check = client.recording.delete(meeting_id=meeting_id)
    # check = zoom_api.delete_recordings(meeting_id)
    check = za.delete_recordings(meeting_id)
    if check[1] == 204:
        # print('Recording Delete!')
        return True
    # return check.status_code
    return check[1]


def list_all_zoom_users():
    # group_response = client.user.list()
    group_list = za.get_users()
    # group_list = json.loads(group_response.content)
    return group_list


def strip_emails_from_group_list(group_list):
    # print(group_list)
    # for x in group_list['users']:
    for x in group_list:
        for y in x['users']:
            # print(y)
            # email = x['email']
            #     print(x['users'])
            user = zu(y)
            if debug:
                print('Email Address: ' + user.email)
                # syslog('Email Address: ' + email)
            find_old_recordings(user.email)


def find_old_recordings(email):
    # recordings_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
    # recordings_list = json.loads(recordings_response.content)
    recordings_list = za.list_user_recordings(email)

    # if debug:
    # print(recordings_list)
    # syslog(recordings_list)
    # for y in recordings_list['meetings']:
    for y in recordings_list['meetings']:
        # print(y)
        recording = zr(y)
        # if y['total_records'] != 0:
        if recording.recording_count != 0:
            # print(y['meetings'])
            # for w in y['meetings']:
            # for w in recordings_list['meetings']:
            #     recording = zm(w)
            # start = str(y['start_time'])
            start = str(recording.start_time)
            # topic = y['topic']
            topic = str(recording.topic)
            start_time = datetime.strptime(start, date_format_str)
            now = datetime.now()
            delta = start_time - now
            meeting_id = ''
            if debug:
                print('Topic: ' + topic)
                print('Start_time', str(start_time))
                print('Number of days old: ' + str(delta.days))
                # syslog(topic)
                # syslog(start_time)
                # syslog(delta.days)
            if delta.days <= -7:
                if debug:
                    print('More then 7 days old, time to delete')
                    # syslog('More then 7 days old, time to delete')
                # for z in y['recording_files']:
                for z in recording.recordings:
                    record = rf(z)
                    # meeting_id = z['meeting_id']
                    meeting_id = str(record.meeting_id)
                check = delete_zoom_recording(meeting_id)
                if check is True:
                    print("Deleted " + topic + " it is " + str(delta.days) + " days old.")
                else:
                    print("Something is wrong, here is the status code: " + str(check))


def check_for_specials_now():
    find_old_recordings('nathant@utm.edu')
    find_old_recordings('ebell@utm.edu')
    room_list = za.list_zoom_rooms()
    for x in room_list:
        zoom_id = str(x['zr_id'])
        # gen_host_id = "rooms_" + zoom_id + "@utm.edu"
        gen_host_id = f"rooms_{zoom_id}@utm.edu"
        # print(gen_host_id)
        find_old_recordings(gen_host_id)


def main():
    print('Starting Zoom auto delete!')
    group_list = list_all_zoom_users()
    strip_emails_from_group_list(group_list)
    check_for_specials_now()


if __name__ == "__main__":
    main()

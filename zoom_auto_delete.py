#!/usr/bin/python3

import json
import syslog
from zoom_rooms import list_rooms
from datetime import datetime
from zoomus import ZoomClient
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)
year = "2022"
day = "01"
month = "01"
convert_time = datetime.fromisoformat(year + "-" + month + '-' + day)
debug = os.environ.get('debug')
date_format_str = '%Y-%m-%dT%H:%M:%SZ'


def delete_zoom_recording(meeting_id):
    check = client.recording.delete(meeting_id=meeting_id)
    if check.status_code == '204':
        print('Recording Delete!')
        return True
    return False


def list_all_zoom_users():
    group_response = client.user.list()
    group_list = json.loads(group_response.content)
    if debug:
        print(group_list)
        #syslog.syslog(syslog.LOG_INFO, group_list)
    return group_list


def strip_emails_from_group_list(group_list):
    for x in group_list['users']:
        email = x['email']
        if debug:
            print('Email Address: ' + email)
            #syslog('Email Address: ' + email)
        find_old_recordings(email)


def find_old_recordings(email):
    recordings_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
    recordings_list = json.loads(recordings_response.content)
    #if debug:
    print(recordings_list)
        #syslog(recordings_list)
    for y in recordings_list['meetings']:
        start = str(y['start_time'])
        topic = y['topic']
        start_time = datetime.strptime(start, date_format_str)
        now = datetime.now()
        delta = start_time - now
        meeting_id = ''
        if debug:
            print('Topic: ' + topic)
            print('Start_time' + str(start_time))
            print('Number of days old: ' + str(delta.days))
            #syslog(topic)
            #syslog(start_time)
            #syslog(delta.days)
        if str(delta.days) == '-7' or str(delta.days) < '-7':
            if debug:
                print('More then 7 days old, time to delete')
                #syslog('More then 7 days old, time to delete')
            for z in y['recording_files']:
                meeting_id = z['meeting_id']
            check = delete_zoom_recording(meeting_id)
            if check:
                print("Deleted " + topic + "it is " + str(delta.days) + " old.")


def check_for_specials_now():
    find_old_recordings('nathant@utm.edu')
    find_old_recordings('ebell@utm.edu')
    room_list = list_rooms()
    for x in room_list['rooms']:
        zoom_id = str(x['id'])
        gen_host_id = "rooms_" + zoom_id + "@utm.edu"
        find_old_recordings(gen_host_id)


def main():
    group_list = list_all_zoom_users()
    strip_emails_from_group_list(group_list)
    check_for_specials_now()


if __name__ == "__main__":
    main()

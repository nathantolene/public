#!/usr/bin/python3

import json
import sys
import requests
import urllib.parse
# from zoomus import ZoomClient
from datetime import date, datetime
import os
from os.path import exists
import zoom_api
import mysql.connector
import zoom_auto_delete
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
home_path = os.environ.get('home_path')
# sub_path = os.environ.get('sub_path')
# year = "2022"
year = str(date.today().year)
day = "01"
month = "01"
convert_time = datetime.fromisoformat(year + "-" + month + '-' + day)
today = date.today()
today = today.strftime("%Y-%m-%dT%H:%M:%SZ")
# client = ZoomClient(api_key, api_sec)
group_id = os.environ.get('zoom_group_id')
zdl_host = os.environ.get('zdl_host')
zdl_user = os.environ.get('zdl_user')
zdl_password = os.environ.get('zdl_password')
zdl_database = os.environ.get('zdl_database')
debug = os.environ.get('debug')
space = " "
dot = "."
comma = ", "
cm = "', '"
changer = 0
slash = '/'


def get_active_speaker_if_needed(meeting_id, topic):
    sswsv = check_for_shared_screen_with_speaker_view(meeting_id)
    # if sswsv is False:
    print('sswsv', sswsv)
    if not sswsv:
        check = move_active_speaker_to_upload_dir(meeting_id)
        print('check', check)
        # if check is False:
        if not check:
            print("This Meeting doesn't have a recording to upload to AVideo", topic)


def mysql_insert_update(select_sql):
    db = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    db.commit()
    db.close()


def mysql_select(select_sql):
    db = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    result = cursor.fetchall()
    db.close()
    return result


def get_zoom_group_emails():
    group_list = zoom_api.list_user_in_group(group_id)
    print('Getting Zoom Group List')
    return group_list


def update_recording_count(group_list):
    for x in group_list['members']:
        email = x['email']
        # recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        recording_list = zoom_api.list_user_recordings(email)
        # recording_list = json.loads(recording_list_response.content)
        for meetings in recording_list['meetings']:
            recording_count = meetings['recording_count']
            if recording_count == 0:
                continue
            zoom_meeting_id = meetings['id']
            meeting_id = meetings['uuid']  # key to meeting id
            select_sql = "select recording_count, topic from meetings where meeting_id ='" + meeting_id + "'"
            result = mysql_select(select_sql)
            topic = result['topic']
            for y in result:
                if not str(y['recording_count']) == recording_count:
                    update_sql = "update meetings set recording_count ='" \
                                 + str(recording_count) + "' where meeting_id ='" + meeting_id + "'"
                    mysql_insert_update(update_sql)
            select_sql = "select downloaded from recordings where meeting_id = '" + meeting_id + "'"
            result = mysql_select(select_sql)
            full_download = 0
            for y in result:
                if y['downloaded'] is None:
                    continue
                full_download = full_download + y['downloaded']
            if full_download == recording_count:
                print('Full Downloaded: ' + str(full_download))
                print('Recording Count: ' + str(recording_count))
                if '/' in meeting_id:
                    encoded = urllib.parse.quote(meeting_id, safe='')
                    meeting_id = urllib.parse.quote(encoded, safe='')
                # check = client.recording.delete(meeting_id=zoom_meeting_id)
                get_active_speaker_if_needed(zoom_meeting_id, topic)
                check = zoom_api.delete_recordings(zoom_meeting_id)
                print('Check Status Code: ' + str(check))
                if check[1] == '204':
                    print("Status Code is 204 marking as downloaded")
                    update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting_id + "'"
                    mysql_insert_update(update_sql)
                if check[1] == '404':
                    print("Status code is 404 marking as downloaded")
                    update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting_id + "'"
                    mysql_insert_update(update_sql)


def get_list_of_recordings_from_email_list(group_list):
    # Purpose of this function is to insert recording info into zdl_database db for later processing
    for x in group_list['members']:
        email = x['email']
        print('Checking for recordings for user:', email)
        recording_list = zoom_api.list_user_recordings(email)
        for meetings in recording_list['meetings']:
            uuid_status = check_uuid(meetings['uuid'])
            if not uuid_status:
                print('Inserting new meeting info for', meetings['topic'])
                insert_new_meeting_info(meetings)
            try:
                for recordings in meetings['recording_files']:
                    status = recordings['status']
                    if status == 'processing':
                        print('Recording still processing on Zoom', meetings['topic'])
                        continue
                    recording_id = recordings['id']
                    new_recording = check_for_recording_id(recording_id)
                    if not new_recording:
                        print('Inserting new recording info for', meetings['topic'])
                        insert_new_recording_info(recordings)
            except KeyError:
                continue


def check_uuid(uuid):
    select_sql = "select id, meeting_id from meetings where meeting_id = '" + uuid + "'"
    result = mysql_select(select_sql)
    for x in result:
        if x['meeting_id'] == uuid:
            return True
    return False


def insert_new_meeting_info(meetings):
    start_time = meetings['start_time']
    sql_time = start_time
    sql_time = datetime.fromisoformat(sql_time[:-1])
    sql_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    meetings_id = meetings['uuid']  # key to meeting id
    meetings_zoom_number = str(meetings['id'])
    account_id = str(meetings['account_id'])
    host_id = str(meetings['host_id'])
    topic = str(meetings['topic'])
    topic = topic.replace("'", "_")
    meetings_type = str(meetings['type'])
    timezone = str(meetings['timezone'])
    duration = str(meetings['duration'])
    recording_count = str(meetings['recording_count'])
    share_url = str(meetings['share_url'])
    insert_sql = "insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
                 "start_time, timezone, duration, recording_count, share_url, modified) values ('" \
                 + meetings_id + cm + meetings_zoom_number + cm + account_id + \
                 cm + host_id + cm + topic + cm + meetings_type + \
                 cm + sql_time + cm + timezone + cm + duration + \
                 cm + recording_count + cm + share_url + cm + timestamp + "')"
    mysql_insert_update(insert_sql)


def insert_new_recording_info(recordings):
    status = str(recordings['status'])
    recording_id = str(recordings['id'])
    meeting_id = str(recordings['meeting_id'])
    recording_start = str(recordings['recording_start'])
    recording_end = str(recordings['recording_end'])
    file_type = str(recordings['file_type'])
    file_extension = str(recordings['file_extension'])
    file_size = str(recordings['file_size'])
    try:
        play_url = recordings['play_url']
    except KeyError:
        play_url = 'TRANSCRIPT'
    download_url = str(recordings['download_url'])
    recording_type = str(recordings['recording_type'])
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_time = recording_start
    sql_time = datetime.fromisoformat(sql_time[:-1])
    start_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = recording_end
    end_time = datetime.fromisoformat(end_time[:-1])
    end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    insert_sql = "insert into recordings (status, recording_id, meeting_id, recording_start, recording_end," \
                 " file_type, file_extension, file_size, play_url, download_url, recording_type, modified) " \
                 "values ( '" + status + cm + recording_id + cm + meeting_id + cm + \
                 start_time + cm + end_time + cm + file_type + cm + file_extension + cm + \
                 file_size + cm + play_url + cm + download_url + cm + recording_type + cm + timestamp + "')"
    mysql_insert_update(insert_sql)


def check_for_recording_id(recording_id):
    select_sql = "select recording_id from recordings where recording_id ='" + recording_id + "'"
    result = mysql_select(select_sql)
    for x in result:
        if x['recording_id'] == recording_id:
            return True
    return False


def download_recording(zoomname, download_url, r_type):
    dl_url = download_url
    sub_path = r_type
    filename = zoomname
    path = home_path + sub_path + slash
    path_exist = os.path.exists(path)
    if not path_exist:
        os.makedirs(path)
    dl_path = os.path.join(path, filename)
    r = requests.get(dl_url, allow_redirects=True, stream=True)
    with requests.get(dl_url, allow_redirects=True, stream=True) as r, open(dl_path, "wb") as f:
        print("Downloading %s" % filename)
        total_length = r.headers.get('content-length')
        if total_length is None:  # no content length header
            f.write(r.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
    file_exist = os.path.exists(dl_path)
    if file_exist:
        return True
    else:
        return False


def check_db_and_download_all():
    select_sql = "select id, meeting_id, download_url, recording_start, recording_type," \
                 " file_type from recordings where downloaded is null;"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        r_id = str(x['id'])
        # print(r_id)
        m_id = str(x['meeting_id'])
        r_type = x['recording_type']
        download_url = str(x['download_url'])
        start_time = str(x['recording_start'])
        file_type = str(x['file_type'])
        select_sql2 = "select topic from meetings where meeting_id ='" + m_id + "'"
        result2 = mysql_select(select_sql2)
        # print(result2)
        # print(select_sql2)
        # topic = str(result2['topic'])
        for y in result2:
            topic = y['topic']
            print(topic)
            print(r_type)
            zoomname = topic + space + start_time + dot + file_type.lower()
            check = download_recording(zoomname, download_url, r_type)
            if check is True:
                update_to_downloaded(r_id)
        # for y in result2:
        #     topic = str(y['topic'])
        #     if not check_time_diff(r_id):
        #         print(topic)
        #         print(r_type)
        #         if r_type == 'audio_transcript':
        #             zoomname = topic + space + start_time + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'shared_screen_with_speaker_view':
        #             zoomname = topic + space + start_time + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'shared_screen_with_gallery_view':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'TIMELINE' or r_type == 'timeline':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'CHAT' or r_type == 'chat_file':
        #             zoomname = topic + space + start_time + space + r_type + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'gallery_view':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'shared_screen':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'active_speaker':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)
        #         if r_type == 'closed_caption':
        #             zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
        #             check = download_recording(zoomname, download_url, r_type)
        #             # print(zoomname)
        #             if check is True:
        #                 update_to_downloaded(r_id)


def update_to_downloaded(r_id):
    update_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
    mysql_insert_update(update_sql)


def delete_recordings_from_zoom(group_list):
    for x in group_list['members']:
        email = x['email']
        recording_list = zoom_api.list_user_recordings(email)
        # recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        # recording_list = json.loads(recording_list_response.content)
        # print(recording_list)
        for meetings in recording_list['meetings']:
            meeting_id = meetings['uuid']
            # print(meeting_id)
            select_sql = "select downloaded from meetings where meeting_id = '" + meeting_id + "'"
            result = mysql_select(select_sql)
            for y in result:
                # print(y)
                if str(y['downloaded']) == '1':
                    if '/' in meeting_id:
                        encoded = urllib.parse.quote(meeting_id, safe='')
                        meeting_id = urllib.parse.quote(encoded, safe='')
                    check = zoom_api.delete_recordings(meeting_id)
                    if check is False:
                        print('ERROR!!!')
                    # check = client.recording.delete(meeting_id=meeting_id)
                    # print('Check Status Code: ' + str(check.status_code))


def check_time_diff(r_id):
    select_sql = "select recording_start, recording_end from recordings where id ='" + r_id + "'"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        start = str(x['recording_start'])
        # print(start)
        end = str(x['recording_end'])
        # print(end)
        date_format_str = '%Y-%m-%d %H:%M:%S'
        start_time = datetime.strptime(start, date_format_str)
        end_time = datetime.strptime(end, date_format_str)
        diff = end_time - start_time
        diff_in_minutes = diff.total_seconds() / 60
        # print(diff_in_minutes)
        if diff_in_minutes < 10:
            update_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
            result = mysql_insert_update(update_sql)
            # print(result)
            return True
        return False


def check_for_shared_screen_with_speaker_view(meeting_id):
    select_sql = "select recording_type from recordings where meeting_id = '" + meeting_id + "';"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        if x['recording_type'] == 'shared_screen_with_speaker_view':
            return True
        else:
            continue
    return False


def move_active_speaker_to_upload_dir(meeting_id):
    select_sql = "select topic, start_time from meetings where meeting_id = '" + meeting_id + "'"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        topic = x['topic']
        start_time = str(x['start_time'])
        recording = topic + space + start_time + space + 'active_speaker.mp4'
        path = home_path + 'active_speaker/' + recording
        path = str(path)
        print(path)
        check = exists(path)
        if check is True:
            move_to = home_path + 'shared_screen_with_speaker_view/' + recording
            print('Moving Active Speaker to upload dir', topic)
            os.rename(path, move_to)
            return True
        return False


def main():
    group_list = get_zoom_group_emails()
    get_list_of_recordings_from_email_list(group_list)
    check_db_and_download_all()
    update_recording_count(group_list)
    delete_recordings_from_zoom(group_list)
    zoom_auto_delete.main()


if __name__ == "__main__":
    main()

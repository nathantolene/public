#!/usr/bin/python3
# import json
import sys
import requests
# import urllib.parse
# from zoomus import ZoomClient
from datetime import date, datetime
import os
from os.path import exists
import tool_box
# import zoom_api
import mysql.connector
import zoom_auto_delete
from dotenv import load_dotenv

load_dotenv()

za = tool_box.ZoomApi()
zm = tool_box.ZoomMeetings
zr = tool_box.ZoomRecordings
rf = tool_box.RecordingFiles
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


class ZoomGroupList:

    class Members:
        def __init__(self, member):
            try:
                self.id = member['id']
                self.first_name = member['first_name']
                self.last_name = member['last_name']
                self.type = member['type']
                self.primary_group = member['primary_group']
            except KeyError:
                pass
            self.email = member['email']


class ZoomDownloaderDB:
    class Recordings:
        def __init__(self, recording):
            self.id = recording['id']
            self.recording_id = recording['recording_id']
            self.meeting_id = recording['meeting_id']
            self.recording_start = recording['recording_start']
            self.recording_end = recording['recording_end']
            self.file_type = recording['file_type']
            self.file_extension = recording['file_extension']
            self.file_size = recording['file_size']
            self.play_url = recording['play_url']
            self.download_url = recording['download_url']
            self.recording_type = recording['recording_type']
            self.status = recording['status']
            self.downloaded = recording['downloaded']

    class Meetings:
        def __init__(self, meeting):
            self.id = meeting['id']
            self.account_id = meeting['account_id']
            self.host_id = meeting['host_id']
            self.topic = meeting['topic']
            self.meeting_type = meeting['meeting_type']
            self.start_time = meeting['start_time']
            self.timezone = meeting['timezone']
            self.duration = meeting['duration']
            self.recording_count = meeting['recording_count']
            self.share_url = meeting['share_url']
            self.meeting_id = meeting['meeting_id']
            self.meetings_zoom_number = meeting['meetings_zoom_number']
            self.downloaded = meeting['downloaded']

    class Specials:
        def __init__(self, special):
            self.id = special['id']
            self.meeting_id = special['meeting_id']
            self.meeting_topic = special['meeting_topic']
            self.days = special['days']


def check_if_special(meeting):
    start_time = datetime.strptime(meeting.start_time, '%Y-%m-%dT%H:%M:%SZ')
    start_day = datetime.strftime(start_time, '%a')
    select_sql = f"select * from specials where meeting_id ='{meeting.id}'"
    result = mysql_select(select_sql)
    for x in result:
        special = ZoomDownloaderDB.Specials(x)
        if special.days != '':
            if start_day in special.days:
                meeting.topic = special.meeting_topic
            else:
                continue
        else:
            meeting.topic = special.meeting_topic
        meeting.type = 3
    return meeting
    # if meeting.id == 2538404901:  # Expand to it's own def
    #     meeting.type = 3
    #     meeting.topic = 'BIO 130 Vanhoose'  # expand see above
    # if meeting.id == 9645631645:
    #     # '2023-01-26T21:27:38Z'
    #     start_time = datetime.strptime(meeting.start_time, '%Y-%m-%dT%H:%M:%SZ')
    #     start_day = datetime.strftime(start_time, '%a')
    #     print(start_day)
    #     if (start_day == 'Mon') or (start_day == 'Wed') or (start_day == 'Fri'):
    #         meeting.topic = 'ENGL 112 Glass'
    #     if (start_day == 'Tue') or (start_day == 'Thu'):
    #         meeting.topic = 'HIST 202 Jones'
    #     meeting.type = 3
    # if meeting.id == 6485187465:
    #     meeting.topic = "ENGL 112 Dierks"
    #     meeting.type = 3
    # if meeting.id == 9984425689:
    #     meeting.topic = "Math 210 Hamilton"
    #     meeting.type = 3
    # if meeting.id == 2096427308:
    #     meeting.topic = "Math 210 Gatewood_Camden"
    #     meeting.type = 3
    # if meeting.id == 3612598652:
    #     meeting.topic = "Math 210 Gatewood_Covington"
    #     meeting.type = 3
    # return meeting


def get_zoom_rooms_list_convert_to_group_list_type(group_list):
    z_rooms = za.list_zoom_rooms()
    for x in z_rooms:
        for y in x['rooms']:
            email = y['id']
            group_list['members'].append({'email': email})
    return group_list


def get_active_speaker_if_needed(meeting_id, topic):
    meeting_id = str(meeting_id)
    sswsv = check_for_shared_screen_with_speaker_view(meeting_id)
    if not sswsv:
        check = move_active_speaker_to_upload_dir(meeting_id)
        if not check:
            # print("This Meeting doesn't have a recording to upload to AVideo", topic)
            print(f"This Meeting doesn't have a recording to upload to AVideo {topic}")


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
    group_list = za.list_user_in_group(group_id)
    return group_list


def update_recording_count(recording_list):
    for x in recording_list:
        for meetings in x['meetings']:
            meeting = zr(meetings)
            if meeting.recording_count == 0:
                continue
            print(meeting.uuid)
            print(meeting.id)
            # select_sql = "select recording_count, topic from meetings where meeting_id ='" + str(meeting.uuid) + "'"
            select_sql = f"select * from meetings where meeting_id ='{str(meeting.uuid)}'"
            result = mysql_select(select_sql)
            topic = ''
            db_meeting = ''
            for y in result:
                db_meeting = ZoomDownloaderDB.Meetings(y)
                # topic = y['topic']
                # db_meeting = db_meeting
                # if not str(y['recording_count']) == meeting.recording_count:
                if not str(db_meeting.recording_count) == meeting.recording_count:
                    # update_sql = "update meetings set recording_count ='" \
                    #              + str(meeting.recording_count) + "' where meeting_id ='" + meeting.uuid + "'"
                    update_sql = f"update meetings set recording_count ='{str(meeting.recording_count)}' where " \
                                 f"meeting_id ='{meeting.uuid}'"
                    mysql_insert_update(update_sql)
            # select_sql = "select downloaded from recordings where meeting_id = '" + meeting.uuid + "'"
            select_sql = f"select downloaded from recordings where meeting_id = '{meeting.uuid}'"
            result = mysql_select(select_sql)
            full_download = 0
            for y in result:
                if y['downloaded'] is None:
                    continue
                full_download = full_download + y['downloaded']
            if full_download == meeting.recording_count:
                print('Full Downloaded: ' + str(full_download))
                print('Recording Count: ' + str(meeting.recording_count))
                get_active_speaker_if_needed(meeting.uuid, db_meeting.topic)
                check = za.delete_recordings(meeting.id)
                print('Check Status Code: ' + str(check))
                if check[1] == 204:
                    print("Status Code is 204 marking as downloaded")
                    # update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting.uuid + "'"
                    update_sql = f"update meetings set downloaded = 1 where meeting_id = '{meeting.uuid}'"
                    mysql_insert_update(update_sql)
                if check[1] == 404:
                    print("Status code is 404 marking as downloaded")
                    # update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting.uuid + "'"
                    update_sql = f"update meetings set downloaded = 1 where meeting_id = '{meeting.uuid}'"
                    mysql_insert_update(update_sql)


def get_list_of_recordings_from_email_list(group_list):
    # Purpose of this function is to insert recording info into zdl_database db for later processing
    recordings_lists = []
    for x in group_list['members']:
        # print(x)
        member = ZoomGroupList.Members(x)
        # email = x['email']
        # print('Checking for recordings for user:', email)
        print(f"Checking for recordings for user: {member.email}")
        # recording_list = zoom_api.list_user_recordings(email)
        recording_list = za.list_user_recordings(member.email)
        recordings_lists.append(recording_list)
        for meetings in recording_list['meetings']:
            # print(meetings)
            meeting = zr(meetings)
            if meeting.total_size == 0:
                continue
            meeting = check_if_special(meeting)
            if meeting.type != 3:
                continue
            uuid_status = check_uuid(meeting.uuid)
            if not uuid_status:
                # print('Inserting new meeting info for', meeting.topic)
                print(f"Inserting new meeting info for {meeting.topic}")
                insert_new_meeting_info(meeting)
            try:
                for recordings in meetings['recording_files']:
                    recording = rf(recordings)
                    # status = recordings['status']
                    status = recording.status
                    if status == 'processing':
                        print(f'Recording still processing on Zoom {meeting.topic}')
                        continue
                    # recording_id = recordings['id']
                    new_recording = check_for_recording_id(recording.id)
                    if not new_recording:
                        print(f'Inserting new recording info for {meeting.topic}')
                        insert_new_recording_info(recordings)
            except KeyError:
                continue
        # print(recordings_lists)
    return recordings_lists


def check_uuid(uuid):
    # select_sql = "select id, meeting_id from meetings where meeting_id = '" + uuid + "'"
    select_sql = f"select id, meeting_id from meetings where meeting_id = '{uuid}'"
    result = mysql_select(select_sql)
    for x in result:
        if x['meeting_id'] == uuid:
            return True
    return False


def insert_new_meeting_info(meetings):
    sql_time = meetings.start_time
    sql_time = datetime.fromisoformat(sql_time[:-1])
    sql_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    # insert_sql = f"insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
    #              "start_time, timezone, duration, recording_count, share_url, modified) values ('" \
    #              + str(meetings.uuid) + cm + str(meetings.id) + cm + str(meetings.account_id) + \
    #              cm + str(meetings.host_id) + cm + str(meetings.topic) + cm + str(meetings.type) + \
    #              cm + sql_time + cm + str(meetings.timezone) + cm + str(meetings.duration) + \
    #              cm + str(meetings.recording_count) + cm + str(meetings.share_url) + cm + timestamp + "')"
    insert_sql = f"insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
                 f"start_time, timezone, duration, recording_count, share_url, modified) values " \
                 f"(" \
                 f"'{str(meetings.uuid)}', " \
                 f"'{str(meetings.id)}', " \
                 f"'{str(meetings.account_id)}', " \
                 f"'{str(meetings.host_id)}', " \
                 f"'{str(meetings.topic)}', " \
                 f"'{str(meetings.type)}', " \
                 f"'{sql_time}', " \
                 f"'{str(meetings.timezone)}', " \
                 f"'{str(meetings.duration)}', " \
                 f"'{str(meetings.recording_count)}', " \
                 f"'{str(meetings.share_url)}', " \
                 f"'{timestamp}'" \
                 f")"
    mysql_insert_update(insert_sql)


def insert_new_recording_info(recordings):
    rec = rf(recordings)
    recording_start = str(recordings['recording_start'])
    recording_end = str(recordings['recording_end'])
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_time = recording_start
    sql_time = datetime.fromisoformat(sql_time[:-1])
    start_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = recording_end
    end_time = datetime.fromisoformat(end_time[:-1])
    end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    # insert_sql = "insert into recordings (status, recording_id, meeting_id, recording_start, recording_end," \
    #              " file_type, file_extension, file_size, play_url, download_url, recording_type, modified) " \
    #              "values ( '" + str(rec.status) + cm + str(rec.id) + cm + str(rec.meeting_id) + cm + \
    #              start_time + cm + end_time + cm + str(rec.file_type) + cm + str(rec.file_extension) + cm + \
    #              str(rec.file_size) + cm + str(rec.play_url) + cm + str(rec.download_url) + cm + \
    #              str(rec.recording_type) + cm + timestamp + "')"
    insert_sql = f"insert into recordings (status, recording_id, meeting_id, recording_start, recording_end, " \
                 f"file_type, file_extension, file_size, play_url, download_url, recording_type, modified) " \
                 f"values " \
                 f"(" \
                 f"'{str(rec.status)}', " \
                 f"'{str(rec.id)}', " \
                 f"'{str(rec.meeting_id)}', " \
                 f"'{start_time}', " \
                 f"'{end_time}', " \
                 f"'{str(rec.file_type)}', " \
                 f"'{str(rec.file_extension)}', " \
                 f"'{str(rec.file_size)}', " \
                 f"'{str(rec.play_url)}', " \
                 f"'{str(rec.download_url)}', " \
                 f"'{str(rec.recording_type)}', " \
                 f"'{timestamp}'" \
                 f")"
    mysql_insert_update(insert_sql)


def check_for_recording_id(recording_id):
    select_sql = f"select recording_id from recordings where recording_id ='{recording_id}'"
    result = mysql_select(select_sql)
    for x in result:
        if x['recording_id'] == recording_id:
            return True
    return False


def download_recording(zoom_name, download_url, r_type, meeting_topic):
    dl_url = download_url
    sub_path = r_type
    class_name = f"{meeting_topic}/"
    filename = zoom_name
    filename = filename.replace("/", "_")
    path = f"{home_path}{sub_path}/{class_name}/"
    path_exist = os.path.exists(path)
    if not path_exist:
        os.makedirs(path)
    dl_path = os.path.join(path, filename)
    # r = requests.get(dl_url, allow_redirects=True, stream=True)
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
    # select_sql = "select id, meeting_id, download_url, recording_start, recording_type," \
    #              " file_type from recordings where downloaded is null;"
    select_sql = "select * from recordings where downloaded is null"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        recording = ZoomDownloaderDB.Recordings(x)
        # r_id = str(x['id'])
        # print(r_id)
        # m_id = str(x['meeting_id'])
        # r_type = x['recording_type']
        # download_url = str(x['download_url'])
        # start_time = str(x['recording_start'])
        # file_type = str(x['file_type'])
        select_sql2 = f"select * from meetings where meeting_id ='{str(recording.meeting_id)}'"
        result2 = mysql_select(select_sql2)
        for y in result2:
            meeting = ZoomDownloaderDB.Meetings(y)
            # topic = y['topic']
            if not check_time_diff(recording.id):
                print(meeting.topic)
                print(recording.recording_type)
                zoom_name = f"{meeting.topic} {recording.recording_start}.{recording.file_type.lower()}"
                check = download_recording(zoom_name, recording.download_url, recording.recording_type, meeting.topic)
                if check is True:
                    update_to_downloaded(recording.id)


def update_to_downloaded(r_id):
    update_sql = f"update recordings set downloaded = 1 where id = '{r_id}'"
    mysql_insert_update(update_sql)


def delete_recordings_from_zoom(recordings_list):
    for x in recordings_list:
        # email = x['email']
        # # recording_list = zoom_api.list_user_recordings(email)
        # recording_list = za.list_user_recordings(email)
        # recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        # recording_list = json.loads(recording_list_response.content)
        # print(recording_list)
        for meetings in x['meetings']:
            meeting = zr(meetings)
            # meeting_id = meetings['uuid']
            # meeting_id = meeting.uuid
            # print(meeting_id)
            select_sql = f"select downloaded from meetings where meeting_id = '{str(meeting.id)}'"
            result = mysql_select(select_sql)
            for y in result:
                # print(y)
                if str(y['downloaded']) == '1':
                    # if '/' in str(meeting.uuid):
                    #     encoded = urllib.parse.quote(meeting_id, safe='')
                    #     meeting_id = urllib.parse.quote(encoded, safe='')
                    # check = zoom_api.delete_recordings(meeting_id)
                    check = za.delete_recordings(str(meeting.uuid))
                    if check is False:
                        print('ERROR!!!')
                    # check = client.recording.delete(meeting_id=meeting_id)
                    # print('Check Status Code: ' + str(check.status_code))


def check_time_diff(r_id):
    select_sql = f"select * from recordings where id ='{r_id}'"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        recording = ZoomDownloaderDB.Recordings(x)
        # start = str(x['recording_start'])
        # print(start)
        # end = str(x['recording_end'])
        # print(end)
        date_format_str = '%Y-%m-%d %H:%M:%S'
        start_time = datetime.strptime(str(recording.recording_start), date_format_str)
        end_time = datetime.strptime(str(recording.recording_end), date_format_str)
        diff = end_time - start_time
        diff_in_minutes = diff.total_seconds() / 60
        # print(diff_in_minutes)
        if diff_in_minutes < 10:
            update_sql = f"update recordings set downloaded = 1 where id = '{r_id}'"
            mysql_insert_update(update_sql)
            return True
        return False


def check_for_shared_screen_with_speaker_view(meeting_id):
    select_sql = f"select recording_type from recordings where meeting_id = '{meeting_id}';"
    # print(select_sql)
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        if x['recording_type'] == 'shared_screen_with_speaker_view':
            return True
        else:
            continue
    return False


def move_active_speaker_to_upload_dir(meeting_id):
    select_sql = f"select * from meetings where meeting_id = '{meeting_id}'"
    # print(select_sql)
    result = mysql_select(select_sql)
    # print(result)
    select_sql2 = f"select * from recordings where meeting_id = '{meeting_id}'"
    result2 = mysql_select(select_sql2)
    start_time = ''
    for y in result2:
        recording = ZoomDownloaderDB.Recordings(y)
        start_time = str(recording.recording_start)
        # start_time = str(y['recording_start'])
    for x in result:
        meeting = ZoomDownloaderDB.Meetings(x)
        # topic = x['topic']
        # start_time = str(x['start_time'])
        recording_name = f"{meeting.topic} {start_time}.mp4"
        path = f"{home_path}active_speaker/{recording_name}"
        path = str(path)
        # print(path)
        check = exists(path)
        if check is True:
            move_to = f"{home_path}shared_screen_with_speaker_view/{recording_name}"
            print(f"Moving Active Speaker to upload dir {meeting.topic}")
            os.rename(path, move_to)
            return True
    return False


def main():
    print('Getting Zoom Group List')
    group_list = get_zoom_group_emails()
    group_list = get_zoom_rooms_list_convert_to_group_list_type(group_list)
    recordings_list = get_list_of_recordings_from_email_list(group_list)
    print("Starting Downloads from list in DB")
    check_db_and_download_all()
    print('updating recording count')
    update_recording_count(recordings_list)
    print('deleting recordings from DB')
    delete_recordings_from_zoom(recordings_list)
    zoom_auto_delete.main()


if __name__ == "__main__":
    main()

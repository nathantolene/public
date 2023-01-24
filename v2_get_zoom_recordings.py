#!/usr/bin/python3

# import json
from syslog import syslog
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


class Meetings:
    def __init__(self, meetings):
        self.id = meetings['id']
        try:
            self.timestamp = meetings['timestamp']
            self.account_id = meetings['account_id']
            self.host_id = meetings['host_id']
            self.topic = meetings['topic']
            self.meeting_type = meetings['meeting_type']
            self.start_time = meetings['start_time']
            self.timezone = meetings['timezone']
            self.duration = meetings['duration']
            self.recording_count = meetings['recording_count']
            self.share_url = meetings['share_url']
            self.meeting_id = meetings['meeting_id']
            self.modified = meetings['modified']
            self.meetings_zoom_number = meetings['meetings_zoom_number']
            self.downloaded = meetings['downloaded']
        except:
            pass


class Recordings:
    def __init__(self, recording):
        self.id = recording['id']
        # try:
        self.timestamp = recording['timestamp']
        self.recording_id = recording['recording_id']
        self.meeting_id = recording['meeting_id']
        self.recording_start = recording['recording_start']
        self.recording_end = recording['recording_end']
        self.file_type = recording['file_type']
        try:
            self.file_extension = recording['extension']
        except:
            pass
        self.file_size = recording['file_size']
        self.play_url = recording['play_url']
        self.download_url = recording['download_url']
        self.recording_type = recording['recording_type']
        self.status = recording['status']
        self.modified = recording['modified']
        self.downloaded = recording['downloaded']
        # except:
        #     pass


def check_if_special(meeting):
    ''' This function is to allow for a non meeting type 3 to be processed example:
        if meeting.id == 2538404901:            set the meeting id, which in this case is a type 4 meeting
            meeting.type = 3                    change it's type to 3
            meeting.topic = 'BIO 130 Vanhoose'  add the topic to the meeting
    '''
    if meeting.id == 2538404901:
        meeting.type = 3
        meeting.topic = 'BIO 130 Vanhoose'
    if meeting.id == 9645631645:
        meeting.type = 3
        meeting.topic = 'HIST 202 Jones'
    return meeting


def get_zoom_rooms_list_convert_to_group_list_type(group_list):
    z_rooms = za.list_zoom_rooms()
    for x in z_rooms:
        email = x['zr_id']
        group_list['members'].append({'email': email})
    return group_list


def get_active_speaker_if_needed(meeting_id, topic):
    meeting_id = str(meeting_id)
    sswsv = check_for_shared_screen_with_speaker_view(meeting_id)
    if not sswsv:
        check = move_active_speaker_to_upload_dir(meeting_id)
        if not check:
            print(f"{topic} doesn't have a recording to upload to AVideo")
            syslog(f"{topic} doesn't have a recording to upload to AVideo")


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
            # print(meeting.uuid)
            # print(meeting.id)
            # select_sql = "select recording_count, topic from meetings where meeting_id ='" + str(meeting.uuid) + "'"
            select_sql = f"select * from meetings where meeting_id ='{str(meeting.uuid)}'"
            result = mysql_select(select_sql)
            topic = ''
            for y in result:
                m = Meetings(y)
                # topic = y['topic']
                topic = m.topic
                if not str(m.recording_count) == meeting.recording_count:
                # if not str(y['recording_count']) == meeting.recording_count:
                    # update_sql = "update meetings set recording_count ='" \
                    # + str(meeting.recording_count) + "' where meeting_id ='" + meeting.uuid + "'"
                    update_sql = f"update meetings set recording_count " \
                                 f"='{str(meeting.recording_count)}' " \
                                 f"where meeting_id ='{meeting.uuid}'"
                    mysql_insert_update(update_sql)
            # select_sql = "select downloaded from recordings where meeting_id = '" + meeting.uuid + "'"
            select_sql = f"select * from recordings where meeting_id = '{str(meeting.uuid)}'"
            result = mysql_select(select_sql)
            full_download = 0
            for y in result:
                r = Recordings(y)
                if r.downloaded is None:
                # if y['downloaded'] is None:
                    continue
                full_download = full_download + y['downloaded']
                full_download = full_download + r.downloaded
            if full_download == meeting.recording_count:
                print(f"Full Downloaded: {str(full_download)}")
                syslog(f"Full Downloaded: {str(full_download)}")
                print(f"Recording Count: {str(meeting.recording_count)}")
                syslog(f"Recording Count: {str(meeting.recording_count)}")
                get_active_speaker_if_needed(meeting.uuid, topic)
                check = za.delete_recordings(meeting.id)
                print(f"Check Status Code: {str(check)}")
                syslog(f"Check Status Code: {str(check)}")
                if check[1] == 204:
                    print("Status Code is 204 marking as downloaded")
                    syslog("Status Code is 204 marking as downloaded")
                    # update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting.uuid + "'"
                    update_sql = f"update meetings set downloaded = 1 where meeting_id = '{str(meeting.uuid)}'"
                    mysql_insert_update(update_sql)
                if check[1] == 404:
                    print("Status code is 404 marking as downloaded")
                    syslog("Status code is 404 marking as downloaded")
                    # update_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting.uuid + "'"
                    update_sql = f"update meetings set downloaded = 1 where meeting_id = '{str(meeting.uuid)}'"
                    mysql_insert_update(update_sql)


def get_list_of_recordings_from_email_list(group_list):
    # Purpose of this function is to insert recording info into zdl_database db for later processing
    recordings_lists = []
    for x in group_list['members']:
        email = x['email']
        print(f"Checking for recordings for user: {email}")
        syslog(f"Checking for recordings for user: {email}")
        recording_list = za.list_user_recordings(email)
        recordings_lists.append(recording_list)
        for meetings in recording_list['meetings']:
            meeting = zr(meetings)
            meeting = check_if_special(meeting)
            if meeting.type != 3:
                continue
            uuid_status = check_uuid(meeting.uuid)
            if not uuid_status:
                print('Inserting new meeting info for', meeting.topic)
                insert_new_meeting_info(meeting)
            try:
                for recordings in meetings['recording_files']:
                    recording = rf(recordings)
                    # status = recordings['status']
                    status = recording.status
                    if status == 'processing':
                        print(f"Recording still processing on Zoom {meeting.topic}")
                        syslog(f"Recording still processing on Zoom {meeting.topic}")
                        continue
                    # recording_id = recordings['id']
                    new_recording = check_for_recording_id(recording.id)
                    if not new_recording:
                        print(f"Inserting new recording info for {meeting.topic}")
                        syslog(f"Inserting new recording info for {meeting.topic}")
                        insert_new_recording_info(recordings)
            except KeyError:
                syslog(f"KeyError @ get_list_of_recordings_from_email_list")
                continue
    return recordings_lists


def check_uuid(uuid):
    # select_sql = "select id, meeting_id from meetings where meeting_id = '" + uuid + "'"
    select_sql = f"select * from meetings where meeting_id = '{uuid}'"
    result = mysql_select(select_sql)
    for x in result:
        m = Meetings(x)
        if m.meeting_id == uuid:
        # if x['meeting_id'] == uuid:
            return True
    return False


def insert_new_meeting_info(meetings):
    sql_time = meetings.start_time
    sql_time = datetime.fromisoformat(sql_time[:-1])
    sql_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    # insert_sql = "insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
    #              "start_time, timezone, duration, recording_count, share_url, modified) values ('" \
    #              + str(meetings.uuid) + cm + str(meetings.id) + cm + str(meetings.account_id) + \
    #              cm + str(meetings.host_id) + cm + str(meetings.topic) + cm + str(meetings.type) + \
    #              cm + sql_time + cm + str(meetings.timezone) + cm + str(meetings.duration) + \
    #              cm + str(meetings.recording_count) + cm + str(meetings.share_url) + cm + timestamp + "')"
    insert_sql = f"insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
                 f"start_time, timezone, duration, recording_count, share_url, modified) values (" \
                 f"'{str(meetings.uuid)}', '{str(meetings.id)}', '{str(meetings.account_id)}', " \
                 f"'{str(meetings.host_id)}', '{str(meetings.topic)}', '{str(meetings.type)}', " \
                 f"'{sql_time}', '{str(meetings.timezone)}', '{str(meetings.duration)}', " \
                 f"'{str(meetings.recording_count)}', '{str(meetings.share_url)}', '{timestamp}')"
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
    insert_sql = f"insert into recordings (status, recording_id, meeting_id, recording_start, recording_end," \
                 f" file_type, file_extension, file_size, play_url, download_url, recording_type, modified) " \
                 f"values ('{str(rec.status)}', '{str(rec.id)}', '{str(rec.meeting_id)}', '{start_time}', " \
                 f"'{end_time}', '{str(rec.file_type)}', '{str(rec.file_extension)}', '{str(rec.file_size)}', " \
                 f"'{str(rec.play_url)}', '{str(rec.download_url)}', '{str(rec.recording_type)}', '{timestamp}')"
    print(insert_sql)
    mysql_insert_update(insert_sql)


def check_for_recording_id(recording_id):
    # select_sql = "select recording_id from recordings where recording_id ='" + recording_id + "'"
    select_sql = f"select * from recordings where recording_id ='{recording_id}'"
    result = mysql_select(select_sql)
    for x in result:
        r = Recordings(x)
        if r.recording_id == recording_id:
        # if x['recording_id'] == recording_id:
            return True
    return False


def download_recording(zoom_name, download_url, r_type):
    dl_url = download_url
    sub_path = r_type
    filename = zoom_name
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
    # select_sql = "select id, meeting_id, download_url, recording_start, recording_type," \
    #              " file_type from recordings where downloaded is null;"
    select_sql = "select * from recordings where downloaded is null"
    result = mysql_select(select_sql)
    # print(result)
    for x in result:
        r = Recordings(x)
        # r_id = str(x['id'])
        # print(r_id)
        # m_id = str(x['meeting_id'])
        # r_type = x['recording_type']
        # download_url = str(x['download_url'])
        # start_time = str(x['recording_start'])
        # file_type = str(x['file_type'])
        # select_sql2 = "select topic from meetings where meeting_id ='" + m_id + "'"
        select_sql2 = f"select * from meetings where meeting_id ='{r.meeting_id}'"
        result2 = mysql_select(select_sql2)
        for y in result2:
            m = Meetings(y)
            # topic = y['topic']
            if not check_time_diff(r.id):
                print(m.topic)
                print(r.recording_type)
                # zoom_name = topic + space + start_time + dot + file_type.lower()
                zoom_name = f"{m.topic} {m.start_time}.{r.file_type.lower()}"
                check = download_recording(zoom_name, r.download_url, r.recording_type)
                if check is True:
                    update_to_downloaded(r.id)


def update_to_downloaded(r_id):
    # update_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
    update_sql = f"update recordings set downloaded = 1 where id = '{r_id}'"
    mysql_insert_update(update_sql)


def delete_recordings_from_zoom(recordings_list):
    for x in recordings_list:
        for meetings in x['meetings']:
            meeting = zr(meetings)
            # select_sql = "select downloaded from meetings where meeting_id = '" + str(meeting.id) + "'"
            select_sql = f"select downloaded from meetings where meeting_id = '{str(meeting.id)}'"
            result = mysql_select(select_sql)
            for y in result:
                if str(y['downloaded']) == '1':
                    check = za.delete_recordings(str(meeting.uuid))
                    if check is False:
                        print(f"ERROR!!! deleting {str(meeting.uuid)}")
                        syslog(f"ERROR!!! deleting {str(meeting.uuid)}")


def check_time_diff(r_id):
    # select_sql = "select recording_start, recording_end from recordings where id ='" + r_id + "'"
    select_sql = f"select * from recordings where id ='{r_id}'"
    result = mysql_select(select_sql)
    for x in result:
        r = Recordings(x)
        # start = str(x['recording_start'])
        # end = str(x['recording_end'])
        date_format_str = '%Y-%m-%d %H:%M:%S'
        start_time = datetime.strptime(str(r.recording_start), date_format_str)
        end_time = datetime.strptime(str(r.recording_end), date_format_str)
        diff = end_time - start_time
        diff_in_minutes = diff.total_seconds() / 60
        if diff_in_minutes < 10:
            # update_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
            update_sql = f"update recordings set downloaded = 1 where id = '{r_id}'"
            mysql_insert_update(update_sql)
            return True
        return False


def check_for_shared_screen_with_speaker_view(meeting_id):
    # select_sql = "select recording_type from recordings where meeting_id = '" + meeting_id + "';"
    select_sql = f"select * from recordings where meeting_id = '{meeting_id}'"
    result = mysql_select(select_sql)
    for x in result:
        r = Recordings(x)
        if r.recording_type == 'shared_screen_with_speaker_view':
        # if x['recording_type'] == 'shared_screen_with_speaker_view':
            return True
        else:
            continue
    return False


def move_active_speaker_to_upload_dir(meeting_id):
    # select_sql = "select topic from meetings where meeting_id = '" + meeting_id + "'"
    select_sql = f"select * from meetings where meeting_id = '{meeting_id}'"
    result = mysql_select(select_sql)
    # select_sql2 = "select recording_start from recordings where meeting_id = '" + meeting_id + "'"
    select_sql2 = f"select * from recordings where meeting_id = '{meeting_id}'"
    result2 = mysql_select(select_sql2)
    start_time = ''
    for y in result2:
        r = Recordings(y)
        start_time = r.recording_start
        # start_time = str(y['recording_start'])
    for x in result:
        m = Meetings(x)
        # topic = x['topic']
        # recording = topic + space + start_time + '.mp4'  # + space + 'active_speaker.mp4'
        recording = f"{m.topic} {start_time}.mp4"
        # path = home_path + 'active_speaker/' + recording
        path = f"{home_path}active_speaker/{recording}"
        path = str(path)
        check = exists(path)
        if check is True:
            # move_to = home_path + 'shared_screen_with_speaker_view/' + recording
            move_to = f"{home_path}shared_screen_with_speaker_view/{recording}"
            print(f"Moving Active Speaker to upload dir {m.topic}")
            syslog(f"Moving Active Speaker to upload dir {m.topic}")
            os.rename(path, move_to)
            return True
    return False


def main():
    print('Getting List of Zoom Accounts!')
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

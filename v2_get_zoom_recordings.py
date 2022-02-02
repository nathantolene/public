#!/usr/bin/python3

import json
import requests
from zoomus import ZoomClient
from datetime import date, datetime
import os
import mysql.connector
import zoom_auto_delete
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
home_path = os.environ.get('home_path')
#sub_path = os.environ.get('sub_path')
year = "2022"
day = "01"
month = "01"
convert_time = datetime.fromisoformat(year + "-" + month + '-' + day)
today = date.today()
today = today.strftime("%Y-%m-%dT%H:%M:%SZ")
client = ZoomClient(api_key, api_sec)
group_id = os.environ.get('zoom_group_id')
zdl_host = os.environ.get('zdl_host')
zdl_user = os.environ.get('zdl_user')
zdl_password = os.environ.get('zdl_password')
zdl_database = os.environ.get('zdl_database')
space = " "
dot = "."


def get_zoom_group_emails():
    group_list_response = client.group.list_members(groupid=group_id)
    group_list = json.loads(group_list_response.content)
    return group_list


def update_recording_count():
    group_list = get_zoom_group_emails()
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    for x in group_list['members']:
        email = x['email']
        recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        recording_list = json.loads(recording_list_response.content)
        for meetings in recording_list['meetings']:
            meetings_uuid = meetings['uuid']  # key to meeting id
            recording_count = meetings['recording_count']
            select_sql = "select recording_count from meetings where meeting_id ='" + meetings_uuid + "'"
            mycursor.execute(select_sql)
            myresult = mycursor.fetchall()
            for x in myresult:
                if not str(x['recording_count']) == recording_count:
                    select_sql = "update meetings set recording_count ='" \
                                 + str(recording_count) + "' where meeting_id ='" + meetings_uuid + "'"
                    mycursor.execute(select_sql)
                    mydb.commit()


def get_list_of_recordings_for_email():
    group_list = get_zoom_group_emails()
    for x in group_list['members']:
        #print(x)
        email = x['email']
        recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        recording_list = json.loads(recording_list_response.content)
        #print(recording_list)
        for meetings in recording_list['meetings']:
            meetings_uuid = meetings['uuid']  # key to meeting id
            uuid_status = check_uuid(meetings_uuid)
            meetings_zoom_number = meetings['id']
            account_id = meetings['account_id']
            host_id = meetings['host_id']
            topic = meetings['topic']
            topic = topic.replace("'", "_")
            #print('Topic ' + topic)
            meetings_type = meetings['type']
            #print('Meeintg_type ' + str(meetings_type))
            start_time = meetings['start_time']
            timezone = meetings['timezone']
            duration = meetings['duration']
            #print('Duration ' + str(duration))
            recording_count = meetings['recording_count']
            share_url = meetings['share_url']
            if not uuid_status:
                passer = [meetings_uuid, meetings_zoom_number, account_id, host_id, topic, meetings_type, start_time,
                          timezone, duration, recording_count, share_url]
                insert_new_meeting_info(passer)
            for recordings in meetings['recording_files']:
                status = recordings['status']
                if status == 'processing':
                    continue
                # duration_meeting = recordings['duration']
                # if duration_meeting <= 10:
                #    continue
                recording_id = recordings['id']
                meeting_id = recordings['meeting_id']
                recording_start = recordings['recording_start']
                recording_end = recordings['recording_end']
                file_type = recordings['file_type']
                file_extension = recordings['file_extension']
                file_size = recordings['file_size']
                try:
                    play_url = recordings['play_url']
                except KeyError:
                    play_url = 'TRANSCRIPT'
                    # print('No play_url it is a ' + file_type + ' file!')
                download_url = recordings['download_url']
                recording_type = recordings['recording_type']
                new_recording = check_for_recording_id(recording_id)
                if not new_recording:
                    passer = [status, recording_id, meeting_id, recording_start, recording_end, file_type, file_extension,
                              file_size, play_url, download_url, recording_type]
                    insert_new_recording_info(passer)
                #check_to_download(recording_id)
                #return recording_id


def check_uuid(uuid):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = 'select meeting_id from meetings'
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        if x['meeting_id'] == uuid:
            return True
    return False


def insert_new_meeting_info(passer):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    comma = "', '"
    mycursor = mydb.cursor(dictionary=True)
    sql_time = passer[6]
    sql_time = datetime.fromisoformat(sql_time[:-1])
    sql_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    select_sql = "insert into meetings (meeting_id, meetings_zoom_number, account_id, host_id, topic, meeting_type, " \
                 "start_time, timezone, duration, recording_count, share_url, modified) values ('" \
                 + str(passer[0]) + comma + str(passer[1]) + comma + str(passer[2]) + \
                 comma + str(passer[3]) + comma + str(passer[4]) + comma + str(passer[5]) + \
                 comma + sql_time + comma + str(passer[7]) + comma + str(passer[8]) + \
                 comma + str(passer[9]) + comma + str(passer[10]) + comma + timestamp + "')"
    # print(select_sql)
    mycursor.execute(select_sql)
    mydb.commit()


def insert_new_recording_info(passer):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    comma = "', '"
    mycursor = mydb.cursor(dictionary=True)
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    sql_time = passer[3]
    sql_time = datetime.fromisoformat(sql_time[:-1])
    start_time = sql_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = passer[4]
    end_time = datetime.fromisoformat(end_time[:-1])
    end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    select_sql = "insert into recordings (status, recording_id, meeting_id, recording_start, recording_end," \
                 " file_type, file_extension, file_size, play_url, download_url, recording_type, modified) " \
                 "values ( '" + str(passer[0]) + comma + str(passer[1]) + comma + str(passer[2]) + comma + \
                 start_time + comma + end_time + comma + str(passer[5]) + comma + str(passer[6]) + comma + \
                 str(passer[7]) + comma + str(passer[8]) + comma + str(passer[9]) + comma + str(
        passer[10]) + comma + timestamp + "')"
    # print(select_sql)
    mycursor.execute(select_sql)
    mydb.commit()


def check_for_recording_id(recording_id):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select recording_id from recordings where recording_id ='" + recording_id + "'"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        if x['recording_id'] == recording_id:
            return True
    return False


def download_recording(zoomname, download_url, r_type):
    dl_url = download_url
    sub_path = r_type
    filename = zoomname
    slash = '/'
    path = home_path + sub_path + slash
    path_exist = os.path.exists(path)
    print(dl_url)
    print(path)
    if not path_exist:
        os.makedirs(path)
    dl_path = os.path.join(path, filename)
    r = requests.get(dl_url, allow_redirects=True, stream=True)
    with requests.get(dl_url, allow_redirects=True, stream=True) as r, open(dl_path, "wb") as f:
        f.write(r.content)
    file_exist = os.path.exists(dl_path)
    if file_exist:
        return True


def check_db_and_download_all():
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    #select_sql = "select recordings.downloaded, recordings.id, recordings.download_url," \
    #             " recordings.recording_start, recordings.recording_type, recordings.file_type," \
    #             " meetings.topic from recordings, meetings where" \
    #             " recordings.downloaded is Null"
    select_sql = "select id, meeting_id, download_url, recording_start, recording_type," \
                 " file_type from recordings where downloaded is null;"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    #print(myresult)
    for x in myresult:
        r_id = str(x['id'])
        #print(r_id)
        m_id = str(x['meeting_id'])
        r_type = x['recording_type']
        download_url = str(x['download_url'])
        start_time = str(x['recording_start'])
        file_type = str(x['file_type'])
        select_sql2 = "select topic from meetings where meeting_id ='" + m_id + "'"
        #print(select_sql2)
        mycursor.execute(select_sql2)
        myselect = mycursor.fetchall()
        for y in myselect:
            topic = str(y['topic'])
            if not check_time_diff(r_id):
                print(topic)
                print(r_type)
                if r_type == 'audio_transcript':
                    zoomname = topic + space + start_time + ".vtt"
                    check = download_recording(zoomname, download_url, r_type)
                    print(zoomname)
                    if check:
                        update_to_downloaded(r_id)
                if r_type == 'shared_screen_with_speaker_view':
                    zoomname = topic + space + start_time + dot + file_type.lower()
                    check = download_recording(zoomname, download_url, r_type)
                    print(zoomname)
                    if check:
                        update_to_downloaded(r_id)
                if r_type == 'shared_screen_with_gallery_view':
                    zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
                    check = download_recording(zoomname, download_url, r_type)
                    print(zoomname)
                    if check:
                        update_to_downloaded(r_id)
                if r_type == 'TIMELINE' or r_type == 'timeline':
                    zoomname = topic + space + start_time + space + r_type + dot + file_type.lower()
                    check = download_recording(zoomname, download_url, r_type)
                    if check:
                        update_to_downloaded(r_id)
                if r_type == 'CHAT' or r_type == 'chat_file':
                    zoomname = topic + space + start_time + space + r_type + '.txt'
                    check = download_recording(zoomname, download_url, r_type)
                    print(zoomname)
                    if check:
                        update_to_downloaded(r_id)


def update_to_downloaded(r_id):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
    print(select_sql)
    mycursor.execute(select_sql)
    mydb.commit()


def delete_recordings_from_zoom():
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select id, meeting_id, recording_count from meetings where downloaded is null"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        zoom_meeting_id = x['meeting_id']
        meeting_id = str(x['meeting_id'])
        select_sql = "select downloaded from recordings where meeting_id = '" + meeting_id + "'"
        mycursor.execute(select_sql)
        myr = mycursor.fetchall()
        full_download = 0
        recording_count = x['recording_count']
        for x in myr:
            if x['downloaded'] is None:
                continue
            full_download = full_download + int(str(x['downloaded']))
        if full_download == recording_count:
            print('Full Downloaded: ' + str(full_download))
            print('Recording Count: ' + str(recording_count))
            check = client.recording.delete(meeting_id=zoom_meeting_id)
            print('Check Status Code: ' + str(check.status_code))
            if check.status_code == '204':
                select_sql = "update meetings set downloaded = 1 where meeting_id = '" + meeting_id + "'"
                mycursor.execute(select_sql)
                mydb.commit()


def check_time_diff(r_id):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select recording_start, recording_end from recordings where id ='" + r_id + "'"
    #print(select_sql)
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    #print(myresult)
    for x in myresult:
        start = str(x['recording_start'])
        #print(start)
        end = str(x['recording_end'])
        #print(end)
        date_format_str = '%Y-%m-%d %H:%M:%S'
        start_time = datetime.strptime(start, date_format_str)
        end_time = datetime.strptime(end, date_format_str)
        diff = end_time - start_time
        diff_in_minutes = diff.total_seconds() / 60
        #print(diff_in_minutes)
        if diff_in_minutes < 10:
            select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
            #print(select_sql)
            mycursor.execute(select_sql)
            mydb.commit()
            return True
        return False


def main():
    get_list_of_recordings_for_email()
    check_db_and_download_all()
    update_recording_count()
    delete_recordings_from_zoom()
    zoom_auto_delete.main()


if __name__ == "__main__":
    main()

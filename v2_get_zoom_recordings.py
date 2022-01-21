#!/usr/bin/python3

import json
import requests
from zoomus import ZoomClient
from datetime import date, datetime
from tqdm import tqdm
import sys
import re
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
home_path = os.environ.get('home_path')
sub_path = os.environ.get('sub_path')
year = "2021"
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
debug = 1


def debugger(name, var):
    if debug == 1:
        var = str(var)
        print(name + "=" + var)


def print_line_of_stars():
    print('*********************************************')


def get_zoom_group_emails():
    group_list_reponse = client.group.list_members(groupid=group_id)
    group_list = json.loads(group_list_reponse.content)
    for x in group_list['members']:
        email = x['email']
        #print(email)
        get_list_of_recordings_for_email(email)
        #return email


def get_list_of_recordings_for_email(email):
    recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
    recording_list = json.loads(recording_list_response.content)
    for meetings in recording_list['meetings']:
        meetings_uuid = meetings['uuid']  # key to meeting id
        uuid_status = check_uuid(meetings_uuid)
        meetings_zoom_number = meetings['id']
        account_id = meetings['account_id']
        host_id = meetings['host_id']
        topic = meetings['topic']
        topic = topic.replace("'", "_")
        meetings_type = meetings['type']
        start_time = meetings['start_time']
        timezone = meetings['timezone']
        duration = meetings['duration']
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
    #print(select_sql)
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
    select_sql = 'select recording_id from recordings'
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        if x['recording_id'] == recording_id:
            return True
    return False


def download_recording(passer):
    zoomname = passer[0]
    dl_url = passer[1]
    #file_size = passer[2]
    chunk_size = 1024
    filename = zoomname
    dl_path = os.path.join(home_path, sub_path, filename)
    r = requests.get(dl_url, allow_redirects=True, stream=True)
    with requests.get(dl_url, allow_redirects=True, stream=True) as r, open(dl_path, "wb") as f:
        f.write(r.content)
    return True


def check_to_download(recording_id):
    passer = str(recording_id)
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    #select recordings.meeting_id, meetings.topic from recordings, meetings where meetings.meeting_id = 'VTqOwmDOSCSaX2GQGSbsGQ==' limit 1;
    select_sql = "select recordings.downloaded, recordings.download_url, recordings.recording_start," \
                 " recordings.file_type, recordings.file_size, recordings.recording_type, meetings.topic from" \
                 " recordings, meetings where recordings.recording_id = '" + passer + "'"
    #print(select_sql)
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
#    zoomname = topic + ' ' + start_time + '.' + file_type.lower()
    #print(myresult)
    for x in myresult:
        if x['downloaded'] == 'None' and x['recording_type'] == 'shared_screen_with_speaker_view':
            file_type = x['file_type']
            zoomname = x['topic'] + ' ' + x['start_time'] + '.' + file_type.lower()
            file_size = x['file_size']
            dl_url = x['download_url']
            passing = [zoomname, dl_url, file_size]
            download_recording(passing)
            select_sql = "update recordings set downloaded = 1 where recording_id = " + passer
            mycursor.execute(select_sql)
            mydb.commit()
            #return True


def check_db_and_send_to_downloader():
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select recordings.downloaded, recordings.id, recordings.download_url," \
                 " recordings.recording_start, recordings.file_type," \
                 " recordings.file_size, meetings.topic from recordings, meetings where " \
                 " file_type = 'MP4' and recording_type = 'shared_screen_with_speaker_view' and" \
                 " meetings.meeting_id = recordings.meeting_id"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        downloaded = x['downloaded']
        r_id = str(x['id'])
        if downloaded is None:
            if check_time_diff(r_id):
                continue
            download_url = str(x['download_url'])
            start_time = str(x['recording_start'])
            file_size = str(x['file_size'])
            file_type = str(x['file_type'])
            zoomname = x['topic'] + ' ' + start_time + '.' + file_type.lower()
            #print(zoomname)
            passer = [zoomname, download_url]
            #print(passer)
            check = download_recording(passer)
            if check:
                select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
                mycursor.execute(select_sql)
                mydb.commit()


def check_db_and_download_transcripts():
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select recordings.downloaded, recordings.id, recordings.download_url, " \
                 "recordings.recording_start, recordings.file_type," \
                 " recordings.file_size, meetings.topic from recordings, meetings where" \
                 " recording_type = 'audio_transcript' and" \
                 " meetings.meeting_id = recordings.meeting_id"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        downloaded = x['downloaded']
        r_id = str(x['id'])
        if downloaded is None:
            download_url = str(x['download_url'])
            zoomname = str(x['topic']) + " " + str(x['recording_start']) + ".vtt"
            passer = [zoomname, download_url]
            check = download_recording(passer)
            if check:
                select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
                mycursor.execute(select_sql)
                mydb.commit()


def download_gallery_view(passer):
    zoomname = passer[0]
    dl_url = passer[1]
    #file_size = passer[2]
    chunk_size = 1024
    filename = zoomname
    gv = 'gv/'
    dl_path = os.path.join(home_path, sub_path, gv, filename)
    r = requests.get(dl_url, allow_redirects=True, stream=True)
    with requests.get(dl_url, allow_redirects=True, stream=True) as r, open(dl_path, "wb") as f:
        f.write(r.content)
    return True


def check_db_and_download_gallery_view():
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select recordings.downloaded, recordings.id, recordings.download_url," \
                 " recordings.recording_start, recordings.file_type," \
                 " recordings.file_size, meetings.topic from recordings, meetings where" \
                 " recording_type = 'shared_screen_with_gallery_view' and" \
                 " meetings.meeting_id = recordings.meeting_id"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        downloaded = x['downloaded']
        r_id = str(x['id'])
        if downloaded is None:
            if check_time_diff(r_id):
                continue
            download_url = str(x['download_url'])
            file_type = str(x['file_type'])
            zoomname = str(x['topic']) + " " + str(x['recording_start']) + ' gallery_view.' + file_type.lower()
            passer = [zoomname, download_url]
            check = download_gallery_view(passer)
            if check:
                select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
                mycursor.execute(select_sql)
                mydb.commit()


def delete_recordings_from_zoom():
    # client.recording.delete(meeting_id=meeting_id)
    # select id, meeting_id from meetings where downloaded is null;
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
            print('delete me! ' + meeting_id)
            client.recording.delete(meeting_id=zoom_meeting_id)
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
    select_sql = "select recording_start, recording_end from recordings where recording_id ='" + r_id + "'"
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        start = x['recording_start']
        end = x['recording_end']
        date_format_str = '%Y-%m-%d %H:%M:%S'
        start_time = datetime.strptime(start, date_format_str)
        end_time = datetime.strptime(end, date_format_str)
        diff = end_time - start_time
        diff_in_minutes = diff.total_seconds() / 60
        if diff_in_minutes < 10:
            select_sql = "update recordings set downloaded = 1 where id = '" + r_id + "'"
            mycursor.execute(select_sql)
            mydb.commit()
            return True
        return False


def main():
    get_zoom_group_emails()
    check_db_and_send_to_downloader()
    check_db_and_download_transcripts()
    check_db_and_download_gallery_view()
    delete_recordings_from_zoom()


if __name__ == "__main__":
    main()



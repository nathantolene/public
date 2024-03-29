#!/usr/bin/python3
# import requests
import json

from requests import post
import os
# import json
from json import loads as json_loads
# import syslog
from syslog import syslog
# import datetime
from datetime import datetime
# import yaml
from yaml import load as y_load
from yaml import FullLoader as y_FullLoader
# import mysql.connector
# import get_status_of_video_from_avideo_db
# import re
from re import search as re_search
# import shutil
from shutil import move as shutil_move
import sendemail_v3
import thk
from dotenv import load_dotenv

load_dotenv()

AVIDEO_HOST = os.environ.get('avideo_host')
AVIDEO_USER = os.environ.get('avideo_dbuser')
AVIDEO_PASSWORD = os.environ.get('avideo_dbpass')
AVIDEO_DATABASE = os.environ.get('avideo_db')
UTM_HOST = os.environ.get('host')
UTM_USER = os.environ.get('dbuser')
UTM_PASSWORD = os.environ.get('dbpass')
UTM_DATABASE = os.environ.get('db')
MYDIR = os.environ.get('mydir')
T_DIR = os.environ.get('transcripts_dir')
UPLOAD_FOLDER = os.environ.get('upload_folder')
UPLOAD_URL = os.environ.get('upload_url')
MOVING_TOTAL = os.environ.get('moving_total')
MOVING_TOTAL = int(MOVING_TOTAL)
# cat_ids = os.environ.get('cat_ids')
LOCATION = os.environ.get('db_email_location')
ENCODER_USER = os.environ.get('encoder_user')
ENCODER_PASS = os.environ.get('encoder_pass')
ENCODER_DB = os.environ.get('encoder_db')
ENCODER_HOST = os.environ.get('encoder_host')


def insert_into_utm_db(video_id, cat_id):
    nt_date = str(datetime.today().replace(microsecond=0))
    video_id = str(video_id)
    cat_id = str(cat_id)
    insert_sql = f"insert into videos (av_id, created, categories_id) values ('{video_id}', '{nt_date}', '{cat_id}')"
    # insert_sql = 'INSERT INTO videos (av_id, created, categories_id) VALUES (' + \
    #              video_id + ", '" + nt_date + "', " + cat_id + ')'
    thk.mysql_insert_update(insert_sql, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)


def upload(pass_file_name, cat_id, cat_des, cat_title):
    upload_file = open(os.path.join(MYDIR, pass_file_name), 'rb')
    upload_response = post(UPLOAD_URL,
                                    files={"upl": upload_file},
                                    params={"categories_id": cat_id,
                                            "description": cat_des,
                                            "title": cat_title
                                            }
                            )
    if upload_response.ok:
        # print("Upload completed successfully!")
        # print(upload_response.text)
        get_video_id = json_loads(upload_response.text)
        video_id = get_video_id['videos_id']
        syslog(f"Upload completed successfully!, Video id: {video_id}")
        insert_into_utm_db(video_id, cat_id)
    else:
        syslog(f"Something went wrong! {upload_response.text}")


def get_cat_id(cat_name):
    # print(f'{cat_name} @ 1st get_cat_id')
    # select_sql = 'SELECT id, name FROM categories'
    select_sql = f'SELECT id FROM categories where name like "{cat_name}"'
    result = thk.mysql_select(select_sql, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    # for x in result:
    #     if x['name'] == cat_name:
    #         cat_id = x['id']
    #         print(f'{cat_name} @ get_cat_id {cat_id} cat_id')
    #         return cat_id
    # print(result)
    try:
        result = result[0]['id']
    except IndexError:
        insert_cat_into_avideo_db(cat_name)
    else:
        return result


def get_number_of_files_in_upload_dir():
    files = os.listdir(MYDIR)
    return len(files)


def list_files_get_cat_id():
    moving = 1
    files = os.listdir(MYDIR)
    for file in files:
        if moving <= MOVING_TOTAL:
            full_path = MYDIR + file
            upload_path = UPLOAD_FOLDER + file
            if file.endswith(".mp4"):
                print(file)
                cat_name = file.split(" ")[0] + " " + file.split()[1] + " " + file.split()[2]
                # print(f'{cat_name} @ make cat name')
                key = get_cat_id(cat_name)
                # print(key)
                if key is None:
                    key = get_cat_id(cat_name)
                # print(key)
                cat_des = 'None'
                cat_title = get_cat_title(file, cat_name)
                upload(file, key, cat_des, cat_title)
                move_file(upload_path, full_path)
                moving += moving


def get_cat_title(file, cat_name):
    # print('filename:', file)
    match = re_search(r'\d{4}-\d{2}-\d{2}', file)
    dt = datetime.strptime(match.group(), '%Y-%m-%d').date()
    day_word = dt.strftime("%a")
    month_word = dt.strftime("%b")
    year = dt.strftime("%Y")
    day_num = dt.strftime('%d')
    end = day_word + " " + month_word + " " + day_num + " " + year
    cat_title = cat_name + " " + end
    # print("Title: " + cat_title)
    return cat_title


def move_file(upload_path, full_path):
    if os.path.exists(full_path + upload_path) is True:
        os.rename(full_path, 'dup')
        return
    syslog("Moving " + full_path + " to " + upload_path)
    os.rename(full_path, upload_path)


def insert_cat_into_avideo_db(name):
    # print(f'{name} @ insert')
    clean_name = name.replace(" ", "_")
    clean_name = clean_name.lower()
    # print(f'{clean_name} @ clean name')
    timestamp = str(datetime.today().replace(microsecond=0))
    # parser = '"'
    # insert_sql = 'INSERT INTO categories (name, clean_name, created, modified) values (' \
    #              + parser + name + parser + ', ' + parser + clean_name + parser + ',' + parser + timestamp + parser + ', ' \
    #              + parser + timestamp + parser + ')'
    insert_sql = f"insert into categories (name, clean_name, created, modified) values ('{name}', '{clean_name}', '{timestamp}', '{timestamp}')"
    thk.mysql_insert_update(insert_sql, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    syslog('Updated: ' + AVIDEO_DATABASE + ' with: ' + insert_sql)


def move_transcripts():
    files = os.listdir(T_DIR)
    for file in files:
        full_path = T_DIR + file
        if file.endswith(".vtt"):
            cat_name = file.split(" ", 2)[0] + " " + file.split()[1] + " " + file.split()[2]
            cat_title = get_cat_title(file, cat_name)
            # select_sql = "select status, filename from videos where title = '" + cat_title + "'"
            select_sql = f"select status, filename from videos where title = '{cat_title}'"
            result = thk.mysql_select(select_sql, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
            for x in result:
                if x['status'] == 'a':
                    trans_sub_path = x['filename']
                    avideo_path = '/nfs/web/AVideo/videos/'
                    add_to_name = '.en_US'
                    # upload_path = avideo_path + trans_sub_path + "/" + trans_sub_path + add_to_name + ".vtt"
                    upload_path = f"{avideo_path}{trans_sub_path}/{trans_sub_path}{add_to_name}.vtt"
                    shutil_move(full_path, upload_path)


def get_status_of_video_from_avideo_db(video_id):
    video_id = str(video_id)
    # print(video_id)
    # select_sql = 'select status from videos where id = ' + video_id
    select_sql = f"select status from videos where id = '{video_id}'"
    result = thk.mysql_select(select_sql, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    try:
        return result[0]['status']
    except IndexError:
        return 'e'
    # for x in result:
    #     status = x['status']
    #     return status


def update_status_of_video_in_utm_db(status, video_id):
    status = str(status)
    video_id = str(video_id)
    # update_sql = "update videos set status = '" + status + "' where av_id = '" + video_id + "'"
    update_sql = f"update videos set status = '{status}' where av_id = '{video_id}'"
    thk.mysql_insert_update(update_sql, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)


def get_video_id_to_check_status():
    select_ids_from_utm_db = "select av_id from videos"
    av_ids = thk.mysql_select(select_ids_from_utm_db, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)
    for x in av_ids:
        status = get_status_of_video_from_avideo_db(x['av_id'])
        update_status_of_video_in_utm_db(status, x['av_id'])


def delete_from_utm_videos_if_status_is_a(av_id):
    av_id = str(av_id)
    set_video_to_off_group(av_id)
    delete_sql = f"delete from videos where av_id = '{av_id}'"
    thk.mysql_insert_update(delete_sql, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)


def set_video_to_off_group(av_id):
    cat_id = get_cat_id_from_video_id(av_id)
    cat_name = get_cat_name(cat_id)
    result = find_off_videos_list(cat_name)
    syslog(f"set to off_group {result}")
    if result is True:
        add_video_to_off_group(av_id)


def add_email_to_db():
    for file in os.listdir(LOCATION):
        if file.endswith(".yaml"):
            location_file = os.path.join(LOCATION, file)
            with open(location_file, 'r') as yaml_file:
                email = y_load(yaml_file, Loader=y_FullLoader)
                send_to_address = email['send_to_address']
                cat = email['cat']
                cat_id = str(get_cat_id(cat))
                if cat_id is None:
                    cat_id = get_cat_id(cat)
                # insert_sql = "insert into email (name, email, cat) values ('" + send_to_address + "', '" + send_to_address + "', '" + cat_id + "')"
                insert_sql = f"insert into email (name, email, cat) values ('{send_to_address}', '{send_to_address}', '{cat_id}')"
                thk.mysql_insert_update(insert_sql, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)
                os.remove(location_file)


def add_video_to_off_group(video_id):
    off_group = '3'
    video_id = str(video_id)
    # insert_sql = "insert into videos_group_view (users_groups_id, videos_id) values (" + off_group + ", " + video_id + ")"
    insert_sql = f"insert into videos_group_view (users_group_id, videos_id) values ('{off_group}', '{video_id}')"
    response = thk.mysql_insert_update(insert_sql, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    syslog(response)


def find_off_videos_list(cat_name):
    # print(cat_name)
    # cat_name = cat_name[0]['name']
    select_sql = "select * from off_group"
    result = thk.mysql_select(select_sql, UTM_HOST, UTM_USER, UTM_PASSWORD, UTM_DATABASE)
    for x in result:
        title = x['title']
        # print(title)
        if cat_name == title:
            return True
    return False


def get_cat_name(cat_id):
    # cat_id = cat_id[0]['categories_id']
    # select_cat_name = "select name from categories where id = '" + str(cat_id) + "'"
    select_cat_name = f"select name from categories where id = '{str(cat_id)}'"
    syslog(select_cat_name)
    cat_name = thk.mysql_select(select_cat_name, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    cat_name = str(cat_name[0]['name'])
    return cat_name


def get_cat_id_from_video_id(video_id):
    # select_cat_id = "select categories_id from videos where id = '" + str(video_id) + "'"
    select_cat_id = f"select categories_id from videos where id = '{str(video_id)}'"
    syslog(select_cat_id)
    cat_id = thk.mysql_select(select_cat_id, AVIDEO_HOST, AVIDEO_USER, AVIDEO_PASSWORD, AVIDEO_DATABASE)
    cat_id = str(cat_id[0]['categories_id'])
    return cat_id


def check_encoders():
    select_sql = f'select id from encoder_queue'
    hosts = ENCODER_HOST.split(',')
    num_of_queued_recordings = 0
    for host in hosts:
        # print(host, ids)
        from_host_ids = thk.mysql_select(select_sql, host, ENCODER_USER, ENCODER_PASS, ENCODER_DB)
        # print(from_host_ids)
        num_of_queued_recordings = num_of_queued_recordings + len(from_host_ids)
    if num_of_queued_recordings <= 5:
        # print('Add video')
        return num_of_queued_recordings
    else:
        # print('Do not add video')
        return False


def get_a_file_to_upload():
    files = os.listdir(MYDIR)
    for file in files:
        if file.endswith('.mp4'):
            full_path = MYDIR + file
            upload_path = UPLOAD_FOLDER + file
            cat_name = file.split(" ")[0] + " " + file.split()[1] + " " + file.split()[2]
            key = get_cat_id(cat_name)
            if key is None:
                key = get_cat_id(cat_name)
            cat_des = 'None'
            cat_title = get_cat_title(file, cat_name)
            upload(file, key, cat_des, cat_title)
            move_file(upload_path, full_path)
            return


def main():
    queue_length = check_encoders()
    number_of_files_to_upload = get_number_of_files_in_upload_dir()
    if number_of_files_to_upload > 0:
        if queue_length is False:
            syslog('Queue is Full!')
        if queue_length is not False:
            # list_files_get_cat_id()
            while queue_length <= 5:
                syslog(f'Current Queue size: {queue_length}')
                get_a_file_to_upload()
                number_of_files_to_upload = get_number_of_files_in_upload_dir()
                if number_of_files_to_upload == 0:
                    queue_length = 6
                    syslog('No more files to upload')
                else:
                    queue_length += 1
    else:
        syslog('No files to upload')
    get_video_id_to_check_status()
    move_transcripts()
    add_email_to_db()
    sendemail_v3.main()


if __name__ == "__main__":
    main()
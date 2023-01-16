#!/usr/bin/python3
import requests
import os
import json
import syslog
import datetime
from datetime import datetime
import yaml
# import mysql.connector
# import get_status_of_video_from_avideo_db
import re
import shutil
import sendemail_v3
import thk
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('avideo_host')
user = os.environ.get('avideo_dbuser')
password = os.environ.get('avideo_dbpass')
database = os.environ.get('avideo_db')
utm_host = os.environ.get('host')
utm_user = os.environ.get('dbuser')
utm_password = os.environ.get('dbpass')
utm_database = os.environ.get('db')

mydir = os.environ.get('mydir')
t_dir = os.environ.get('transcripts_dir')
upload_folder = os.environ.get('upload_folder')
upload_url = os.environ.get('upload_url')
moving_total = os.environ.get('moving_total')
cat_ids = os.environ.get('cat_ids')
moving_total = int(moving_total)
location = os.environ.get('db_email_location')


def insert_into_utm_db(video_id, cat_id):
    nt_date = str(datetime.today().replace(microsecond=0))
    video_id = str(video_id)
    cat_id = str(cat_id)
    insert_sql = 'INSERT INTO videos (av_id, created, categories_id) VALUES (' + \
                 video_id + ", '" + nt_date + "', " + cat_id + ')'
    thk.mysql_insert_update(insert_sql, utm_host, utm_user, utm_password, utm_database)


def upload(pass_file_name, cat_id, cat_des, cat_title):
    upload_file = open(os.path.join(mydir, pass_file_name), 'rb')
    upload_response = requests.post(upload_url,
                                    files={"upl": upload_file},
                                    params={"categories_id": cat_id,
                                            "description": cat_des,
                                            "title": cat_title
                                            }
                                    )
    if upload_response.ok:
        print("Upload completed successfully!")
        print(upload_response.text)
        get_video_id = json.loads(upload_response.text)
        video_id = get_video_id['videos_id']
        insert_into_utm_db(video_id, cat_id)

    else:
        print("Something went wrong!")


def get_cat_id(cat_name):
    select_sql = 'SELECT id, name FROM categories'
    result = thk.mysql_select(select_sql, host, user, password, database)
    for x in result:
        if x['name'] == cat_name:
            cat_id = x['id']
            return cat_id
    insert_cat_into_avideo_db(cat_name)


def list_files_get_cat_id():
    moving = 1
    files = os.listdir(mydir)
    for file in files:
        if moving <= moving_total:
            full_path = mydir + file
            upload_path = upload_folder + file
            if file.endswith(".mp4"):
                print(file)
                cat_name = file.split(" ")[0] + " " + file.split()[1] + " " + file.split()[2]
                key = get_cat_id(cat_name)
                print(key)
                if key is None:
                    key = get_cat_id(cat_name)
                print(key)
                cat_des = 'None'
                cat_title = get_cat_title(file, cat_name)
                if check_for_special(file, upload_path, full_path):
                    moving = moving + 1
                    continue
                upload(file, key, cat_des, cat_title)
                move_file(upload_path, full_path)
                moving = moving + 1


def get_cat_number(cat_name):
    cat_dick = get_cat_id(cat_name)
    for key, value in cat_dick.items():
        if cat_name == value:
            print(key)
            return key
    insert_cat_into_avideo_db(cat_name)


def get_cat_des(file):
    cat_des = file.split(" ", 3)[3]
    try:
        view = cat_des.split("_", 4)[3]
        if view == "speaker":
            return cat_des
        else:
            return "gallery"
    except IndexError:
        return "gallery"


def get_cat_title(file, cat_name):
    print('filename:', file)
    match = re.search(r'\d{4}-\d{2}-\d{2}', file)
    dt = datetime.strptime(match.group(), '%Y-%m-%d').date()
    day_word = dt.strftime("%a")
    month_word = dt.strftime("%b")
    year = dt.strftime("%Y")
    day_num = dt.strftime('%d')
    end = day_word + " " + month_word + " " + day_num + " " + year
    cat_title = cat_name + " " + end
    print("Title: " + cat_title)
    return cat_title


def move_file(upload_path, full_path):
    syslog.syslog("Moving " + full_path + " to " + upload_path)
    os.rename(full_path, upload_path)


def check_for_special(file, upload_path, full_path):
    return False
    # if file.split(" ")[0] == "Sean":
    # key = "109"
    # cat_title = "MGT 350 Walker " + file.split(" ")[2] + " " + file.split(" ")[3]
    # cat_des = file.split("+")[1]
    # if cat_des != "active_speaker":
    #    move_file(upload_path, full_path)
    # else:
    #    upload(file, key, cat_des, cat_title)
    #    move_file(upload_path, full_path)
    # return "True"
    # if file.split(" ")[0] == "Louis":
    # key = "108"
    # day = file.replace(" ", "_")
    # day = day.replace("_", "+")
    # day = day.split("+")[8]
    # cat_des = file.split("_")[3]
    # if cat_des != "speaker":
    #    move_file(upload_path, full_path)
    # else:
    #    if day == "Fri":
    #        cat_title = "PSYC 340 Gamble " + file.split(" ")[2] + " " + file.split(" ")[3]
    #        upload(file, key, cat_des, cat_title)
    #        move_file(upload_path, full_path)
    #    if day == "Mon":
    #        cat_title = "PSYC 340 Gamble " + file.split(" ")[2] + " " + file.split(" ")[3]
    #        upload(file, key, cat_des, cat_title)
    #        cat_title = "PSYC 340 Gamble " + file.split(" ")[2] + " " + file.split(" ")[3]
    #        upload(file, key, cat_des, cat_title)
    #        move_file(upload_path, full_path)
    # return "True"
    # if file.split(" ")[0] == "Camden":
    #     match = re.search(r'\d{4}-\d{2}-\d{2}', file)
    #     dt = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #     day = dt.strftime("%a")
    #     if day == "Mon" or day == "Wed" or day == "Fri":
    #         key = '231'
    #         cat_title = get_cat_title(file, 'ENGL 112 Hacker')
    #         upload(file, key, 'None', cat_title)
    #         move_file(upload_path, full_path)
    #         return True
    #     if day == "Tue" or day == 'Thu':
    #         key = '232'
    #         cat_title = get_cat_title(file, "HIST 202 Camper")
    #         upload(file, key, 'None', cat_title)
    #         move_file(upload_path, full_path)
    #         return True
    # else:
    #     return


def insert_cat_into_avideo_db(name):
    clean_name = name.replace(" ", "_")
    clean_name = clean_name.lower()
    timestamp = str(datetime.today().replace(microsecond=0))
    parser = '"'
    insert_sql = 'INSERT INTO categories (name, clean_name, created, modified) values (' \
                 + parser + name + parser + ', ' + parser + clean_name + parser + ',' + parser + timestamp + parser + ', ' \
                 + parser + timestamp + parser + ')'
    thk.mysql_insert_update(insert_sql, host, user, password, database)
    syslog.syslog('Updated: ' + database + ' with: ' + insert_sql)


def move_transcripts():
    files = os.listdir(t_dir)
    for file in files:
        full_path = t_dir + file
        if file.endswith(".vtt"):
            cat_name = file.split(" ", 2)[0] + " " + file.split()[1] + " " + file.split()[2]
            cat_title = get_cat_title(file, cat_name)
            select_sql = "select status, filename from videos where title = '" + cat_title + "'"
            result = thk.mysql_select(select_sql, host, user, password, database)
            for x in result:
                if x['status'] == 'a':
                    trans_sub_path = x['filename']
                    avideo_path = '/nfs/web/AVideo/videos/'
                    add_to_name = '.en_US'
                    upload_path = avideo_path + trans_sub_path + "/" + trans_sub_path + add_to_name + ".vtt"
                    shutil.move(full_path, upload_path)


def get_status_of_video_from_avideo_db(video_id):
    video_id = str(video_id)
    select_sql = 'select status from videos where id = ' + video_id
    result = thk.mysql_select(select_sql, host, user, password, database)
    for x in result:
        status = x['status']
        return status


def update_status_of_video_in_utm_db(status, video_id):
    status = str(status)
    video_id = str(video_id)
    update_sql = "update videos set status = '" + status + "' where av_id = '" + video_id + "'"
    thk.mysql_insert_update(update_sql, utm_host, utm_user, utm_password, utm_database)


def get_video_id_to_check_status():
    select_ids_from_utm_db = "select av_id from videos"
    av_ids = thk.mysql_select(select_ids_from_utm_db, utm_host, utm_user, utm_password, utm_database)
    for x in av_ids:
        status = get_status_of_video_from_avideo_db(x['av_id'])
        update_status_of_video_in_utm_db(status, x['av_id'])


def delete_from_utm_videos_if_status_is_a(av_id):
    av_id = str(av_id)
    # this sets the video to the off group if listed in utm_add_on.off_group
    cat_id = get_cat_id_from_video_id(av_id)
    cat_name = get_cat_name(cat_id)
    result = find_off_videos_list(cat_name)
    if result is True:
        add_video_to_off_group(av_id)
    # end of set video to off group
    delete_sql = 'delete from videos where av_id = ' + av_id
    thk.mysql_insert_update(delete_sql, utm_host, utm_user, utm_password, utm_database)


def add_email_to_db():
    for file in os.listdir(location):
        if file.endswith(".yaml"):
            location_file = os.path.join(location, file)
            with open(location_file, 'r') as yaml_file:
                email = yaml.load(yaml_file, Loader=yaml.FullLoader)
                send_to_address = email['send_to_address']
                cat = email['cat']
                cat_id = str(get_cat_id(cat))
                if cat_id is None:
                    cat_id = get_cat_id(cat)
                insert_sql = "insert into email (name, email, cat) values ('" + send_to_address + "', '" + send_to_address + "', '" + cat_id + "')"
                thk.mysql_insert_update(insert_sql, utm_host, utm_user, utm_password, utm_database)
                os.remove(location_file)


def add_video_to_off_group(video_id):
    off_group = '3'
    video_id = str(video_id)
    insert_sql = "insert into videos_group_view (users_groups_id, videos_id) values (" + off_group + ", " + video_id + ")"
    response = thk.mysql_insert_update(insert_sql, host, user, password, database)
    print(response)


def find_off_videos_list(cat_name, video_id):
    select_sql = "select * from off_group"
    result = thk.mysql_select(select_sql, utm_host, utm_user, utm_password, utm_database)
    for x in result:
        title = x['title']
        if cat_name == title:
            return True
    return False


def get_cat_name(cat_id):
    cat_id = cat_id[0]['categories_id']
    select_cat_name = "select name from categories where id = '" + str(cat_id) + "'"
    print(select_cat_name)
    cat_name = thk.mysql_select(select_cat_name, host, user, password, database)
    return cat_name


def get_cat_id_from_video_id(video_id):
    select_cat_id = "select categories_id from videos where id = '" + str(video_id) + "'"
    print(select_cat_id)
    cat_id = thk.mysql_select(select_cat_id, host, user, password, database)
    return cat_id


def main():
    list_files_get_cat_id()
    get_video_id_to_check_status()
    move_transcripts()
    add_email_to_db()
    sendemail_v3.main()


if __name__ == "__main__":
    main()

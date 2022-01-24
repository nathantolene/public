#!/usr/bin/python3
import requests
import os
import json
import syslog
import datetime
from datetime import datetime
import mysql.connector
import get_status_of_video_from_avideo_db
import re
import shutil
import sendemail_v3
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


def insert_into_utm_db(video_id, cat_id):
    nt_date = str(datetime.today().replace(microsecond=0))
    video_id = str(video_id)
    cat_id = str(cat_id)
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = 'INSERT INTO videos (av_id, created, categories_id) VALUES (' + \
                 video_id + ", '" + nt_date + "', " + cat_id + ')'
    mycursor.execute(select_sql)
    mydb.commit()


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
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = 'SELECT id, name FROM categories'
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
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
            #print(file)
            if file.endswith(".mp4"):
                print(file)
                cat_name = file.split(" ")[0] + " " + file.split()[1] + " " + file.split()[2]
                #print(cat_name)
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
    #try:
    for key, value in cat_dick.items():
        if cat_name == value:
            print(key)
            return key
    insert_cat_into_avideo_db(cat_name)

    #except IndexError:
    #    print("Filename is not correct")
    #    return 1


def get_cat_des(file):
    # print(file)
    cat_des = file.split(" ", 3)[3]
    # print("Des: " + cat_des)
    try:
        view = cat_des.split("_", 4)[3]
        # print(view)
        if view == "speaker":
            # print(view)
            return cat_des
        else:
            # print("gallery")
            return "gallery"
    except IndexError:
        # print("gallery2")
        return "gallery"


def get_cat_title_LF(file, cat_name):
    try:
        cat_title = cat_name + " " + file.split(" ")[4] + " " + file.split()[5] + " " + file.split()[6]
        return cat_title
    except IndexError:
        return file


def get_cat_title(file, cat_name):
    print('filename:', file)
    #convert_title = file.split(" ")[3]
    #print('convert title: ', convert_title)
    #convert_month = convert_title.split("T")[0]
    #print('convert month: ', convert_month)
    #day_num = convert_month.split("-")[2]
    #year_num = convert_month.split("-")[0]
    # print(convert_month)
    match = re.search(r'\d{4}-\d{2}-\d{2}', file)
    dt = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #dt = convert_month
    #year, month, day = (int(x) for x in dt.split('-'))
    #ans = datetime.date(year, month, day)
    day_word = dt.strftime("%a")
    month_word = dt.strftime("%b")
    year = dt.strftime("%Y")
    day_num = dt.strftime('%d')
    end = day_word + " " + month_word + " " + day_num + " " + year
    # print(day_word + " " + month_word + " " + day_num + " " + year)
    cat_title = cat_name + " " + end
    print("Title: " + cat_title)
    return cat_title


def move_file(upload_path, full_path):
    syslog.syslog("Moving " + full_path + " to " + upload_path)
    os.rename(full_path, upload_path)


def check_for_special(file, upload_path, full_path):
    #if file.split(" ")[0] == "Sean":
        #key = "109"
        #cat_title = "MGT 350 Walker " + file.split(" ")[2] + " " + file.split(" ")[3]
        #cat_des = file.split("+")[1]
        #if cat_des != "active_speaker":
        #    move_file(upload_path, full_path)
        #else:
        #    upload(file, key, cat_des, cat_title)
        #    move_file(upload_path, full_path)
        #return "True"
    #if file.split(" ")[0] == "Louis":
        #key = "108"
        #day = file.replace(" ", "_")
        #day = day.replace("_", "+")
        #day = day.split("+")[8]
        #cat_des = file.split("_")[3]
        #if cat_des != "speaker":
        #    move_file(upload_path, full_path)
        #else:
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
        #return "True"
    if file.split(" ")[0] == "Camden":
        match = re.search(r'\d{4}-\d{2}-\d{2}', file)
        dt = datetime.strptime(match.group(), '%Y-%m-%d').date()
        day = dt.strftime("%a")
        if day == "Mon" or day == "Wed" or day == "Fri":
            key = '231'
            cat_title = get_cat_title(file, 'ENGL 112 Hacker')
            upload(file, key, 'None', cat_title)
            move_file(upload_path, full_path)
            return True
        if day == "Tue" or day == 'Thu':
            key = '232'
            cat_title = get_cat_title(file, "HIST 202 Camper")
            upload(file, key, 'None', cat_title)
            move_file(upload_path, full_path)
            return True
    else:
        return


def insert_cat_into_avideo_db(name):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        autocommit=True
    )
    clean_name = name.replace(" ", "_")
    clean_name = clean_name.lower()
    timestamp = str(datetime.today().replace(microsecond=0))
    parser = '"'
    mycursor = mydb.cursor()
    insert_sql = 'INSERT INTO categories (name, clean_name, created, modified) values (' \
        + parser + name + parser + ', ' + parser + clean_name + parser + ',' + parser + timestamp + parser + ', ' \
                 + parser + timestamp + parser + ')'
    #print(insert_sql)
    syslog.syslog('Updated: ' + database + ' with: ' + insert_sql)
    mycursor.execute(insert_sql)
    mydb.commit()
    #mycursor.execute(commit)


def move_transcripts():
    files = os.listdir(t_dir)
    for file in files:
        full_path = t_dir + file
        #print(file)
        if file.endswith(".vtt"):
            #print(file)
            cat_name = file.split(" ", 2)[0] + " " + file.split()[1] + " " + file.split()[2]
            #print(cat_name)
            cat_title = get_cat_title(file, cat_name)
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                autocommit=True
            )
            mycursor = mydb.cursor(dictionary=True)
            select_sql = "select status, filename from videos where title = '" + cat_title + "'"
            mycursor.execute(select_sql)
            myresult = mycursor.fetchall()
            for x in myresult:
                if x['status'] == 'a':
                    trans_sub_path = x['filename']
                    avideo_path = '/nfs/web/AVideo/videos/'
                    add_to_name = '.en_US'
                    upload_path = avideo_path + trans_sub_path + "/" + trans_sub_path + add_to_name + ".vtt"
                    shutil.move(full_path, upload_path)


def main():
    list_files_get_cat_id()
    get_status_of_video_from_avideo_db.get_video_id_to_check_status()
    move_transcripts()
    sendemail_v3.main()


if __name__ == "__main__":
    main()
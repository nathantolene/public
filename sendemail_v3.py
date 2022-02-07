#!/usr/bin/python3

import mysql.connector
import syslog
import get_status_of_video_from_avideo_db
import sys
import os
from dotenv import load_dotenv
load_dotenv()

host = os.environ.get('host')
user = os.environ.get('dbuser')
password = os.environ.get('dbpass')
database = os.environ.get('db')
avideo_host = os.environ.get('avideo_host')
avideo_user = os.environ.get('avideo_dbuser')
avideo_pass = os.environ.get('avideo_dbpass')
avideo_database = os.environ.get('avideo_db')
smtp_server = os.environ.get('smtp_server')
from_address = os.environ.get('from_address')
copy_nathan = os.environ.get('copy_nathan')
video_name = ''
class_name = ''
video_link = ''
video_duration = ''
video_description = ''
cat_id = ''

parser = '"'


def sendit(send_to_address, name):
    statement = 'sendemail -f ' + from_address + \
                ' -t ' + send_to_address + \
                ' -u ' + parser + video_name + parser + \
                ' -m ' + parser + "Dear " + name + "," + \
                "\nA new video was uploaded to dlcontent.utm.edu server for " + class_name + ".\n\n" \
                + "Video Name: " + video_name + '\n' \
                + "Video Link: " + video_link + \
                "\nVideo Duration: " + video_duration + \
                "\nVideo Description: " + video_description + \
                "\n\nThanks,\n\nUTM Distance Learning Content Server" + \
                parser + ' -s ' + smtp_server
    syslog.syslog(statement)
    # print(statement)
    os.system(statement)


def delete_one_off(email_id):
    email_id = str(email_id)
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mycursor = mydb.cursor()
    select_sql = "delete from email where ID = '" + email_id + "'"
    mycursor.execute(select_sql)
    mydb.commit()


def check_db_for_email_address(cat_id):
    cat_id = str(cat_id)
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("select * from email where cat = '" + cat_id + "'")
    email_address = mycursor.fetchall()
    for x in email_address:
        check_cat_id = x['cat']
        address_to_send = x['email']
        name_to_email = x['name']
        one_off = x['one_off']
        email_id = x['ID']
        print(email_id)
        print(one_off)
        if check_cat_id == cat_id:
            syslog.syslog('Email Address: ' + address_to_send)
            # print(row[2])
            sendit(address_to_send, name_to_email)
            if one_off == '1':
                delete_one_off(email_id)
    if copy_nathan == 'True':
        sendit('nathant@utm.edu', 'Automater')


def check_db_for_ready_videos():
    get_status_of_video_from_avideo_db.get_video_id_to_check_status()
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select av_id from videos where status = 'a'"
    mycursor.execute(select_sql)
    ready_to_send = mycursor.fetchall()
    for row in ready_to_send:
        #print(row['av_id'])
        av_id = row['av_id']
        get_video_info_for_email(av_id)
        get_status_of_video_from_avideo_db.delete_from_utm_videos_if_status_is_a(av_id)


def get_video_info_for_email(av_id):
    mydb = mysql.connector.connect(
        host=avideo_host,
        user=avideo_user,
        password=avideo_pass,
        database=avideo_database
    )
    mycursor = mydb.cursor(dictionary=True)
    av_id = str(av_id)
    #https://dlcontent.utm.edu/v/2129?channelName=Upload
    #select title, description, duration from videos where id = '2120
    select_sql = "select title, description, duration, categories_id from videos where id = '" + av_id + "'"
    mycursor.execute(select_sql)
    info = mycursor.fetchall()
    for row in info:
        global video_name, video_description, video_duration, class_name, video_link, cat_id
        video_name = row['title']
        video_description = row['description']
        video_duration = row['duration']
        class_name = row['title'].split(" ")
        class_name = class_name[0] + " " + class_name[1] + " " + class_name[2]
        domain = 'https://dlcontent.utm.edu/v/'
        channel = '?channelName=Upload'
        video_link = domain + av_id + channel
        cat_id = row['categories_id']
        check_db_for_email_address(cat_id)


def main():
    check_db_for_ready_videos()


if __name__ == "__main__":
    main()
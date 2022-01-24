#!/usr/bin/python3

import os
import datetime
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

utm_host = os.environ.get('host')
utm_user = os.environ.get('dbuser')
utm_password = os.environ.get('dbpass')
utm_database = os.environ.get('db')
avideo_host = os.environ.get('avideo_host')
avideo_user = os.environ.get('avideo_dbuser')
avideo_password = os.environ.get('avideo_dbpass')
avideo_database = os.environ.get('avideo_db')


def get_status_of_video_from_avideo_db(video_id):
    video_id = str(video_id)
    mydb = mysql.connector.connect(
        host=avideo_host,
        user=avideo_user,
        password=avideo_password,
        database=avideo_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = 'select status from videos where id = ' + video_id

    mycursor.execute(select_sql)
    status = mycursor.fetchall()
    #print(status)
    for x in status:
        status = x['status']
    return status


def update_status_of_video_in_utm_db(status, video_id):
    status = str(status)
    video_id = str(video_id)
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "update videos set status = '" + status + "' where av_id = '" + video_id + "'"
    #print(select_sql)
    mycursor.execute(select_sql)
    mydb.commit()


def get_video_id_to_check_status():
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = 'select * from videos'
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        #print(x['av_id'])
        status = get_status_of_video_from_avideo_db(x['av_id'])
        update_status_of_video_in_utm_db(status, x['av_id'])


def delete_from_utm_videos_if_status_is_a(av_id):
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    av_id = str(av_id)
    select_sql = 'delete from videos where av_id = ' + av_id
    mycursor.execute(select_sql)
    mydb.commit()



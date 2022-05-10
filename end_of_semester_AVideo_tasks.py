#!/usr/bin/python3

import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
host = os.environ.get('avideo_host')
user = os.environ.get('avideo_dbuser')
password = os.environ.get('avideo_dbpass')
database = os.environ.get('avideo_db')


def mysql_runner(sql):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = db.cursor(dictionary=True)
    print(sql)
    cursor.execute(sql)
    response = cursor.fetchall()
    db.commit()
    db.close()
    return response


def get_list_of_video_ids(not_this_cat_id):
    select_sql = "select id from videos where categories_id != " + not_this_cat_id
    response = mysql_runner(select_sql)
    return response


def change_cat_id_to_new_cat_id(new_cat_id, list_of_video_ids):
    for x in list_of_video_ids['id']:
        print(x)
        update_sql = "update videos set categories_id = " + new_cat_id + " where id  = " + x
        response = mysql_runner(update_sql)
        print(response)


def add_video_to_off_group(list_of_video_ids, off_group):
    for x in list_of_video_ids:
        insert_sql = "insert into videos_group_view (users_groups_id, videos_id) values (" + off_group + ", " + x + ")"
        response = mysql_runner(insert_sql)
        print(response)


def main():
    not_this_cat_id = input("What Cat ID should I exclude? ")
    list_of_video_ids = get_list_of_video_ids(not_this_cat_id)
    new_cat_id = input("What Cat ID are we changing to? ")
    change_cat_id_to_new_cat_id(new_cat_id, list_of_video_ids)
    off_group = input("What group should I add the videos to? ")
    add_video_to_off_group(list_of_video_ids, off_group)


if __name__ == "__main__":
    main()

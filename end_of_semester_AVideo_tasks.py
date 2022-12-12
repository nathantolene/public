#!/usr/bin/python3

import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
host = os.environ.get('avideo_host')
user = os.environ.get('avideo_dbuser')
password = os.environ.get('avideo_dbpass')
database = os.environ.get('avideo_db')


def mysql_runner(sql, sql_type):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = db.cursor(dictionary=True)
    print(sql)
    cursor.execute(sql)
    response = 'NOTHING'
    if sql_type == 's':
        response = cursor.fetchall()
    if sql_type == 'u' or sql_type == 'i':
        db.commit()
        response = ''
    db.close()
    return response


def get_list_of_video_ids():
    select_sql_w_exclude = "select id from videos where categories_id != 269 and categories_id != 110 and " \
                           "categories_id != 293;" # add more cat_ids to exclude
    # select_sql = "select id from videos where categories_id != " + not_this_cat_id
    response = mysql_runner(select_sql_w_exclude, 's')
    return response


def change_cat_id_to_new_cat_id(new_cat_id, list_of_video_ids):
    for x in list_of_video_ids:
        video_id = str(x['id'])
        update_sql = "update videos set categories_id = " + new_cat_id + " where id  = " + video_id
        response = mysql_runner(update_sql, 'u')
        print(response)


def add_video_to_off_group(list_of_video_ids, off_group):
    for x in list_of_video_ids:
        video_id = str(x['id'])
        insert_sql = "insert into videos_group_view (users_groups_id, videos_id) values (" + off_group + ", " + video_id + ")"
        response = mysql_runner(insert_sql, 'i')
        print(response)


def turn_on_list_of_videos(list_of_video_ids):
    for x in list_of_video_ids:
        video_id = str(x['id'])
        update_video_to_on = "update videos_group_view set users_group_id = 1 where videos_id = '" + video_id + "'"
        print(update_video_to_on)
        # result = mysql_runner(update_video_to_on, 'u')


def get_list_of_videos_by_instru_name():
    i_name = input('Instructor Name: ')
    select_videos = "select id from videos where title like '%" + i_name + "%';"
    print(select_videos)
    # result = mysql_runner(select_videos, 's')
    # return result


def main():
    # not_this_cat_id = input("What Cat ID should I exclude? ")
    list_of_video_ids = get_list_of_video_ids()
    new_cat_id = input("What Cat ID are we changing to? ")
    change_cat_id_to_new_cat_id(new_cat_id, list_of_video_ids)
    off_group = input("What group should I add the videos to? ")
    add_video_to_off_group(list_of_video_ids, off_group)


if __name__ == "__main__":
    main()

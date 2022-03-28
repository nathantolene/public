#!/usr/bin/python3

import sys
import mysql.connector
from shutil import copy2 as copier
from os.path import exists
import os
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('avideo_host')
user = os.environ.get('avideo_dbuser')
password = os.environ.get('avideo_dbpass')
database = os.environ.get('avideo_db')
download_folder = os.environ.get('download_folder')
avideo_root_videos = os.environ.get('avideo_root_videos')


def get_list_user_files(username, class_name):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select filename, title from videos where title like '" \
                 + username + "' and title like '" + class_name + "'"
    mycursor.execute(select_sql)
    response = mycursor.fetchall()
    return response


def copy_files_to_download_folder(files):
    for x in files:
        title = x['title']
        filename = x['filename']
        copy_move = input('Would you like to copy:(Y/N) ' + title)
        copy_move = copy_move.lower()
        if copy_move == 'y':
            copier(avideo_root_videos + filename, download_folder)
            file_exists = exists(download_folder + filename)
            if file_exists:
                print("Copied", title, "to", download_folder + filename)
            else:
                print("Something went wrong!")
                breaking = input("Would you like to Stop?(Y/N)")
                breaking = breaking.lower()
                if breaking == 'y':
                    sys.exit()
        else:
            continue


def main():
    username = input("User? ")
    class_name = input("Class Name? ")
    files = get_list_user_files(username, class_name)
    copy_files_to_download_folder(files)


if __name__ == "__main__":
    main()
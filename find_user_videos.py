#!/usr/bin/python3

import sys
import mysql.connector
import shutil
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
    select_sql = "select filename, title from videos where title like '%" \
                 + username + "%' and title like '%" + class_name + "%'"
    print(select_sql)
    mycursor.execute(select_sql)
    response = mycursor.fetchall()
    return response


def copy_files_to_download_folder(files, username):
    gogo = input('Would you like to copy all files for(Y/N) ' + username + " ")
    gogo = gogo.lower()
    if gogo == 'y':
        for x in files:
            title = x['title']
            directory = x['filename']
            username = username + "/"
            shutil.copytree(avideo_root_videos + directory, download_folder + username + directory)
            file_exists = exists(download_folder + username + directory)
            if file_exists:
                print("Copied", title, "to", download_folder + username + directory)
            else:
                print("Something went wrong!")
                breaking = input("Would you like to Stop?(Y/N)")
                breaking = breaking.lower()
                if breaking == 'y':
                    sys.exit()
    if gogo == 'n':
        for x in files:
            title = x['title']
            directory = x['filename']
            username = username + "/"
            copy_move = input('Would you like to copy:(Y/N) ' + title + " ")
            copy_move = copy_move.lower()
            if copy_move == 'y':
                shutil.copytree(avideo_root_videos + directory, download_folder + username + directory)
                file_exists = exists(download_folder + username + directory)
                if file_exists:
                    print("Copied", title, "to", download_folder + username + directory)
                else:
                    print("Something went wrong!")
                    breaking = input("Would you like to Stop?(Y/N)")
                    breaking = breaking.lower()
                    if breaking == 'y':
                        sys.exit()
            else:
                continue


def create_symlink_to_files(files, username):
    for x in files:
        title = x['title']
        directory = x['filename']
        #os.symlink(avideo_root_videos + directory, os.path.join(download_folder, os.path.dirname(avideo_root_videos)))
        new_path = download_folder + username + "/" + title + directory
        isExist = os.path.exists(new_path)
        if not isExist:
            os.makedirs(new_path)
        os.symlink(avideo_root_videos + directory, new_path)


def main():
    username = input("User? ")
    class_name = input("Class Name? ")
    files = get_list_user_files(username, class_name)
    # copy_files_to_download_folder(files, username)
    create_symlink_to_files(files, username)


if __name__ == "__main__":
    main()
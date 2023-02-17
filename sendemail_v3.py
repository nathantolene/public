#!/usr/bin/python3

import mysql.connector
import yaml
import syslog
# import get_status_of_video_from_avideo_db
# from upload_to_avideo import get_status_of_video_from_avideo_db
# from upload_to_avideo import delete_from_utm_videos_if_status_is_a
# from upload_to_avideo import get_video_id_to_check_status
# import sys
import os
from dotenv import load_dotenv

load_dotenv()

UTM_HOST = os.environ.get('host')
UTM_USER = os.environ.get('dbuser')
UTM_PASS = os.environ.get('dbpass')
UTM_DB = os.environ.get('db')
AV_HOST = os.environ.get('avideo_host')
AV_USER = os.environ.get('avideo_dbuser')
AV_PASS = os.environ.get('avideo_dbpass')
AV_DB = os.environ.get('avideo_db')
SMTP_SERVER = os.environ.get('smtp_server')
FROM_ADDRESS = os.environ.get('from_address')
COPY_ADMIN = os.environ.get('copy_nathan')
LOCATION = os.environ.get('location')


# video_name = ''
# class_name = ''
# video_link = ''
# video_duration = ''
# video_description = ''
# cat_id = ''
# parser = '"'


class UtmAddOnDB:
    class Videos:
        def __init__(self, x):
            self.id = x['id']
            self.av_id = x['av_id']
            self.status = x['status']
            self.categories_id = x['categories_id']

    class Email:
        def __init__(self, x):
            self.id = x['ID']
            self.name = x['name']
            self.email = x['email']
            self.category = x['cat']
            self.one_off = x['one_off']

    class SendEmail:
        def __init__(self, x):
            self.id = x['id']
            self.send_to = x['send_to']
            self.subject = x['subject']
            self.body = x['body']

    class OffGroup:
        def __init__(self, x):
            self.id = x['id']
            self.title = x['title']
            self.off_group = '3'


class AVideoDB:
    class Videos:
        def __init__(self, x):
            self.name = x['title']
            self.description = x['description']
            self.duration = x['duration']
            self.categories_id = x['categories_id']
            self.class_name = x['title'].split(" ")
            self.class_name = f"{self.class_name[0]} {self.class_name[1]} {self.class_name[2]}"
            self.domain = 'https://dlcontent.utm.edu/v/'
            self.channel = '?channelName=Upload'
            self.link = ""


def mysql_insert_update_utm(select_sql):
    db = mysql.connector.connect(
        host=UTM_HOST,
        user=UTM_USER,
        password=UTM_PASS,
        database=UTM_DB
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    db.commit()
    db.close()


def mysql_select_utm(select_sql):
    db = mysql.connector.connect(
        host=UTM_HOST,
        user=UTM_USER,
        password=UTM_PASS,
        database=UTM_DB
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    result = cursor.fetchall()
    db.close()
    return result


def mysql_insert_update_avideo(select_sql):
    db = mysql.connector.connect(
        host=AV_HOST,
        user=AV_USER,
        password=AV_PASS,
        database=AV_DB
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    db.commit()
    db.close()


def mysql_select_avideo(select_sql):
    db = mysql.connector.connect(
        host=AV_HOST,
        user=AV_USER,
        password=AV_PASS,
        database=AV_DB
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    result = cursor.fetchall()
    db.close()
    return result


def email_from_db():
    # mydb = mysql.connector.connect(
    #     host=host,
    #     user=user,
    #     password=password,
    #     database=database
    # )
    # mycursor = mydb.cursor(dictionary=True)
    select_sql = "select * from send_email"
    # mycursor.execute(select_sql)
    # result = mycursor.fetchall()
    result = mysql_select_utm(select_sql)
    for x in result:
        email = UtmAddOnDB.SendEmail(x)
        send_email = f'sendemail ' \
                     f'-f {FROM_ADDRESS} ' \
                     f'-t {email.send_to} ' \
                     f'-u "{email.subject}" ' \
                     f'-m "{email.body}" ' \
                     f'-s {SMTP_SERVER}'
        syslog.syslog(send_email)
        os.system(send_email)
        delete_sql = f"delete from send_email where id = '{str(email.id)}'"
        mysql_insert_update_utm(delete_sql)
        # mycursor.execute(select_sql)
        # mydb.commit()
        # mydb.close()


def find_files_to_email():
    for file in os.listdir(LOCATION):
        if file.endswith(".yaml"):
            location_file = os.path.join(LOCATION, file)
            with open(location_file, 'r') as yaml_file:
                email = yaml.load(yaml_file, Loader=yaml.FullLoader)
                # print(email['body'])
                body = email['body']
                send_to_address = email['send_to_address']
                subject = email['subject']
                # send_email = 'sendemail -f ' + from_address + \
                #              ' -t ' + send_to_address + \
                #              ' -u ' + parser + subject + parser + \
                #              ' -m ' + parser + body + parser + ' -s ' + smtp_server
                send_email = f"sendemail" \
                             f" -f {FROM_ADDRESS}" \
                             f" -t {send_to_address}" \
                             f" -u '{subject}'" \
                             f" -m '{body}'" \
                             f" -s {SMTP_SERVER}'"
                if COPY_ADMIN == 'True':
                    send_email = f"{send_email} -bcc nathant@utm.edu"
                syslog.syslog(send_email)
                os.system(send_email)
                os.remove(location_file)


def sendit(email, video):
    # statement = 'sendemail -f ' + from_address + \
    #             ' -t ' + send_to_address + \
    #             ' -u ' + parser + video_name + parser + \
    #             ' -m ' + parser + "Dear " + name + "," + \
    #             "\nA new video was uploaded to dlcontent.utm.edu server for " + class_name + ".\n\n" \
    #             + "Video Name: " + video_name + '\n' \
    #             + "Video Link: " + video_link + \
    #             "\nVideo Duration: " + video_duration + \
    #             "\nVideo Description: " + video_description + \
    #             "\n\nThanks,\n\nUTM Distance Learning Content Server" + \
    #             parser + ' -s ' + smtp_server
    body = f"Dear {email.name},\n" \
           f"A new video was uploaded to dlcontent.utm.edu server for {video.class_name}.\n\n" \
           f"Video Name: {video.name}\n" \
           f"Video Link: {video.link}\n" \
           f"Video Duration: {video.duration}\n" \
           f"\nThanks,\n" \
           f"\nUTM Distance Learning Content Server"
    statement = f"sendemail -f {FROM_ADDRESS} -t {email.email} -u '{video.name}' " \
                f"-m '{body}' -s {SMTP_SERVER}"
    if COPY_ADMIN == 'True':
        statement = f"{statement} -bcc nathant@utm.edu"
    syslog.syslog(statement)
    # print(statement)
    os.system(statement)


def delete_one_off(email_id):
    email_id = str(email_id)
    # mydb = mysql.connector.connect(
    #     host=host,
    #     user=user,
    #     password=password,
    #     database=database
    # )
    # mycursor = mydb.cursor()
    delete_sql = f"delete from email where ID = '{email_id}'"
    mysql_insert_update_utm(delete_sql)
    # mycursor.execute(select_sql)
    # mydb.commit()


def check_db_for_email_address(video):
    # cat_id = str(cat_id)
    # mydb = mysql.connector.connect(
    #     host=host,
    #     user=user,
    #     password=password,
    #     database=database
    # )
    # mycursor = mydb.cursor(dictionary=True)
    select_sql = f"select * from email where cat = '{video.categories_id}'"
    email_address = mysql_select_utm(select_sql)
    # mycursor.execute("select * from email where cat = '" + cat_id + "'")
    # email_address = mycursor.fetchall()
    for x in email_address:
        email = UtmAddOnDB.Email(x)
        # check_cat_id = x['cat']
        # address_to_send = x['email']
        # name_to_email = x['name']
        # one_off = x['one_off']
        # email_id = x['ID']
        # print(email_id)
        # print(one_off)
        # if check_cat_id == cat_id:
        if email.category == video.categories_id:
            syslog.syslog(f'Email Address: {email.email}')
            # print(row[2])
            sendit(email, video)
            if email.one_off == '1':
                delete_one_off(email.id)
    # if copy_nathan == 'True':
    #     sendit('nathant@utm.edu', 'Automater')


def check_db_for_ready_videos():
    get_video_id_to_check_status()
    # mydb = mysql.connector.connect(
    #     host=host,
    #     user=user,
    #     password=password,
    #     database=database
    # )
    # mycursor = mydb.cursor(dictionary=True)
    # select_sql = "select av_id from videos where status = 'a'"
    select_sql = "select * from videos where status = 'a'"
    ready_to_send = mysql_select_utm(select_sql)
    # mycursor.execute(select_sql)
    # ready_to_send = mycursor.fetchall()
    for row in ready_to_send:
        video = UtmAddOnDB.Videos(row)
        # av_id = row['av_id']
        # av_id = video.av_id
        get_video_info_for_email(video.av_id)
        delete_from_utm_videos_if_status_is_a(video.av_id)


def get_video_info_for_email(av_id):
    # mydb = mysql.connector.connect(
    #     host=avideo_host,
    #     user=avideo_user,
    #     password=avideo_pass,
    #     database=avideo_database
    # )
    # mycursor = mydb.cursor(dictionary=True)
    av_id = str(av_id)
    select_sql = f"select title, description, duration, categories_id from videos where id = '{av_id}'"
    # mycursor.execute(select_sql)
    info = mysql_select_avideo(select_sql)
    # info = mycursor.fetchall()
    for row in info:
        video = AVideoDB.Videos(row)
        # global video_name, video_description, video_duration, class_name, video_link, cat_id
        # video_name = row['title']
        # video_name = video.name
        # video_description = row['description']
        # video_description = video.description
        # video_duration = row['duration']
        # video_duration = video.duration
        # class_name = row['title'].split(" ")
        # class_name = class_name[0] + " " + class_name[1] + " " + class_name[2]
        # class_name = video.class_name
        # domain = 'https://dlcontent.utm.edu/v/'
        # domain = video.domain
        # channel = '?channelName=Upload'
        # channel = video.channel
        # video_link = domain + av_id + channel
        video.link = f"{video.domain}{av_id}{video.channel}"
        # video_link = f"{domain}{av_id}{channel}"
        # cat_id = row['categories_id']
        # cat_id = video.categories_id
        check_db_for_email_address(video)


def delete_from_utm_videos_if_status_is_a(av_id):
    av_id = str(av_id)
    set_video_to_off_group(av_id)
    delete_sql = f"delete from videos where av_id = '{av_id}'"
    mysql_insert_update_utm(delete_sql)


def get_video_id_to_check_status():
    select_ids_from_utm_db = "select av_id from videos"
    av_ids = mysql_select_utm(select_ids_from_utm_db)
    for x in av_ids:
        status = get_status_of_video_from_avideo_db(x['av_id'])
        update_status_of_video_in_utm_db(status, x['av_id'])


def get_status_of_video_from_avideo_db(video_id):
    video_id = str(video_id)
    # select_sql = 'select status from videos where id = ' + video_id
    select_sql = f"select status from videos where id = '{video_id}'"
    result = mysql_select_avideo(select_sql)
    print(result)
    return result[0]['status']


def update_status_of_video_in_utm_db(status, video_id):
    status = str(status)
    video_id = str(video_id)
    update_sql = f"update videos set status = '{status}' where av_id = '{video_id}'"
    mysql_insert_update_utm(update_sql)


def set_video_to_off_group(av_id):
    cat_id = get_cat_id_from_video_id(av_id)
    cat_name = get_cat_name(cat_id)
    result = find_off_videos_list(cat_name)
    # syslog(f"set to off_group {result}")
    if result is True:
        add_video_to_off_group(av_id)


def get_cat_id_from_video_id(video_id):
    # select_cat_id = "select categories_id from videos where id = '" + str(video_id) + "'"
    select_cat_id = f"select categories_id from videos where id = '{str(video_id)}'"
    # syslog(select_cat_id)
    cat_id = mysql_select_avideo(select_cat_id)
    cat_id = str(cat_id[0]['categories_id'])
    return cat_id


def get_cat_name(cat_id):
    # cat_id = cat_id[0]['categories_id']
    # select_cat_name = "select name from categories where id = '" + str(cat_id) + "'"
    select_cat_name = f"select name from categories where id = '{str(cat_id)}'"
    # syslog(select_cat_name)
    cat_name = mysql_select_avideo(select_cat_name)
    cat_name = str(cat_name[0]['name'])
    return cat_name


def find_off_videos_list(cat_name):
    # print(cat_name)
    # cat_name = cat_name[0]['name']
    select_sql = "select * from off_group"
    result = mysql_select_utm(select_sql)
    for x in result:
        # title = x['title']
        off_group = UtmAddOnDB.OffGroup(x)
        # print(title)
        if cat_name == off_group.title:
            return True
    return False


def add_video_to_off_group(video_id):
    off_group = '3'
    video_id = str(video_id)
    # insert_sql =
    # "insert into videos_group_view (users_groups_id, videos_id) values (" + off_group + ", " + video_id + ")"
    insert_sql = f"insert into videos_group_view (users_groups_id, videos_id) values ('{off_group}', '{video_id}')"
    mysql_insert_update_avideo(insert_sql)
    # syslog(response)


def main():
    check_db_for_ready_videos()
    email_from_db()
    find_files_to_email()


if __name__ == "__main__":
    main()

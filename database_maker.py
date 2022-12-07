import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.environ.get('zdl_host')
db_user = os.environ.get('zdl_user')
db_pass = os.environ.get('zdl_password')
db = os.environ.get('classes_db')


def mysql_select(select_sql):
    database = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db
    )
    cursor = database.cursor(dictionary=True)
    cursor.execute(select_sql)
    response = cursor.fetchall()
    database.close()
    return response


def mysql_insert(insert_sql):
    database = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db
    )
    cursor = database.cursor(dictionary=True)
    cursor.execute(insert_sql)
    database.commit()
    database.close()
    if cursor.lastrowid is not None:
        return cursor.lastrowid


def make_db_classes_tables():
    # make tables for classes database
    make_google_events_table = "create table google_events(" \
                               "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                               "event_id VARCHAR(100) NOT NULL," \
                               "start_time DATETIME," \
                               "end_time DATETIME, " \
                               "start_tz varchar(32)," \
                               "end_tz varchar(32)," \
                               "summary varchar(255)," \
                               "description varchar(255)," \
                               "location TEXT," \
                               "recurringEventId varchar(255)," \
                               "recurrence varchar(255), " \
                               "FK_g_event INT," \
                               "crn varchar(10), " \
                                "im varchar(10), " \
                               "hs varchar(255)," \
                               "email_link MEDIUMTEXT," \
                               "email_record MEDIUMTEXT," \
                               "dates mediumtext, " \
                               "not_dl boolean" \
                               ")"
    mysql_insert(make_google_events_table)
    make_google_events_master_table = "create table google_events_master(" \
                                      "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                                      "event_id VARCHAR(100)," \
                                      "start_time DATETIME," \
                                      "end_time DATETIME, " \
                                      "start_tz varchar(32)," \
                                      "end_tz varchar(32)," \
                                      "summary varchar(255)," \
                                      "description MEDIUMTEXT," \
                                      "location TEXT," \
                                      "recurringEventId varchar(255)," \
                                      "recurrence varchar(255), " \
                                      "attendees MEDIUMTEXT" \
                                      ")"
    mysql_insert(make_google_events_master_table)
    make_attendees_table = "create table attendees(" \
                           "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY," \
                           "email text," \
                           "displayName text," \
                           "organizer varchar(16)," \
                           "self varchar(16), " \
                           "resource varchar(16)," \
                           "responseStatus varchar(16)," \
                           "FK_g_event INT, " \
                           "im varchar(10), " \
                           "not_dl boolean"\
                           ")"
    mysql_insert(make_attendees_table)
    add_foreign_keys_attendees = "alter table attendees ADD FOREIGN KEY (FK_g_event) REFERENCES google_events_master (id);"
    mysql_insert(add_foreign_keys_attendees)
    add_foreign_keys_g_events = "alter table google_events add foreign key (FK_g_event) references google_events_master (id)"
    mysql_insert(add_foreign_keys_g_events)


def drop_classes_tables():
    drop_attendees = "drop table attendees;"
    mysql_insert(drop_attendees)
    drop_google_events = "drop table google_events;"
    mysql_insert(drop_google_events)
    drop_google_events_master = "drop table google_events_master;"
    mysql_insert(drop_google_events_master)


def make_rooms_tables():
    insert_sql = "create table rooms (" \
                 "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " \
                 "building varchar(100) not null, " \
                 "code varchar(10), " \
                 "displayName varchar(100), " \
                 "email varchar(700)," \
                 "room varchar(255), " \
                 "room_type varchar(255), " \
                 "zr_name varchar(255), " \
                 "zr_id varchar(255)" \
                 ")"
    mysql_insert(insert_sql)


def make_monthly_report_table():
    make_table = "create table zoom_reports (" \
                 "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " \
                 "uuid varchar(255), " \
                 "zoom_id varchar(255), " \
                 "meeting_type varchar(255), " \
                 "topic varchar(255), " \
                 "user_name varchar(255), " \
                 "user_email varchar(255), " \
                 "start_time varchar(255), " \
                 "end_time varchar(255), " \
                 "duration int, " \
                 "total_minutes int," \
                 "participants_count int," \
                 "dept varchar(255), " \
                 "source varchar(255)" \
                 ")"
    mysql_insert(make_table)
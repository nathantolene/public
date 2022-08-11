#!/usr/bin/python3

#from create_zoom_meeting import create_zoom_meeting
import os
import datetime
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
changer = 0
# all fields "ID, PTRM, CRN, SUBJ, CRS, SEC, IM, TITLE, CRHRS, MTWRFS, TIME, INSTRUCTOR, ENRL, SITE, Center Room #, Main Campus Rm #,
# Off Campus School, Share link with student, Note"


def mysql_select(sql):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    my_database.close()
    return my_result


def mysql_update(sql):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    my_cursor.execute(sql)
    my_database.commit()
    my_database.close()


def find_duplicates():
    select_sql = "select " \
                 "SUBJ, count(SUBJ), " \
                 "CRS, count(CRS), " \
                 "TITLE, count(TITLE), " \
                 "MTWRFS, count(MTWRFS), " \
                 "TIME, count(TIME), " \
                 "INSTRUCTOR, count(INSTRUCTOR) " \
                 "from importer " \
                 "group by " \
                 "SUBJ , " \
                 "CRS , " \
                 "TITLE , " \
                 "MTWRFS , " \
                 "TIME , " \
                 "INSTRUCTOR " \
                 "having count(SUBJ) > 1 " \
                 "and count(CRS) > 1 " \
                 "and count(TITLE) > 1 " \
                 "and count(MTWRFS) > 1 " \
                 "and count(TIME) >1 " \
                 "and count(INSTRUCTOR) > 1;"
    #print(select_sql)
    result = mysql_select(select_sql)
    #print(result)
    for x in result:
        #print(x)
        SUBJ = x['SUBJ']
        CRS = x['CRS']
        TITLE = x['TITLE']
        INSTRUCTOR = x['INSTRUCTOR']
        select_sql = "select ID from importer where SUBJ ='" + SUBJ + "' and CRS = '" + CRS + "' and TITLE = '" + TITLE + "' and INSTRUCTOR = '" + INSTRUCTOR + "'"
        repeater = mysql_select(select_sql)
        get_classes(repeater)
        print('***')


def get_classes(IDS):
    #print(IDS)
    ID1 = str(IDS[0]['ID'])
    #print(ID1)
    select_sql = "SELECT `SUBJ`, `CRS`,`TITLE`, `MTWRFS`, `TIME`, `INSTRUCTOR`, `SITE`, `Center Room #`, `Main Campus Rm #`, `Off Campus School`, `ID` FROM `importer` WHERE ID = '" + ID1 + "';"
    result = mysql_select(select_sql)
    site = result[0]['SITE']
    room = result[0]['Center Room #']
    if site != 'Online Crse':
        if room != "TBA":
            subj = result[0]['SUBJ']
            crs = result[0]['CRS']
            name = result[0]['INSTRUCTOR']
            name = name.split(" ")
            name = name[0]
            print(subj, crs, name)
            # send info to zoom_info
            zoom_info_maker(subj, crs, name)
            #print(result[0]['SUBJ'], result[0]['CRS'], result[0]['TITLE'], result[0]['INSTRUCTOR'], result[0]['MTWRFS'], result[0]['TIME'], result[0]['ID'])
            for x in IDS:
                ID = str(x['ID'])
                select_sql = "SELECT `SUBJ`, `CRS`,`TITLE`, `MTWRFS`, `TIME`, `INSTRUCTOR`, `SITE`, `Center Room #`, `Main Campus Rm #`, `Off Campus School`, `ID` FROM `importer` WHERE ID = '" + ID + "';"
                result = mysql_select(select_sql)
                for z in result:
                    room = z['Center Room #']
                    site = z['SITE']
                    main_campus = z['Main Campus Rm #']
                    title = z['TITLE']
                    instructor = z['INSTRUCTOR']
                    days = z['MTWRFS']
                    time = z['TIME']
                    subject = z['SUBJ']
                    coarse = z['CRS']
                    if room != "TBA":
                        if site != 'Online Crse':
                            #print(subject + ' ' + coarse + ' ' + title + ' ' + instructor + ' ' + days + ' ' + time)
                            #print(room + " " + site + " " + main_campus)
                            print(site, room)


def clean_days():
    select_sql = "select ID, MTWRFS from importer"
    result = mysql_select(select_sql)
    for x in result:
        ID = str(x['ID'])
        day = x['MTWRFS']
        day = day.replace(" ", "")
        print(day)
        update_sql = "update importer set MTWRFS = '" + day + "' where ID = '" + ID + "'"
        mysql_update(update_sql)


def host_load(changer):
    host_id_load = ['dlzoom2@ut.utm.edu',
                    'dlzoom3@ut.utm.edu',
                    'dlzoom4@ut.utm.edu',
                    'dlzoom5@ut.utm.edu',
                    'dlzoom6@ut.utm.edu',
                    'dlzoom7@ut.utm.edu',
                    'dlzoom8@ut.utm.edu',
                    'dlzoom9@ut.utm.edu',
                    'dlzoom10@ut.utm.edu',
                    'dlzoom11@ut.utm.edu',
                    'dlzoom12@ut.utm.edu',
                    'dlzoom13@ut.utm.edu',
                    'dlzoom14@ut.utm.edu',
                    'dlzoom15@ut.utm.edu'
                    ]
    #print(host_id_load[changer])
    return host_id_load[changer]


def zoom_info_maker(subj, crs, name):
    update_sql = "insert into zoom_info (zoom_title) values (" + subj + " " + crs + " " + name + ")"
    mysql_update(update_sql)


def main():
    find_duplicates()
    #clean_days()


if __name__ == "__main__":
    main()
#!/usr/bin/python3

import os
import datetime
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
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
    return my_result


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
    counting = 0
    for x in result:
        #print(x)
        SUBJ = x['SUBJ']
        CRS = x['CRS']
        TITLE = x['TITLE']
        INSTRUCTOR = x['INSTRUCTOR']
        select_sql = "select ID from importer where SUBJ ='" + SUBJ + "' and CRS = '" + CRS + "' and TITLE = '" + TITLE + "' and INSTRUCTOR = '" + INSTRUCTOR + "'"
        repeater = mysql_select(select_sql)
        get_classes(repeater, counting)
        #print(repeater)
        #for y in repeater:
        #    ID = str(y['ID'])
        #    select_sql = "SELECT `SUBJ`, `CRS`,`TITLE`, `MTWRFS`, `TIME`, `INSTRUCTOR`, `SITE`, `Center Room #`, `Main Campus Rm #`, `Off Campus School`, `ID` FROM `importer` WHERE ID = '" + ID + "';"
        #    #print(select_sql)
        #    rooms = mysql_select(select_sql)
            #print(rooms[0]['SUBJ'])
            #print(rooms)
        #    for z in rooms:
        #        room = z['Center Room #']
        #        site = z['SITE']
        #        main_campus = z['Main Campus Rm #']
        #        title = z['TITLE']
        #        instructor = z['INSTRUCTOR']
        #        days = z['MTWRFS']
        #        time = z['TIME']
        #        subject = z['SUBJ']
        #        coarse = z['CRS']
        #        if room != "TBA":
        #            if site != 'Online Crse':
        #                print(subject + ' ' + coarse + ' ' + title + ' ' + instructor + ' ' + days + ' ' + time)
        #                print(room + " " + site + " " + main_campus)
        print('***')


def get_classes(IDS, counting):
    #print(IDS)
    ID1 = str(IDS[0]['ID'])
    #print(ID1)
    select_sql = "SELECT `SUBJ`, `CRS`,`TITLE`, `MTWRFS`, `TIME`, `INSTRUCTOR`, `SITE`, `Center Room #`, `Main Campus Rm #`, `Off Campus School`, `ID` FROM `importer` WHERE ID = '" + ID1 + "';"
    result = mysql_select(select_sql)
    site = result[0]['SITE']
    room = result[0]['Center Room #']
    if site != 'Online Crse':
        if room != "TBA":
            print(result[0]['SUBJ'], result[0]['CRS'], result[0]['TITLE'], result[0]['INSTRUCTOR'], result[0]['MTWRFS'], result[0]['TIME'], result[0]['ID'])
            counting = counting + 1
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
                            print(room + " " + site + " " + main_campus)


def update_main_campus_rooms():
    select_sql = "SELECT * FROM `importer` WHERE `Main Campus Rm #` != ''"
    result = mysql_select(select_sql)
    #print(result)
    for x in result:
        main_campues_room = x['Main Campus Rm #']
        if main_campues_room == "BH 107":
            print(main_campues_room)


def main():
    find_duplicates()
    #update_main_campus_rooms()

if __name__ == "__main__":
    main()
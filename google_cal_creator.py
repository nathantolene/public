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
    for x in result:
        #print(x)
        SUBJ = x['SUBJ']
        CRS = x['CRS']
        TITLE = x['TITLE']
        INSTRUCTOR = x['INSTRUCTOR']
        select_sql = "select ID from importer where SUBJ ='" + SUBJ + "' and CRS = '" + CRS + "' and TITLE = '" + TITLE + "' and INSTRUCTOR = '" + INSTRUCTOR + "'"
        repeater = mysql_select(select_sql)
        #print(repeater)
        for y in repeater:
            ID = str(y['ID'])
            select_sql = "select `Center Room #`, `SITE`, `Main Campus Rm #`, 'TITLE', 'INSTRUCTOR', 'MTWRFS', 'TIME' from importer where ID = '" + ID + "';"
            #print(select_sql)
            rooms = mysql_select(select_sql)
            for z in rooms:
                room = z['Center Room #']
                site = z['SITE']
                main_campus = z['Main Campus Rm #']
                title = z['TITLE']
                instructor = z['INSTRUCTOR']
                days = z['MTWRFS']
                time = z['TIME']
                if room != "TBA":
                    if site != 'Online Crse':
                        print(title + ' ' + instructor + ' ' + days + ' ' + time)
                        print(room + " " + site + " " + main_campus)
        print('***')


def main():
    find_duplicates()


if __name__ == "__main__":
    main()
import mysql.connector
import os
import json
from dotenv import load_dotenv

load_dotenv()

utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
space = " "
dot = "."
comma = ", "
mark = "'"


def banner_pull_clear():
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    delete_sql = "delete from banner_pull"
    mycursor.execute(delete_sql)
    mydb.commit()


def banner_info_insert(events):
    #print(events)
    banner_pull_clear()
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    for i in range(len(events)):
        for x in events[i]['items']:
            #print(x)
            termcode = mark + x['ssbsect_term_code'] + mark
            crn = mark + x['ssbsect_crn'] + mark
            subj = mark + x['ssbsect_subj_code'] + mark
            crse_numb = mark + x['ssbsect_crse_numb'] + mark
            title = mark + str.replace(x['scbcrse_title'], "'", "_") + mark
            fname = mark + x['instr_fname'] + mark
            lname = mark + str.replace(x['instr_lname'], "'", "_") + mark
            bldg_code = mark + x['ssrmeet_bldg_code'] + mark
            room = mark + x['ssrmeet_room_code'] + mark
            start_date = mark + x['ssrmeet_start_date'] + mark
            end_date = mark + x['ssrmeet_end_date'] + mark
            try:
                begin_time = mark + x['ssrmeet_begin_time'] + mark
            except TypeError:
                pass
            end_time = mark + x['ssrmeet_end_time'] + mark
            try:
                sun = mark + str(x['ssrmeet_sun_day']) + mark
            except NameError:
                sun = 'None'
            try:
                mon = mark + str(x['ssrmeet_mon_day']) + mark
            except NameError:
                mon = 'None'
            try:
                tue = mark + str(x['ssrmeet_tue_day']) + mark
            except NameError:
                tue = 'None'
            try:
                wed = mark + str(x['ssrmeet_wed_day']) + mark
            except NameError:
                wed = 'None'
            try:
                thu = mark + str(x['ssrmeet_thu_day']) + mark
            except NameError:
                thu = 'None'
            try:
                fri = mark + str(x['ssrmeet_fri_day']) + mark
            except NameError:
                fri = 'None'
            try:
                sat = mark + str(x['ssrmeet_sat_day']) + mark
            except NameError:
                sat = 'None'

            insert_sql = "insert into banner_pull " \
                         "(termcode, crn, subj, crse_numb, title, fname, lname, bldg_code, room, " \
                         "start_date, end_date, begin_time, end_time, sun, mon, tue, wed, thu, fri, sat) " \
                         "values " \
                         "( " + termcode + comma + crn + comma + subj + comma + crse_numb + comma + title + comma + fname \
                         + comma + lname + comma + bldg_code + comma + room + comma + start_date + comma + end_date + \
                         comma + begin_time + comma + end_time + comma + sun + comma + mon + comma + tue + comma + wed + \
                         comma + thu + comma + fri + comma + sat + ")"
            #print(insert_sql)
            mycursor.execute(insert_sql)
            mydb.commit()


def list_it():
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select * from room_info"
    mycursor.execute(select_sql)
    my_result = mycursor.fetchall()
    return my_result


def find_classes():
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = " select title, count(title) from banner_pull group by title having count(title) > 1"
    # select lname, count(lname), title, count(title) from banner_pull
    # group by lname, title having count(lname) > 1 and count(title) > 1;
    mycursor.execute(select_sql)
    myresult = mycursor.fetchall()
    #print(myresult)
    for x in myresult:
        #print(x['title'])
        #print(x['count(title)'])
        select_sql = "select title, bldg_code, room, lname, begin_time, end_time from banner_pull where title = '" \
                     + x['title'] + "'"
        mycursor.execute(select_sql)
        myr = mycursor.fetchall()
        #print(myr)
        #for x in myr:
        #    print(x)

if __name__ == "__main__":
    #banner_info_insert(events)
    #find_classes()
    list_it()
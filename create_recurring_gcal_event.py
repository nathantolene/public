#!/usr/bin/python3

import os
import re
from datetime import datetime
from datetime import timedelta
import google_calendar_api
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
cal_id = os.environ.get('cal_id')
tz = 'America/Chicago'
until_equals = 'UNTIL='
end_of_semester = '20221203T170000Z'
rrule = 'RRULE:FREQ=WEEKLY;BYDAY='
# Example RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20221203T170000Z'

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
    row_id = my_cursor.lastrowid
    my_database.close()
    return row_id


def make_recurring_gcal_event(summary, description, start_time, start_tz, end_time, end_tz, location, attendees, recurrence):
    service = google_calendar_api.get_calendar_service()
    create = service.events().insert(calendarId=cal_id, body={
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time,
                  "timeZone": start_tz,
                  },
        "end": {"dateTime": end_time,
                "timeZone": end_tz,
                },
        "location": location,
        "recurrence": recurrence,
        "attendees": attendees,
    }
                                     ).execute()


def convert_days_rrules(days):
    #print(days['MTWRFS'])
    r_days = []
    for x in days['MTWRFS']:
        day = x
        print(day)
        for y in day:
            print(y)
            if y == 'U':
                y = 'SU'
            if y == 'M':
                y = 'MO'
            if y == 'T':
                y = 'TU'
            if y == 'W':
                y = 'WE'
            if y == 'R':
                y = 'TH'
            if y == 'F':
                y = 'FR'
            if y == 'S':
                y = 'SA'
            print(y)
            r_days.append(y)
    print(r_days)
    return r_days


def cal_rrule(days):
    r_days = convert_days_rrules(days)
    result = rrule
    for x in r_days:
        result = result + x + ','
        print(result)
    result = result[:-1]
    result = result + ';' + until_equals + end_of_semester
    return result


def cal_time(time):
    #time = [{'TIME': '04:00-05:50p'}]
    print(time)
    #for x in time:
    #print(x)
    #timing = x[0]
    timing = time
    am_pm = timing[-1]
    if am_pm == 'p':
        am_pm = 'PM'
    if am_pm == 'a':
        am_pm = 'AM'
    timing = timing[:-1]
    ts = timing.split('-')
    start_time = ts[0] + am_pm
    st_format = datetime.strptime(start_time, "%I:%M%p")
    end_time = ts[1] + am_pm
    et_format = datetime.strptime(end_time, "%I:%M%p")
    st_format = st_format + timedelta(minutes=-3)
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    sec = datetime.today().second
    st_format = st_format.replace(year=year, month=month, day=day)
    st_format = st_format.isoformat()
    st_format = st_format + "-05:00"
    et_format = et_format + timedelta(minutes=3)
    et_format = et_format.replace(year=year, month=month, day=day)
    et_format = et_format.isoformat()
    et_format = et_format + "-05:00"
    #print(st_format, et_format)
    times = (st_format, et_format)
    return times


def test_recurring_gcal_event():
    # summary, description, start_time, start_tz, end_time, end_tz, location, attendees, recurrence
    select_sql = "select importer_key, ID from zoom_info"
    result = mysql_select(select_sql)
    for x in result:
        zoom_info_id = str(x['ID'])
        key = str(x['importer_key'])
        select_sql = "select * from importer where ID ='" + key + "'"
        result = mysql_select(select_sql)
        for y in result:
            #print(y)
            start_tz = tz
            end_tz = tz
            crn = y['CRN']
            subj = y['SUBJ']
            crs = y['CRS']
            title = y['TITLE']
            time = y['TIME']
            name = y['INSTRUCTOR']
            name = name.split(" ")
            name = name[0]
            surmmary = subj + " " + crs + " " + name
            description = title
            #print(start_tz, end_tz, crn, subj, crs, title, time, name, surmmary, description)
            time_tup = cal_time(time)
            select_sql = "select zoom_number from zoom_info where ID = '" + zoom_info_id + "'"
            location = mysql_select(select_sql)
            select_sql = "select zoom_location from zoom_info where ID = '" + zoom_info_id + "'"
            attendees = mysql_select(select_sql)
            select_sql = "select recurring_settings from zoom_info where ID ='" + zoom_info_id + "'"
            recurrence = mysql_select(select_sql)
            #print(time_tup, location, attendees, recurrence)
            start_time = time_tup[0]
            end_time = time_tup[1]
            print(start_time)
            print(end_time)

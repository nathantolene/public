#!/usr/bin/python3

import os
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
    #days = 'MWF'
    print(days)
    r_days = []
    for x in days:
        print(x)
        day = x['MTWRFS']
        if day == 'U':
            day = 'SU'
        if day == 'M':
            day = 'MO'
        if day == 'T':
            day = 'TU'
        if day == 'W':
            day = 'WE'
        if day == 'R':
            day = 'TH'
        if day == 'F':
            day = 'FR'
        if day == 'S':
            day = 'SA'
        r_days.append(day)
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

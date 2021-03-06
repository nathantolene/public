import os
import time
import mysql.connector
from datetime import datetime
import cisco
import yaml
import google_calendar_service
import syslog
from dotenv import load_dotenv

load_dotenv()
utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
cm = ","
cq = ",'"
qc = "',"
qcq = "','"
q = "'"
delay = 60


def check_if_in_call(building, room):
    connected = cisco.get_current_sip_number(building, room)
    print(connected)


def connect_cisco_room(building, room, zoom_number, passcode):
    cisco_response = cisco.join_call(building, room, zoom_number, passcode)
    return cisco_response


def find_cisco_rooms(zoom_part):
    connect_me = []
    for n in zoom_part:
        part = n[0]
        part = part.strip()
        with open('room_info.yaml', 'r') as stream:
            for b in yaml.safe_load(stream):
                if part == b['displayName']:
                    if b['room_type'] == 'cisco':
                        connect_me.append({'building': b['building'], 'room': b['room']})
                else:
                    pass
            stream.close()
    return connect_me


def get_participants_from_gcal_location(location):
    location = str(location)
    location = location.split(',')
    attendee = []
    for x in location:
        # print(x)
        if "http" in x:
            continue
        attendee.append([x])
        attendee = sorted(attendee)
    # print(attendee)
    return attendee


def find_sip_number_from_gcal_location(location):
    zoom_number = location.split('/')
    zoom_number = zoom_number[4]
    zoom_number = zoom_number.split(',')
    zoom_number = zoom_number[0].split('?')
    zoom_number = zoom_number[0]
    # print(zoom_number)
    return zoom_number


def activate_events():
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    now = datetime.now()
    now = now.strftime("%Y-%m-%dT%H:%M:00-05:00")
    select_sql = "select id from gcal where start_time = " + q + now + q
    #print(select_sql)
    syslog.syslog("Checking for event START at " + now)
    my_cursor.execute(select_sql)
    response_activate = my_cursor.fetchall()
    #print(response_activate)
    try:
        syslog.syslog(response_activate)
    except TypeError:
        pass
    try:
        for x in response_activate:
            db_id = str(x['id'])
            select_sql = "select location from gcal where id = " + q + db_id + q
            my_cursor.execute(select_sql)
            syslog.syslog("Getting rooms for connection")
            location = my_cursor.fetchall()
            try:
                syslog.syslog(location)
            except TypeError:
                pass
            location = location[0]['location']
            zoom_number = find_sip_number_from_gcal_location(location)
            attendees = get_participants_from_gcal_location(location)
            connect_me = find_cisco_rooms(attendees)
            for z in connect_me:
                building = z['building']
                room = z['room']
                passcode = 'Skyhawks!'
                try:
                    connected = cisco.get_current_sip_number(building, room)
                    syslog.syslog(building + room + " Connected to " + connected)
                    connection = str(connected)
                    connection = connection.split(':')
                    connection = connection[1]
                    connection = connection.split('@')
                    connection = connection[0]
                except TypeError:
                    pass
                    #syslog.syslog("Not Connected to a Call " + building + room)
                if connected is None:
                    cisco_response = cisco.join_call(building, room, zoom_number, passcode)
                    print(cisco_response)
                else:
                    if connection == zoom_number:
                        continue
                    else:
                        call_id = cisco.get_call_id(building, room)
                        disconnect = cisco.disconnect_from_current_call(building, room, call_id)
                        print(disconnect)
                        try:
                            syslog.syslog(disconnect)
                        except TypeError:
                            pass
                        time.sleep(2)
                        cisco_response = cisco.join_call(building, room, zoom_number, passcode)
                        print(cisco_response)
                        try:
                            syslog.syslog(cisco_response)
                        except TypeError:
                            pass
    except IndexError:
        pass
    my_database.close()


def deactivate_events():
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    now = datetime.now()
    now = now.strftime("%Y-%m-%dT%H:%M:00-05:00")
    select_sql = "select id from gcal where end_time = " + q + now + q
    syslog.syslog("Checking for event END at " + now)
    my_cursor.execute(select_sql)
    response_deactivate = my_cursor.fetchall()
    try:
        for x in response_deactivate:
            db_id = str(x['id'])
            select_sql = "select location from gcal where id = " + q + db_id + q
            my_cursor.execute(select_sql)
            location = my_cursor.fetchall()
            location = location[0]['location']
            attendees = get_participants_from_gcal_location(location)
            disconnect_me = find_cisco_rooms(attendees)
            for z in disconnect_me:
                building = z['building']
                room = z['room']
                call_id = cisco.get_call_id(building, room)
                cisco_response = cisco.disconnect_from_current_call(building, room, call_id)
                print(cisco_response)
                try:
                    syslog.syslog("Cisco response " + cisco_response)
                except TypeError:
                    pass
    except IndexError:
        pass
    my_database.close()


def main():
    print('Updating Google Calendar events')
    syslog.syslog("Updating Google Calendar events")
    google_calendar_service.main()
    counter = 0
    while True:
        now = datetime.now()
        now = now.strftime('%Y-%m-%dT%H:%M:%S-05:00')
        print('Starting...', now)
        syslog.syslog("Checking " + now)
        deactivate_events()
        activate_events()
        print('Restarting...', now)
        syslog.syslog("Restarting " + now)
        if counter == 15:
            print('Updating Google Calendar events -- service')
            syslog.syslog("Updating Google Calendar events" + now)
            google_calendar_service.main()
            counter = 0
        else:
            counter += 1
        time.sleep(delay)


if __name__ == "__main__":
    main()

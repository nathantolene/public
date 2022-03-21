import requests
import xmltodict
import datetime
from datetime import timedelta
from datetime import datetime
from cal_setup import get_calendar_service
from lxml.etree import tostring
from lxml.builder import E
import os
import mysql.connector
import json
from zoomus import ZoomClient
from dotenv import load_dotenv

load_dotenv()

domain = os.environ.get('domain')
path = '/status.xml'
post_path = '/putxml'
starter = 'http://'
cisco_user = os.environ.get('cisco_user')
cisco_pass = os.environ.get('cisco_pass')
gcal_host_email = os.environ.get('gcal_host_email')
gcal_host = os.environ.get('utm_host')
gcal_user = os.environ.get('utm_user')
gcal_password = os.environ.get('utm_password')
gcal_database = os.environ.get('utm_database')
api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)
service = get_calendar_service()
zoom_passcode = os.environ.get('zoom_passcode')


def pull_cisco_room_info():
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select building, room, email from room_info where room_type = 'cisco'"
    mycursor.execute(select_sql)
    cisco = mycursor.fetchall()
    # print(cisco)
    return cisco


def get_participants_from_zoom_call(zoom_number):
    info = client.meeting.list_meeting_participants(id=zoom_number)
    info = json.loads(info.content)
    # print(info)
    participants = []
    try:
        for x in info['participants']:
            #print(x)
            participants.append(x)
    except KeyError:
        print('Class disconnected or not started', zoom_number )
        pass
    # print(participants)
    return participants


def change_gcal_event_color(events, color, gcal_id):
    for x in events:
        start = x['start']['dateTime']
        end = x['end']['dateTime']
        summary = x['summary']
        try:
            description = x['description']
        except KeyError:
            description = ''
        try:
            location = x['location']
        except KeyError:
            location = ''
        event_id = x['id']
        try:
            recurringEventId = x['recurring_id']
        except KeyError:
            recurringEventId = ''
        try:
            attendees = x['attendees']
        except KeyError:
            attendees = []
        if event_id == gcal_id:
            update_event = service.events().update(
                calendarId=gcal_host_email,
                eventId=event_id,
                body={
                    "colorId": color,
                    "start": {"dateTime": start},
                    "end": {"dateTime": end},
                    "location": location,
                    "description": description,
                    "summary": summary,
                    "attendees": attendees,
                    "recurringEventId": recurringEventId,
                }
            ).execute()


def get_info_from_cisco(cisco):
    for x in cisco:
        building = x['building']
        room = x['room']
        email = x['email']
        if building == 'Business Admin':
            building = 'BA'
        if building == 'Gooch Hall':
            building = 'Gooch'
        gather = starter + building + room + domain + path
        # print(gather)
        response = requests.get(gather, auth=(cisco_user, cisco_pass))
        data = response.content
        converted_root = xmltodict.parse(data)
        try:
            try:
                sip_number = converted_root['Status']['Call']['CallbackNumber']
                sip_number = sip_number.split(':')
                sip_number = sip_number[1].split('.')
            except AttributeError:
                sip_number = converted_root['Status']['Call']['CallbackNumber']['#text']
                sip_number = sip_number.split(':')
                sip_number = sip_number[1].split('.')
            insert_info_from_cisco(building + room, sip_number[0], email)
        except KeyError:
            # print(building, room, 'Not in Call')
            pass


def insert_info_from_cisco(name, sip, email):
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    cm = "', '"
    t = "'"
    insert_sql = "insert into cisco ( name, sip, email ) values ('" + name + cm + sip + cm + email + "')"
    mycursor.execute(insert_sql)
    mydb.commit()


def get_events_from_gcal():
    timeMin = datetime.now().isoformat() + 'Z'
    dt = datetime.today() + timedelta(days=1)
    timeMax = datetime.combine(dt, datetime.min.time())
    timeMax = timeMax.isoformat() + 'Z'
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId=gcal_host_email,
        timeMin=timeMin,
        timeMax=timeMax,
        maxResults=50,
        singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def find_sip_number_from_gcal_location(location):
    zoom_number = location.split('/')
    zoom_number = zoom_number[4]
    zoom_number = zoom_number.split(',')
    zoom_number = zoom_number[0].split('?')
    zoom_number = zoom_number[0]
    # print(zoom_number)
    return zoom_number


def find_attendees_from_gcal_location(location):
    location_split = location.split(',')
    attendee = []
    for x in location_split:
        if "http" in x:
            continue
        attendee.append(x)
    # print(attendee)
    return attendee


def insert_glcal_info_into_db(events):
    for x in events:
        # print(x)
        gcal_id = x['id']
        summary = x['summary']
        summary = summary.replace("'", '')
        try:
            description = x['description']
        except KeyError:
            description = ''
        location = x['location']
        start = x['start']['dateTime']
        st_tz = x['start']['timeZone']
        end_time = x['end']['dateTime']
        et_tz = x['end']['timeZone']
        try:
            recurring_id = x['recurringEventId']
        except KeyError:
            recurring_id = ''
        cm = "', '"
        t = "'"
        mydb = mysql.connector.connect(
            host=gcal_host,
            user=gcal_user,
            password=gcal_password,
            database=gcal_database
        )
        mycursor = mydb.cursor(dictionary=True)
        insert_sql = "insert into gcal (gcal_id, summary, description, location, start_time," \
                     " st_tz, end_time, et_tz, recurring_id) values (" + t + gcal_id + cm + summary + \
                     cm + description + cm + location + cm + start + cm + st_tz + cm + end_time + \
                     cm + et_tz + cm + recurring_id + t + ");"
        # print(insert_sql)
        mycursor.execute(insert_sql)
        mydb.commit()
        try:
            for y in x['attendees']:
                email = y['email']
                try:
                    displayName = y['displayName']
                except KeyError:
                    displayName = ''
                try:
                    responseStatus = y['responseStatus']
                except KeyError:
                    responseStatus = ''
                try:
                    resource = y['resource']
                    resource = str(resource)
                    #print(resource)
                except KeyError:
                    resource = ''
                try:
                    organizer = y['organizer']
                    organizer = str(organizer)
                    #print(organizer)
                except KeyError:
                    organizer = ''
                insert_sql2 = "insert into gcal_attendees " \
                              "(gcal_id, email, displayName, responceStatus, organizer, resource) " \
                              "values " \
                              "('" + gcal_id + cm + email + cm + displayName + cm + responseStatus + cm \
                              + organizer + cm + resource + "');"
                # print(insert_sql2)
                mycursor.execute(insert_sql2)
                mydb.commit()
        except KeyError:
            continue


def clear_tables():
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    delete_gcal = "delete from gcal"
    mycursor.execute(delete_gcal)
    delete_sql_gcal_attendees = "delete from gcal_attendees"
    mycursor.execute(delete_sql_gcal_attendees)
    delete_sql_cisco = "delete from cisco"
    mycursor.execute(delete_sql_cisco)
    mydb.commit()


def find_attendees_from_gcal_attendees_db(gcal_id):
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select displayName from gcal_attendees where gcal_id ='" + gcal_id + "'"
    mycursor.execute(select_sql)
    attendees = mycursor.fetchall()
    #print(attendees)
    return attendees


def insert_active_attendees():
    pass


def active_calls():
    now = datetime.now().isoformat() + 'Z'
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select location, gcal_id from gcal where '" + now + "' between start_time and end_time"
    # print(select_sql)
    mycursor.execute(select_sql)
    response = mycursor.fetchall()
    for x in response:
        location = x['location']
        #sip_number = x['location'].split(",")
        #sip_number = sip_number[0]
        #sip_number = sip_number.split("?")
        #sip_number = sip_number[0].split("/")
        #sip_number = sip_number[4]
        sip_number = find_sip_number_from_gcal_location(location)
        gcal_id = x['gcal_id']
        participants = get_participants_from_zoom_call(sip_number)
        if not participants:
            continue
        attendess = find_attendees_from_gcal_attendees_db(gcal_id)
        #print(participants)
        peers = []
        for y in participants:
            leave_reason = ''
            try:
                #print(y['leave_reason'])
                leave_reason = y['leave_reason']
            except KeyError:
                pass
            if leave_reason == '':
                active_user = y['user_name']
                #print('Active:', active_user + '*')
                peers.append(active_user)
        for z in attendess:
            #print(peers)
            try:
                displayName_real = z['displayName']
                displayName = displayName_real.split("-")
                building = displayName[0]
                building = building.split(' ')
                try:
                    if building[1]:
                        building = building[0]
                    if building == 'Business':
                        building = 'BA'
                except IndexError:
                    building = displayName[0]
                    building = building.replace(" ", "")
                room = displayName[2]
                room = room.split('(')
                room = room[0]
                room = room.replace(" ", "")
                room = room.upper()
                #print(building, room)
                building_room = building + ' ' + room
                for w in peers:
                    #print(w)
                    if w == building_room:
                        print('Connected', building_room)
                        update_sql = "update gcal_attendees set active=1 where gcal_id ='" + gcal_id + "'" + \
                                     "and displayName = '" + displayName_real + "'"
                        #print(insert_sql)
                        mycursor.execute(update_sql)
                        mydb.commit()
                    else:
                        #print('else', w)
                        pass
            except IndexError:
                continue
        compare_gcal_w_attendees(gcal_id)


def active_dlzoom1():
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    update_sql = "update gcal_attendees set active = 1 where email = 'dlzoom1@ut.utm.edu'"
    mycursor.execute(update_sql)
    mydb.commit()


def compare_gcal_w_attendees(gcal_id):
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(buffered=True)
    select_sql = "select active from gcal_attendees where gcal_id = '" + gcal_id + "'"
    mycursor.execute(select_sql)
    rows = mycursor.rowcount # to use rowcount you must use buffered=True with mydb.cursor as above
    active = mycursor.fetchall()
    count = 0
    #print('rows', rows)
    for x in active:
        if x[0] is None:
            continue
        count = count + x[0]
        #print(count)
    if count == rows:
        mycursor = mydb.cursor(dictionary=True)
        update_sql = "update gcal set all_in_attendance = 1 where gcal_id = '" + gcal_id + "'"
        mycursor.execute(update_sql)
        mydb.commit()


def get_events_to_update_color(events):
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select * from gcal where all_in_attendance = 1"
    mycursor.execute(select_sql)
    green_events = mycursor.fetchall()
    for x in green_events:
        # print(x)
        # select_sql2 = "select * from gcal_attendees where gcal_id = '" + x['gcal_id'] + "'"
        # mycursor.execute(select_sql2)
        # attendees = mycursor.fetchall()
        # print(attendees)
        print('All rooms are connected for', x['summary'])
        gcal_id = x['gcal_id']
        change_gcal_event_color(events, 10, gcal_id)


def join_call(building, room, sip_number):
    xml_string = tostring(E.Command(E.Dial(E.Number(sip_number))),
                         pretty_print=True, xml_declaration=True, encoding='utf-8')
    #print(xmlstring)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    #print(post.content)
    return post


def find_missing_attendees():
    now = datetime.now().isoformat() + 'Z'
    mydb = mysql.connector.connect(
        host=gcal_host,
        user=gcal_user,
        password=gcal_password,
        database=gcal_database
    )
    mycursor = mydb.cursor(dictionary=True)
    select_sql = "select location, gcal_id, summary from gcal where '" + now + "' between start_time and end_time"
    mycursor.execute(select_sql)
    responce = mycursor.fetchall()
    for x in responce:
        gcal_id = x['gcal_id']
        location = x['location']
        summary = x['summary']
        sip_number = find_sip_number_from_gcal_location(location)
        sip_number = sip_number + '.' + zoom_passcode + '@zoomcrc.com'
        #print(gcal_id)
        select_sql2 = "select displayName from gcal_attendees where gcal_id = '" + gcal_id + "' and active is NUll"
        mycursor.execute(select_sql2)
        missing = mycursor.fetchall()
        #print(missing)
        for y in missing:
            displayName_real = y['displayName']
            displayName = displayName_real.split("-")
            building = displayName[0]
            building = building.split(' ')
            try:
                if building[1] == 'Hall':
                    building = building[0]
            except IndexError:
                building = displayName[0]
                building = building.replace(" ", "")
            room = displayName[2]
            room = room.split('(')
            room = room[0]
            room = room.replace(" ", "")
            select_sql3 = "select room_type from room_info where displayName = '"+ displayName_real + "'"
            mycursor.execute(select_sql3)
            rooms = mycursor.fetchall()
            for z in rooms:
                room_type = z['room_type']
                if room_type == 'cisco':
                    print(displayName_real, 'is missing from', summary)
                    yes_no = input('Should I connect this room? Y/N: ')
                    yes_no = yes_no.lower()
                    if yes_no == 'y':
                        join_call(building, room, sip_number)
                        #print(building, room, sip_number)
                    else:
                        continue


def main():
    clear_tables()
    #cisco = pull_cisco_room_info()
    #get_info_from_cisco(cisco)
    events = get_events_from_gcal()
    insert_glcal_info_into_db(events)
    active_dlzoom1()
    active_calls()
    get_events_to_update_color(events)
    #find_missing_attendees()


if __name__ == "__main__":
    main()

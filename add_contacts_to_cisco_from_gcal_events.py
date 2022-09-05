#!/usr/bin/python

import google_calendar_api
import cisco
import os
import yaml
from dotenv import load_dotenv

load_dotenv()
passcode = os.environ.get('zoom_passcode')
room_file = os.environ.get('rooms_info_abspath')


def load_rooms():
    with open(room_file) as file:
        all_rooms = yaml.full_load(file)
    #print(all_rooms)
    return all_rooms


def get_events_for_room(room_email):
    events = google_calendar_api.get_events_from_gcal(room_email)
    event_list = []
    for x in events:
        event = {}
        title = x['summary']
        loc = x['location']
        loc = google_calendar_api.find_sip_number_from_gcal_location(loc)
        event['title'] = title
        event['location'] = loc
        event_list.append(event)
    return event_list


def get_emails_for_cisco_rooms(all_rooms):
    #print(all_rooms)
    emails = []
    for x in all_rooms:
        #print(x)
        type = x['room_type']
        if type == 'cisco':
            list = {}
            email = x['email']
            building = x['building']
            room = x['room']
            #print(email, building, room)
            list['email'] = email
            list['building'] = building
            list['room'] = room
            emails.append(list)
        #print(emails)
    return emails


def build_zoom_number_from_sip_number(sip_number):
    zoom_number = sip_number + '.' + passcode + '@zoomcrc.com'
    return zoom_number


def main():
    all_rooms = load_rooms()
    emails = get_emails_for_cisco_rooms(all_rooms)
    for x in emails:
        room_email = x['email']
        building = x['building']
        room = x['room']
        cisco.delete_all_contacts_for_room(building, room)
        events = get_events_for_room(room_email)
        #print(events, building, room)
        #if building == 'Parsons' and room == '201':
            #print(events, building, room)
        for y in events:
            title = y['title']
            loc = y['location']
            loc = build_zoom_number_from_sip_number(loc)
            cisco.add_contact(building, room, title, loc)


if __name__ == "__main__":
    main()
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime
from datetime import timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.environ.get('cred_file')
gcal_host_email = os.environ.get('gcal_host_email')


def get_calendar_service():
    credential = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credential = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credential or not credential.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            credential = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credential, token)

    service = build('calendar', 'v3', credentials=credential)
    return service


service = get_calendar_service()


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


def find_attendees_from_gcal_location(location):
    location_split = location.split(',')
    attendee = []
    for x in location_split:
        if "http" in x:
            continue
        attendee.append(x)
    # print(attendee)
    return attendee


def get_current_active_events(events):
    for x in events:
        tz = pytz.timezone('America/Chicago')
        begin_time = x['start']['dateTime']
        begin_time = datetime.strptime(begin_time, '%Y-%m-%dT%H:%M:%S-05:00')
        begin_time = begin_time.replace(tzinfo=tz)
        print(begin_time)
        end_time = x['end']['dateTime']
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S-05:00')
        end_time = end_time.replace(tzinfo=tz)
        print(end_time)
        check_time = None
        check_time = check_time or datetime.now(tz=tz)
        print(check_time)
        active = is_event_currently_active(begin_time, end_time, check_time)
        return active


def is_event_currently_active(begin_time, end_time, current_time):
    if begin_time < end_time:
        return begin_time <= current_time <= end_time
    else:  # crosses midnight
        return current_time >= begin_time or current_time <= end_time
import datetime
from datetime import date
import zoomus
import syslog
import time
import json
import yaml
import os
from zoomus import ZoomClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)
zoom_passcode = os.environ.get('zoom_passcode')
delete_on = 0


# host_id = 'nathant@utm.edu'

def list_zoom_meetings(host_id):
    listings = client.meeting.list(user_id=host_id)
    listings_content = json.loads(listings.content)
    # print(listings_content)
    for topics in listings_content['meetings']:
        topic = topics['topic']
        #start_time = topics['start_time']
        #start_time = start_time.split('T')
        duration = topics['duration']
        id = topics['id']
        join_url = topics['join_url']
        print(host_id)
        #print(topic + '\n--Start time: ' + start_time[1] +
        #      '\n--Duration: ' + str(duration) + '\n--ID: ' + str(id)
        #      + '\n--Join URL: ' + join_url
        #      )
        print('Topic: ', topic, "\nID: ", id,'\nJoin URL: ', join_url)
        if delete_on > 0:
            delete_zoom_meeting(id)
        return id
    # for topics in listings_content['meetings']:
    #    for all_topics in topics:
    #        topic = all_topics['topic']
    #        start_time = all_topics['start_time']
    #        start_time = start_time.split('T')
    #        duration = all_topics['duration']
    #        id = all_topics['id']
    #        join_url = all_topics['join_url']
    #        print(topic + '\n--Start time: ' + start_time[1] +
    #              '\n--Duration: ' + str(duration) + '\n--ID: ' + str(id)
    #              + '\n--Join URL: ' + join_url
    #              )
    #        return id


def create_zoom_meeting(host_id, topic, pmi):
    if not pmi:
        create = client.meeting.create(user_id=host_id,
                                       topic=topic,
                                       duration=60,
                                       password=zoom_passcode,
                                       start_time=date.today(),
                                       type=3,
                                       settings={"use_pmi": 'false'},
                                       #recurrence={"type": 2,
                                       #            "repeat_interval": 1,
                                       #            "weekly_days": '2,4',
                                       #            "end_times": 30}
                                       )
        listing = yaml.safe_load(create.content)
        print(listing)
        zoom_join = listing['join_url']
        print(zoom_join)
        return zoom_join
    if pmi:
        create = client.meeting.create(user_id=host_id,
                                       topic=topic,
                                       #duration=60,
                                       #password='Skyhawks!',
                                       #start_time=date.today(),
                                       type=1,
                                       settings={"use_pmi": 'True'},
                                       #recurrence={"type": 1,
                                       #            "repeat_interval": 1,
                                       #            "weekly_days": '2,4',
                                       #            "end_times": 30}
                                       )
        listing = yaml.safe_load(create.content)
        zoom_join = listing['join_url']
        print(zoom_join)
        return zoom_join


def delete_zoom_meeting(meeting_id):
    delete = client.meeting.delete(id=meeting_id)


def delete_all_meetings():
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
    hosting = len(host_id_load)
    print(hosting)
    while hosting >= 0:
        print(host_id_load[hosting - 1])
        hosting = hosting - 1
        id = list_zoom_meetings(host_id_load[hosting])
        print('deleting: ', id)
        delete_zoom_meeting(id)


def list_all_meetings():
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
    hosting = len(host_id_load)
    # print(hosting)
    # print('\n')
    while hosting >= 0:
        # print(host_id_load[hosting - 1])
        hosting = hosting - 1
        id = list_zoom_meetings(host_id_load[hosting])
        # print(id)

# create_zoom_meeting()
# delete_zoom_meeting('98283443230')
# list_zoom_meetings('dlzoom10@ut.utm.edu')
#delete_all_meetings()
list_all_meetings()

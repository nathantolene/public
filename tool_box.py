import requests
from datetime import datetime, timedelta
import json
import jwt
import os
from time import time
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


CA_PATH = os.environ.get('ca_path')
ACCOUNT_ID = os.environ.get('zoom_account_id')
CLIENT_ID = os.environ.get('zoom_client_id')
CLIENT_SECRET = os.environ.get('zoom_client_secret')
AUTH_SERVER_URL = "https://zoom.us/oauth/token"
api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
today = datetime.today()
first = today.replace(day=1)
last_month = first - timedelta(days=31)
from_date = last_month.strftime("%Y-%m-%d")
alternative_hosts = 'nathant@utm.edu;ajamerso@utm.edu;madams@utm.edu'  # list must have ; between users


def generate_token_s2s_oauth():
    token_req_payload = {'grant_type': 'account_credentials', 'account_id': ACCOUNT_ID}

    token_response = requests.post(AUTH_SERVER_URL,
                                   data=token_req_payload, verify=CA_PATH, allow_redirects=False,
                                   auth=(CLIENT_ID, CLIENT_SECRET))

    if token_response.status_code != 200:
        print("Failed to obtain token from the Zoom server")
    else:
        # print("SuccessfulLy obtained a new token")
        tokens = json.loads(token_response.text)
        return tokens['access_token']


def generate_token():
    token = jwt.encode(
        {'iss': api_key, 'exp': time() + 5000},
        api_sec,
        algorithm='HS256'
    )
    return token


class ZoomUsers:
    def __init__(self, users):
        self.id = users['id']
        self.f_name = users['first_name']
        self.l_name = users['last_name']
        self.email = users['email']
        self.type = users['type']
        self.pmi = users['pmi']
        try:
            self.timezone = users['timezone']
        except KeyError:
            self.timezone = ''
        self.verified = users['verified']
        self.created_at = users['created_at']
        try:
            self.last_login_time = users['last_login_time']
        except KeyError:
            self.last_login_time = ''
        try:
            self.language = users['language']
        except KeyError:
            self.language = ''
        self.status = users['status']
        self.role_id = users['role_id']
        self.user_created_at = users['user_created_at']


class ZoomRecordings:
    def __init__(self, recording_info):
        self.uuid = recording_info['uuid']
        self.id = recording_info['id']
        self.account_id = recording_info['account_id']
        self.host_id = recording_info['host_id']
        self.topic = recording_info['topic']
        self.type = recording_info['type']
        self.start_time = recording_info['start_time']
        self.timezone = recording_info['timezone']
        self.duration = recording_info['duration']
        self.total_size = recording_info['total_size']
        self.recording_count = recording_info['recording_count']
        self.share_url = recording_info['share_url']
        self.recordings = recording_info['recording_files']
        if '/' in self.uuid:
            encoded = urllib.parse.quote(self.uuid, safe='')
            self.uuid = urllib.parse.quote(encoded, safe='')


class RecordingFiles:
    def __init__(self, recording_files):
        self.id = recording_files['id']
        self.meeting_id = recording_files['meeting_id']
        if '/' in self.meeting_id:
            encoded = urllib.parse.quote(self.meeting_id, safe='')
            self.meeting_id = urllib.parse.quote(encoded, safe='')
        self.recording_start = recording_files['recording_start']
        self.recording_end = recording_files['recording_end']
        self.file_type = recording_files['file_type']
        self.file_extension = recording_files['file_extension']
        self.file_size = recording_files['file_size']
        self.download_url = recording_files['download_url']
        self.status = recording_files['status']
        try:
            self.recording_type = recording_files['recording_type']
        except KeyError:
            self.recording_type = ''
        try:
            self.play_url = recording_files['play_url']
        except KeyError as e:
            self.play_url = 'TRANSCRIPT'


class ZoomMeetings:

    def __init__(self, meeting_info):
        self.uuid = meeting_info['uuid']
        self.id = meeting_info['id']
        self.host_id = meeting_info['host_id']
        self.topic = meeting_info['topic']
        self.type = meeting_info['type']
        try:
            self.start_time = meeting_info['start_time']
        except:
            pass
        self.duration = meeting_info['duration']
        self.timezone = meeting_info['timezone']
        self.created_at = meeting_info['created_at']
        self.join_url = meeting_info['join_url']
        return


class ZoomApi:
    def __init__(self):
        self.endpoint_base = 'https://api.zoom.us/v2'
        # self.headers = {'authorization': 'Bearer %s' % generate_token(),
        #                 'content-type': 'application/json'}
        self.headers = {'authorization': 'Bearer %s' % generate_token_s2s_oauth(),
                        'content-type': 'application/json'}

    def pagination(self, get, end_point):
        all_info = [get]
        try:
            next_page = get['next_page_token']
            # print(next_page)
            while next_page != '':
                params = {
                    'next_page_token': next_page
                }
                next_get = requests.get(self.endpoint_base + end_point, headers=self.headers, params=params)
                next_get = json.loads(next_get.content)
                next_page = next_get['next_page_token']
                all_info.append(next_get)
                # print('used pagination')
        except KeyError or TypeError:
            return all_info
        return all_info

    def getter(self, end_point):
        get = requests.get(self.endpoint_base + end_point, headers=self.headers)
        get = json.loads(get.content)
        get = self.pagination(get, end_point)
        return get

    def getter_params(self, end_point, params):
        get = requests.get(self.endpoint_base + end_point, headers=self.headers, params=params)
        get = json.loads(get.content)
        get = self.pagination(get, end_point)
        return get

    def post(self, end_point, data):
        post = requests.post(self.endpoint_base + end_point, headers=self.headers, data=json.dumps(data))
        post = json.loads(post.content)
        return post

    def deleter(self, end_point):
        deleter = requests.delete(self.endpoint_base + end_point, headers=self.headers)
        # deleter = json.loads(deleter.content)
        return deleter

    def putter(self, end_point, params):
        putter = requests.put(self.endpoint_base + end_point, headers=self.headers, data=json.dumps(params))
        return putter

    def list_user_meetings(self, userId):
        end_point = f'/users/{userId}/meetings'
        get = self.getter(end_point)
        return get

    def list_user_recordings(self, userId):
        endpoint = f'/users/{userId}/recordings/'
        add_from_date = {
            "from": from_date,
            "to": today
        }
        all_recordings = self.getter_params(endpoint, add_from_date)
        return all_recordings[0]

    def list_zoom_rooms(self):
        end_point = '/rooms/zrlist'
        data = {
            "jsonrpc": "2.0",
            "method": "list",
        }
        post = self.post(end_point, data)
        return post['result']['data']

    def get_invitation(self, meeting_id):
        endpoint = f'/meetings/{meeting_id}/invitation'
        get = self.getter(endpoint)
        return get

    def create_zoom_meeting(self, host_id, topic, zoom_passcode):
        end_point = f'/users/{host_id}/meetings'
        data = {'user_id': host_id,
                'topic': topic,
                'duration': 60,
                'password': zoom_passcode,
                # 'start_time': date.today(),
                'type': 3,
                'settings': {"use_pmi": 'false', 'alternative_hosts': alternative_hosts,
                             'alternative_hosts_email_notification': 'False'},
                }
        post = self.post(end_point, data)
        return post

    def list_meeting_participants(self, meeting_id):
        endpoint = f'/metrics/meetings/{meeting_id}/participants/'
        get = self.getter(endpoint)
        return get

    def list_all_zoom_meetings(self):
        endpoint = f'/metrics/meetings'
        now = datetime.now().strftime('%Y-%m-%d')
        scope = {
            "type": "live",
            "params": {
                "from": now,
                "to": now
            }
        }
        get = self.getter_params(endpoint, scope)
        return get

    def list_user_in_group(self, groupId):
        end_point = f'/groups/{groupId}/members?page_size=300'
        all_users = self.getter(end_point)
        return all_users[0]

    def list_groups(self):
        end_point = '/groups'
        groups = self.getter(end_point)
        return groups

    def add_zoom_user_to_group(self, email, group_id):
        end_point = f'/groups/{group_id}/members'
        data = {
            "members": [
                {
                    "email": email,
                }
            ]
        }
        # post = requests.post(endpoint_base + endpoint, headers=headers, data=json.dumps(data))
        # post = json.loads(post.content)
        post = self.getter_params(end_point, data)
        return post

    def get_users(self):
        end_point = "/users/"
        all_users = self.getter(end_point)
        return all_users

    def get_meeting(self, meeting_id):
        end_point = f'/meetings/{meeting_id}/'
        get = self.getter(end_point)
        return get

    def get_meeting_report(self, user_id):
        end_point = f'/report/users/{user_id}/meetings/'
        # from = yyyy-mm-dd
        # to = yyyy-mm-dd
        from_input = input('Please enter year, month, day as yyyy-mm-dd from which to start')
        to_input = input('Please enter year, month, day as yyyy-mm-dd from which to end')
        params = {
            'from': from_input,
            'to': to_input
        }
        get = self.getter_params(end_point, params)
        return get

    def get_meeting_participant_reports(self, meeting_id):
        end_point = f'/report/meetings/{meeting_id}/participants/'
        get = self.getter(end_point)
        return get

    def get_meeting_detail_reports(self, meeting_id):
        end_point = f'/report/meetings/{meeting_id}/'
        get = self.getter(end_point)
        return get

    def get_meeting_recordings(self, meeting_id):
        end_point = f'/meetings/{meeting_id}/recordings'
        get = self.getter(end_point)
        return get

    def get_daily_usage_report(self):
        end_point = f'/report/daily/'
        year = input('Year?')
        month = input('Month')
        params = {
            'year': year,
            'month': month
        }
        get = self.getter_params(end_point, params)
        return get

    def get_cloud_recording_usage_report(self):
        end_point = f'/report/cloud_recording/'
        from_input = input('Start date yyyy-mm-dd: ')
        to_input = input('End date yyyy-mm-dd: ')
        params = {
            'from': from_input,
            'to': to_input
        }
        get = self.getter_params(end_point, params)
        return get

    def get_sharing_and_recording_details(self, meeting_id):
        end_point = f'/metrics/meetings/{meeting_id}/participants/sharing'
        get = self.getter(end_point)
        return get

    def get_list_sip_h323_devices(self):
        end_point = '/h323/devices'
        get = self.getter(end_point)
        return get

    def get_zoom_room_device_information(self, room_id):
        end_point = f'/rooms/{room_id}/device_profiles/devices/'
        get = self.getter(end_point)
        return get

    def get_list_zoom_room_devices(self, room_id):
        end_point = f'/rooms/{room_id}/devices/'
        get = self.getter(end_point)
        return get

    def get_zoom_room_settings(self, room_id):
        end_point = f'/rooms/{room_id}/settings/'
        setting_type = input('Setting Type: (Meeting/Alert): ')
        params = {
            'setting_type': setting_type
        }
        get = self.getter_params(end_point, params)
        return get

    def delete_recordings(self, meetingId):
        end_point = f'/meetings/{meetingId}/recordings'
        delete = self.deleter(end_point)
        if delete.status_code == 200 or delete.status_code == 204:
            # print('Meeting:', meetingId, 'Deleted')
            return True, delete.status_code
        if delete.status_code == 404:
            # print('ERROR: Meeting recording not found or There is no recording for this meeting.', meetingId)
            return False, delete.status_code

    def end_meeting(self, zoom_number):
        end_point = f'/meetings/{zoom_number}/status'
        params = {
            "action": "end"
        }
        put = self.putter(end_point, params)
        if put.status_code == 204:
            # print("ENDED", zoom_number)
            return True
        if put.status_code != 204:
            return False

    def zoom_room_join(self, meeting_id, password, room_id):
        end_point = f'/rooms/{room_id}/meetings'
        params = {
            "jsonrpc": "2.0",
            "method": "join",
            "params": {
                "meeting_number": meeting_id,
                "password": password,
                "force_accept": False,
                # "callback_url": "https://api.test.zoom.us/callback?token=123"
            }
        }
        post = self.post(end_point, params)
        return post

    def create_zoom_meeting_pmi(self, host_id, topic, zoom_passcode):
        end_point = f'/users/{host_id}/meetings'
        params = {'user_id': host_id,
                  'topic': topic,
                  'duration': 60,
                  'password': zoom_passcode,
                  # 'start_time': date.today(),
                  'type': 3,
                  'settings': {"use_pmi": 'True', 'alternative_hosts': alternative_hosts,
                               'alternative_hosts_email_notification': 'False'},
                  }
        post = self.post(end_point, params)
        return post

    def get_room_usage_report(self, userId, from_date, to_date):
        end_point = f'/report/users/{userId}/meetings'
        params = {
            'from': from_date,  # 2022-01-01
            'to': to_date,
            'page_size': 300
        }
        return self.getter_params(end_point, params)

    def delete_meeting(self, meetingId):
        end_point = f'/meetings/{meetingId}'
        delete = self.deleter(end_point)
        # print(delete.status_code)
        if delete.status_code == 200 or delete.status_code == 204:
            # print('Meeting:', meetingId, 'Deleted')
            return True, delete.status_code
        if delete.status_code == 404:
            # print('ERROR: Meeting  not found or There is no meeting.', meetingId)
            return False, delete.status_code

    def zoom_room_account_profile(self):
        end_point = '/rooms/account_profile'
        return self.getter(end_point)

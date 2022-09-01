import requests
from datetime import datetime
import json
import zoom_api_token


endpoint_base = 'https://api.zoom.us/v2'
headers = {'authorization': 'Bearer %s' % zoom_api_token.generate_token(),
           'content-type': 'application/json'}


#def page_checker(endpoint, get):
#    pager = get[0]['next_page_token']
#    endpoint = endpoint + '?next_page_token=' + pager
#    #endpoint = endpoint + '?page_size='
#    print(endpoint)
#    req = requests.get(endpoint_base + endpoint, headers=headers)
#    get.append(json.loads(req.content))
#    print(get)
#    return get

# def set_host_key(userId):
#     host_key = '359666'
#     end_point = f'/users/{userId}'
#     change_host_key = {
#         "host_key": host_key
#     }
#     put = requests.put(endpoint_base + end_point, headers=headers, data=json.dumps(change_host_key))
#     if put.status_code == 204:
#         print("Changed Host Code to:", host_key)
#         return True
#     if put.status_code != 204:
#         print(put.status_code)
#         return False


def list_user_in_group(groupId):
    end_point = f'/groups/{groupId}/members?page_size=300'
    req = requests.get(endpoint_base + end_point, headers=headers)
    get = json.loads(req.content)
    return get


def list_user_meetings(userId):
    end_point = f'/users/{userId}/meetings'
    get = requests.get(endpoint_base + end_point, headers=headers)
    get = json.loads(get.content)
    return get


def end_meeting(zoom_number):
    # https://api.zoom.us/v2/meetings/{meetingId}/status
    end_point = f'/meetings/{zoom_number}/status'
    end = {
        "action": "end"
    }
    put = requests.put(endpoint_base + end_point, headers=headers, data=json.dumps(end))
    # print(put.status_code)
    if put.status_code == 204:
        print("ENDED", zoom_number)
        return True
    if put.status_code != 204:
        return False


def list_all_zoom_meetings():
    endpoint = f'/metrics/meetings'
    now = datetime.now().strftime('%Y-%m-%d')
    scope = {
        "type": "live",
        "params": {
            "from": now,
            "to": now
        }
    }
    get = requests.get(endpoint_base + endpoint, headers=headers, params=json.dumps(scope))
    get = json.loads(get.content)
    return get


def list_user_recordings(user_id):
    endpoint = f'/users/{user_id}/recordings/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_users():
    endpoint = "/users/"
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_invitation(meeting_id):
    endpoint = f'/meetings/{meeting_id}/invitation'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def zoom_room_join(meeting_id, password, room_id):
    endpoint = f'/rooms/{room_id}/meetings'
    join = {
        "jsonrpc": "2.0",
        "method": "join",
        "params": {
            "meeting_number": meeting_id,
            "password": password,
            "force_accept": False,
            # "callback_url": "https://api.test.zoom.us/callback?token=123"
        }
    }
    post = requests.post(endpoint_base + endpoint, headers=headers, data=json.dumps(join))
    post = json.loads(post.content)
    return post


def list_zoom_rooms():
    end_point = '/rooms/zrlist'
    rooms = {
        "jsonrpc": "2.0",
        "method": "list",
    }
    post = requests.post(endpoint_base + end_point, headers=headers, data=json.dumps(rooms))
    post = json.loads(post.content)
    return post


def get_meeting(meeting_id):
    endpoint = f'/meetings/{meeting_id}/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_meeting_report(user_id):
    endpoint  = f'/report/users/{user_id}/meetings/'
    # from = yyyy-mm-dd
    # to = yyyy-mm-dd
    from_input = input('Please enter year, month, day as yyyy-mm-dd from which to start')
    to_input = input('Please enter year, month, day as yyyy-mm-dd from which to end')
    parms  = {
        'from': from_input,
        'to': to_input
    }
    get = requests.get(endpoint_base + endpoint, headers=headers, params=parms)
    get = json.loads(get.content)
    return get


def get_meeting_participant_reports(meeting_id):
    endpoint = f'/report/meetings/{meeting_id}/participants/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_meeting_detail_reports(meeting_id):
    endpoint = f'/report/meetings/{meeting_id}/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_daily_usage_report():
    endpoint = f'/report/daily/'
    year = input('Year?')
    month = input('Month')
    params = {
        'year': year,
        'month': month
    }
    get = requests.get(endpoint_base + endpoint, headers=headers, params=params)
    get = json.loads(get.content)
    return get


def get_cloud_recording_usage_report():
    endpoint = f'/report/cloud_recording/'
    from_input = input('Start date yyyy-mm-dd: ')
    to_input = input('End date yyyy-mm-dd: ')
    params = {
        'from': from_input,
        'to': to_input
    }
    get = requests.get(endpoint_base + endpoint, headers=headers, params=params)
    get = json.loads(get.content)
    return get


def list_meeting_participants(meeting_id):
    # https://api.zoom.us/v2/metrics/meetings/{meetingId}/participants
    endpoint = f'/metrics/meetings/{meeting_id}/participants/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_sharing_and_recording_details(meeting_id):
    endpoint = f'/metrics/meetings/{meeting_id}/participants/sharing'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_list_sip_h323_devices():
    endpoint = '/h323/devices'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_zoom_room_device_information(room_id):
    endpoint = f'/rooms/{room_id}/device_profiles/devices/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_list_zoom_room_devices(room_id):
    endpoint = f'/rooms/{room_id}/devices/'
    get = requests.get(endpoint_base + endpoint, headers=headers)
    get = json.loads(get.content)
    return get


def get_zoom_room_settings(room_id):
    endpoint = f'/rooms/{room_id}/settings/'
    setting_type = input('Setting Type: (Meeting/Alert): ')
    params = {
        'setting_type': setting_type
    }
    get = requests.get(endpoint_base + endpoint, headers=headers, params=params)
    get = json.loads(get.content)
    return get


def main():
    pass


if __name__ == "__main__":
    main()

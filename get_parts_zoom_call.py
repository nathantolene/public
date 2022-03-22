import os
import json
from zoomus import ZoomClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)


def get_participants_from_zoom_call(zoom_number):
    info = client.meeting.list_meeting_participants(id=zoom_number)
    info = json.loads(info.content)
    #print(info)
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


def main():
    zoom_number = input('Zoom Number? ')
    get_participants_from_zoom_call(zoom_number)


if __name__ == "__main__":
    main()
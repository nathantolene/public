import json
import mysql.connector
from zoomus import ZoomClient
import os
from datetime import date, datetime
import v2_get_zoom_recordings
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)
zdl_host = os.environ.get('zdl_host')
zdl_user = os.environ.get('zdl_user')
zdl_password = os.environ.get('zdl_password')
zdl_database = os.environ.get('zdl_database')
year = "2022"
day = "01"
month = "01"
convert_time = datetime.fromisoformat(year + "-" + month + '-' + day)


def v2_delete_recordings_from_zoom(group_list):
    for x in group_list['members']:
        email = x['email']
        recording_list_response = client.recording.list(user_id=email, page_size=50, start=convert_time)
        recording_list = json.loads(recording_list_response.content)
        print(recording_list)
        for meetings in recording_list['meetings']:
            meeting_id = meetings['uuid']
            print(meeting_id)
            mydb = mysql.connector.connect(
                host=zdl_host,
                user=zdl_user,
                password=zdl_password,
                database=zdl_database
            )
            mycursor = mydb.cursor(dictionary=True)
            select_sql = "select downloaded from meetings where meeting_id = '" + meeting_id + "'"
            mycursor.execute(select_sql)
            myresult = mycursor.fetchall()
            for x in myresult:
                if x['downloaded'] == '1':
                    print('delete me bitch!')



def main():
    group_list = v2_get_zoom_recordings.get_zoom_group_emails()
    #v2_get_zoom_recordings.get_list_of_recordings_from_email_list(group_list)
    v2_delete_recordings_from_zoom(group_list)


if __name__ == "__main__":
    main()
import json
import mysql.connector
from zoomus import ZoomClient
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('zoom_api_key')
api_sec = os.environ.get('zoom_api_sec')
client = ZoomClient(api_key, api_sec)
zdl_host = os.environ.get('zdl_host')
zdl_user = os.environ.get('zdl_user')
zdl_password = os.environ.get('zdl_password')
zdl_database = os.environ.get('zdl_database')
cm = "', '"


def insert_all_rooms_to_zdb(room_list):
    mydb = mysql.connector.connect(
        host=zdl_host,
        user=zdl_user,
        password=zdl_password,
        database=zdl_database
    )
    mycursor = mydb.cursor(dictionary=True)
    for x in room_list['rooms']:
        zoom_id = x['id']
        room_id = x['room_id']
        name = x['name']
        loc_id = x['location_id']
        try:
            act_code = x['activation_code']
        except KeyError:
            act_code = "No current Value"
        status= x['status']
        insert_sql = "insert into zoom_rooms (zoom_id, room_id, name, loc_id, act_code, status) values " \
                     "('" + zoom_id + cm + room_id + name + cm + loc_id + cm + act_code + cm + status + "' )"
        #print(insert_sql)
        mycursor.execute(insert_sql)
        mydb.commit()


def list_rooms():
    list_of_rooms = client.room.list()
    room_list = json.loads(list_of_rooms.content)
    return room_list


def main():
    room_list = list_rooms()
    insert_all_rooms_to_zdb(room_list)


if __name__ == "__main__":
    main()
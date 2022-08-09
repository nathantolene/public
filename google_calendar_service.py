import google_calendar_api
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
utm_host = os.environ.get('utm_host')
utm_user = os.environ.get('utm_user')
utm_password = os.environ.get('utm_password')
utm_database = os.environ.get('utm_database')
now = datetime.now()
#now = now.strftime('%Y-%m-%dT%H:%M:%S-5:00')
cm = ","
cq = ",'"
qc = "',"
qcq = "','"
q = "'"


def clean_db_from_old_events():
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    select_sql = "select start_time, id from gcal"
    my_cursor.execute(select_sql)
    events = my_cursor.fetchall()
    my_database.close()
    for x in events:
        db_id = str(x['id'])
        current_now = now.strftime('%d')
        start_time = x['start_time']
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S-05:00')
        start_time_day = start_time.strftime('%d')
        if current_now != start_time_day:
            remove_event_if_updated(db_id)


def check_if_recurring_id_in_db(recurring_id):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    select_sql = "select id from gcal where recurring_id = " + q + recurring_id + q
    my_cursor.execute(select_sql)
    response = my_cursor.fetchall()
    my_database.close()
    #print(response)
    if not response:
        return False
    else:
        return response


def remove_event_if_updated(db_id):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    delete_sql = "delete from gcal where id = " + db_id
    my_cursor.execute(delete_sql)
    my_database.commit()
    my_database.close()


def get_calendar_events():
    events = google_calendar_api.get_events_from_gcal()
    #print(events)
    return events


def put_event_in_database(event):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    now = str(datetime.now())
    gcal_id = event['id']
    summary = event['summary']
    try:
        description = event['description']
    except KeyError:
        description = ''
    location = event['location']
    start_time = event['start']['dateTime']
    st_tz = event['start']['timeZone']
    end_time = event['end']['dateTime']
    et_tz = event['end']['timeZone']
    try:
        recurring_id = event['recurringEventId']
    except KeyError:
        recurring_id = ''
    updated = event['updated']
    insert_sql = "insert into gcal(gcal_id, " \
                 "summary, " \
                 "description, " \
                 "location, " \
                 "start_time, " \
                 "st_tz, " \
                 "end_time, " \
                 "et_tz, " \
                 "recurring_id, " \
                 "updated, " \
                 "datetime) values(" + \
                 q + gcal_id + qcq + summary + qcq + description + qcq + location + qcq + start_time + \
                 qcq + st_tz + qcq + end_time + qcq + et_tz + qcq + recurring_id + qcq + updated + qcq + now + q + ")"
    #print(insert_sql)
    my_cursor.execute(insert_sql)
    my_database.commit()
    my_database.close()


def check_for_changes_to_events(events):
    my_database = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    my_cursor = my_database.cursor(dictionary=True)
    #print(current_events)
    for z in events:
        check = ''
        try:
            recurring_id = z['recurringEventId']
            check = check_if_recurring_id_in_db(recurring_id)
        except KeyError:
            pass
        #print('r_id', recurring_id)
        updated = z['updated']
        #print(check[0]['id'])
        if not check:
            put_event_in_database(z)
        else:
            db_id = str(check[0]['id'])
            select_sql = "select updated from gcal where id = " + q + db_id + q
            my_cursor.execute(select_sql)
            row = my_cursor.fetchall()
            #print(row[0]['updated'])
            if row[0]['updated'] != updated:
                remove_event_if_updated(db_id)
                put_event_in_database(z)
            else:
                continue
    my_database.close()


def main():
    google_calendar_api.get_calendar_service()
    events = get_calendar_events()
    check_for_changes_to_events(events)
    clean_db_from_old_events()


if __name__ == "__main__":
    main()
import database_maker
import zoom_api
import arrow

parser = "', '"


def get_monthly_zoom_meetings():
    current_day = arrow.utcnow().format('YYYY-MM-DD')
    past_month = arrow.utcnow().shift(months=-1).format('YYYY-MM-DD')
    select_rooms_zr_host = 'select zr_hostname from rooms where zr_hostname is not null'
    zr_hosts = database_maker.mysql_select(select_rooms_zr_host)
    for x in zr_hosts:
        userId = x['zr_hostname']
        result = zoom_api.get_room_usage_report(userId, past_month, current_day)
        # print(result)
        for y in result['meetings']:
            # print(y)
            topic = y['topic']
            topic = topic.replace("'", "")
            insert_meeting_info = "insert into zoom_reports (uuid, zoom_id, meeting_type, topic, user_name, user_email, " \
                                  "start_time, end_time, duration, total_minutes, participants_count, source, date) values ('" \
                                  + y['uuid'] + parser + str(y['id']) + parser + str(y['type']) + parser + topic \
            + parser + y['user_name'] + parser + y['user_email'] + parser + y['start_time'] + parser + y['end_time'] + \
            parser + str(y['duration']) + parser + str(y['total_minutes']) + parser + str(y['participants_count']) \
            + parser + y['source'] + parser + current_day + "')"
            # print(insert_meeting_info)
            database_maker.mysql_insert(insert_meeting_info)


def main():
    get_monthly_zoom_meetings()


if __name__ == "__main__":
    main()

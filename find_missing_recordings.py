import os
import thk
from v2_get_zoom_recordings import check_for_shared_screen_with_speaker_view, move_active_speaker_to_upload_dir
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('zdl_host')
user = os.environ.get('zdl_user')
password = os.environ.get('zdl_password')
database = os.environ.get('zdl_database')


def find_non_shared_screen_recordings():
    select_sql = "select meeting_id from recordings"
    result = thk.mysql_select(select_sql, host, user, password, database)
    for x in result:
        meeting_id = x['meeting_id']
        check = check_for_shared_screen_with_speaker_view(meeting_id)
        if not check:
            # check2 = move_active_speaker_to_upload_dir(meeting_id)
            select_sql = "select topic from meetings where meeting_id ='" + meeting_id + "'"
            result2 = thk.mysql_select(select_sql, host, user, password, database)
            for y in result2:
                print(y, meeting_id)

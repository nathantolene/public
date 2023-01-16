import threading

import zoom_api
import google_calendar_api
import cisco
import threading as thread
import time
import concurrent.futures


def get_google_calendar_info(g_cal_events):
    time.sleep(60)
    events = google_calendar_api.get_events_from_gcal()
    g_cal_events.append(events)
    print(g_cal_events)
    return g_cal_events


def current_zoom_events(zoom_events):
    time.sleep(10)
    events = zoom_api.list_all_zoom_meetings()
    zoom_events.append(events)
    print(zoom_events)
    return zoom_events




while True:
    g_cal_events = []
    zoom_events = []
    #cal = threading.Thread(target=get_google_calendar_info(g_cal_events), daemon=True)
    #print(g_cal_events)
    #z_event = threading.Thread(target=current_zoom_events(zoom_events), daemon=True)
    #print(zoom_events)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(get_google_calendar_info(g_cal_events), range(1))
        executor.map(current_zoom_events(zoom_events), range(1))
    #print(g_cal_events)
    #print(zoom_events)
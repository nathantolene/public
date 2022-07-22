import os
import syslog
import requests
import xmltodict
from lxml.etree import tostring
from lxml.builder import E

from dotenv import load_dotenv

load_dotenv()

domain = os.environ.get('domain')
path = '/status.xml'
starter = 'http://'
cisco_user = os.environ.get('cisco_user')
cisco_pass = os.environ.get('cisco_pass')
#building = 'selmer'
#room = '104'
post_path = '/putxml'
get_path = '/getxml?location='


def join_call(building, room, sip_number, passcode):
    sip_number = str(sip_number)
    if passcode:
        sip_number = sip_number + '.' + passcode
    if not passcode:
        sip_number = sip_number
    xml_string = tostring(E.Command(E.Dial(E.Number(sip_number))),
                          pretty_print=True, xml_declaration=True, encoding='utf-8')
    #print(xml_string)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    syslog.syslog('Connecting' + building + ' ' + room)
    #print(post.content)
    return post


def get_current_sip_number(building, room):
    string = '/Status/Call'
    gather = starter + building + room + domain + get_path + string
    print(gather + string)
    response = requests.get(gather, auth=(cisco_user, cisco_pass))
    print(response.content)
    data = response.content
    converted_root = xmltodict.parse(data)
    print(converted_root)
    try:
        CallbackNumber = converted_root['Status']['Call']['CallbackNumber']
        print(CallbackNumber)
        return CallbackNumber
    except KeyError:
        syslog.syslog(syslog.LOG_ALERT, building + room + " Not in a call")
        return None


def get_bookins_list(building, room):
    # xCommand Bookings List [Days: Days] [DayOffset: DayOffset] [Limit: Limit]
    # [Offset: Offset]
    string = '/Command/Bookings/List/DayOffset=0'


def disconnect_from_current_call(building, room, call_id):
    #xCommand Call Disconnect [CallId: CallId]
    xml_string = tostring(E.Command(E.Call(E.Disconnect(E.CallId(call_id)))),
                          pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(xml_string)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    syslog.syslog("Disconnecting " + building + ' ' + room)
    # print(post.content)
    return post
    pass


def get_call_id(building, room):
    string = '/Status/Call'
    gather = starter + building + room + domain + get_path + string
    #print(gather + string)
    response = requests.get(gather, auth=(cisco_user, cisco_pass))
    #print(response.content)
    data = response.content
    converted_root = xmltodict.parse(data)
    print(converted_root)
    try:
        call_id = converted_root['Status']['Call']['@item']
        syslog.syslog(syslog.LOG_ALERT,call_id + " Connected")
        print(call_id)
        return call_id
    except KeyError:
        syslog.syslog(syslog.LOG_ALERT,building + room + " Not Connected")

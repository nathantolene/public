import os
import requests
import xmltodict
import xml.etree.ElementTree as ET
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
    CallbackNumber = converted_root['Status']['Call']['CallbackNumber']
    print(CallbackNumber)
    return CallbackNumber


def get_bookins_list(building, room):
    # xCommand Bookings List [Days: Days] [DayOffset: DayOffset] [Limit: Limit]
    # [Offset: Offset]
    string = '/Command/Bookings/List/DayOffset=0'


def disconnect_from_current_call(building, room, call_id):
    #xCommand Call Disconnect [CallId: CallId]
    xml_string = tostring(E.Command(E.Call(E.Disconnect(call_id))),
                          pretty_print=True, xml_declaration=True, encoding='utf-8')
    # print(xml_string)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
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
    call_id = converted_root['Status']['Call']['@item']
    print(call_id)
    return call_id

import os
import re
import syslog
import requests
import yaml
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


def load_rooms():
    with open(r'room_info.yaml') as file:
        all_rooms = yaml.full_load(file)
    #print(all_rooms)
    return all_rooms


def delete_contact(building, room, cId):
    #xml_string = tostring(E.Command(E.Phonebook(E.Contact(E.Add('Name:"' + cname + '" Number: "' + cnumber + '"' )))))
    xml_string = tostring(E.Command(E.Phonebook(E.Contact(E.Delete(E.ContactId(cId))))))
    print(xml_string)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    return post.status_code


def add_contact(building, room, cname, cnumber):
    #xml_string = tostring(E.Command(E.Phonebook(E.Contact(E.Add('Name:"' + cname + '" Number: "' + cnumber + '"' )))))
    xml_string = tostring(E.Command(E.Phonebook(E.Contact(E.Add(E.Name(cname), E.Number(cnumber))))))
    print(xml_string)
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    return post


def phonebook_search(building, room):
    xml_string = tostring(E.Command(E.Phonebook(E.Search())))
    gather = starter + building + room + domain + post_path
    post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
    data = post.content
    #print(data)
    converted_root = xmltodict.parse(data)
    print(converted_root)
    try:
        contacts = converted_root['Command']['PhonebookSearchResult']['Contact']
    except KeyError:
        return False
    clist = []
    try:
        for x in contacts:
            contact = {}
            cId = x['ContactId']
            cName = x['Name']
            cNumber = x['ContactMethod']['Number']
            pattern = r"[0-9]+"
            #print(re.findall(pattern, cId))
            #cId = re.findall(pattern, cId)
            #contact = {'cid:' + cId, 'name:' + cName, 'number:' + cNumber }
            contact['cid'] = cId
            contact['name'] = cName
            contact['number'] = cNumber
            clist.append(contact)
    except TypeError:
        contact = {}
        cId = contacts['ContactId']
        cName = contacts['Name']
        cNumber = contacts['ContactMethod']['Number']
        contact['cid'] = cId
        contact['name'] = cName
        contact['number'] = cNumber
        clist.append(contact)
    #print(clist)
    #cId = converted_root['Command']['PhonebookSearchResult']['Contact']['ContactId']
    #print(cId)
    return clist


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
    syslog.syslog('Connecting ' + building + ' ' + room + " to " + sip_number)
    #print(post.content)
    return post


def get_current_sip_number(building, room):
    string = '/Status/Call'
    gather = starter + building + room + domain + get_path + string
    #print(gather + string)
    response = requests.get(gather, auth=(cisco_user, cisco_pass))
    #print(response.content)
    data = response.content
    converted_root = xmltodict.parse(data)
    #print(converted_root)
    try:
        CallbackNumber = converted_root['Status']['Call']['CallbackNumber']
        #print(CallbackNumber)
        CallbackNumber = re.findall('\d{10,11}', CallbackNumber)
        return CallbackNumber[0]
    except KeyError:
        syslog.syslog(building + room + " Not in a call")
        return None


def get_bookins_list(building, room):
    # xCommand Bookings List [Days: Days] [DayOffset: DayOffset] [Limit: Limit]
    # [Offset: Offset]
    string = '/Command/Bookings/List/DayOffset=0'


def disconnect_from_current_call(building, room, call_id):
    #xCommand Call Disconnect [CallId: CallId]
    try:
        xml_string = tostring(E.Command(E.Call(E.Disconnect(E.CallId(call_id)))),
                              pretty_print=True, xml_declaration=True, encoding='utf-8')
        # print(xml_string)
        gather = starter + building + room + domain + post_path
        post = requests.post(gather, data=xml_string, auth=(cisco_user, cisco_pass))
        syslog.syslog("Disconnecting " + building + ' ' + room)
        # print(post.content)
        return post
    except TypeError:
        syslog.syslog(building + room + " Already Disconnected")


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
        syslog.syslog("Call id = " + call_id)
        print(call_id)
        return call_id
    except KeyError:
        syslog.syslog(syslog.LOG_ALERT,building + room + " Not Connected")


def delete_all_contacts_for_all_rooms():
    all_rooms = load_rooms()
    for y in all_rooms:
        if y['room_type'] == 'cisco':
            building = y['building']
            room = y['room']
            cList = phonebook_search(building, room)
            for x in cList:
                cId = x['cid']
                delete_contact(building, room, cId)


def delete_all_contacts_for_room(building, room):
    print(building, room)
    all_rooms = load_rooms()
    for y in all_rooms:
        if y['room_type'] == 'cisco':
            rooms_building = y['building']
            rooms_room = y['room']
            if building == rooms_building and rooms_room == room:
                cList = phonebook_search(building, room)
                if cList is False:
                    continue
                print(cList)
                for x in cList:
                    cId = x['cid']
                    delete_contact(building, room, cId)

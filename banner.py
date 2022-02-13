import oauthlib
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
import urllib, json, requests
from time import sleep
import mysql.connector
import os
import banner_insert
from dotenv import load_dotenv

load_dotenv()

utm_host = os.environ.get('host')
utm_user = os.environ.get('dbuser')
utm_password = os.environ.get('dbpass')
utm_database = os.environ.get('db')
banner_api_base = os.environ.get('banner_api_base')

# CURRENT TERM CODE #
# !!!!!!!!!!!!!!!!! #
thisTerm = "202220"
# !!!!!!!!!!!!!!!!! #


def getTimes(bldg, room, term):
   ## print(bldg, room, term)
    try:
        apiURL = banner_api_base + bldg + "&room=" + room + "&term=" + term
        try:
            oauth = OAuth2Session(client_id=credentials['client_id'],  token=credentials['token'])
            r = oauth.get(apiURL)
        except TokenExpiredError as e:
            print(e)
            oauth = newToken()
        finally:
            try:
                r = oauth.get(apiURL)
            except Exception as e:
                print(e)
                exit()
        #print(r)
        d = r.json() # it's a dict!
        # print(formatJSON(d))
        #sleep(1)

        return d
    except Exception as e:
        print("@getTimes:", str(e))

#
#
def newToken():
    try:
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        credentials['token'] = oauth.fetch_token(
            token_url=credentials['token_uri'],
            access_token=credentials['token'],
            client_id=client_id,
            client_secret=client_secret
        )
        #print("\n\nBanner token renewed.\n\n")
        writeJSON("bannerCreds.json", credentials)
        return oauth
    except Exception as e:
        print("@newToken:", str(e))


def writeJSON(filename, d):
    # Writes dict to JSON file
    # Inputs: JSON filename, dict
    with open(filename, 'w') as json_write:
        json.dump(d, json_write)


def readJSON(filename):
    # Loads JSON file into dict
    # Inputs: JSON filename
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def formatJSON(d):
    # Formats a dict for pretty
    return json.dumps(d, sort_keys=False, indent=4)


def getAllTimes(b):
    newToken()
    try:
        #classes = {"rooms": [{"bldg": building["code"], "room": building["room"]} for building in b["buildings"]],
        #           "classes": []}

        #for c in classes["rooms"]:
        #    classes["classes"].append(getTimes(c["bldg"], c["room"], thisTerm))
        #    print("Got classes for " + c["bldg"], c["room"])

        #return classes["classes"]
        classes = []
        for x in b:
            bldg = x['code']
            room = x['room']
            term = thisTerm
            # print(bldg + room + term)
            classes.append(getTimes(bldg, room, term))
        #print(classes)
        return classes
    except Exception as e:
        print("@getAllTimes:", str(e))


try:
    credentials = readJSON("bannerCreds.json")
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
except Exception as e:
        print("@banner_main:", str(e))


if __name__ == "__main__":
    #b = readJSON('buildings.json')
    b = banner_insert.list_it()
    #print(b)
    events = getAllTimes(b)
    #print(events)
    banner_insert.banner_info_insert(events)
    #writeJSON('banner.txt', events)

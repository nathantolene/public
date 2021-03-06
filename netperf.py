#!/usr/bin/python3
import os
import subprocess
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

utm_host = os.environ.get('host')
utm_user = os.environ.get('dbuser')
utm_password = os.environ.get('dbpass')
utm_database = os.environ.get('db')
netperf_server = os.environ.get('netperf_server')
netperf_command = 'netperf -H ' + netperf_server + ' -t TCP_RR -w 10ms --  -o min_latency,max_latency,mean_latency'


def insert_info():
    sp = subprocess.Popen(netperf_command, shell=True, stdout=subprocess.PIPE)
    f = sp.stdout.readlines()
    # f = str(f)
    print(f)
    # f = f.split("b'")
    # print(f)
    l = len(f)
    print(f[3])
    list = []
    g = str(f[3])
    h = g.split(',')
    for x in h:
        list.append(x)
        print(x)
    print(list)
    minilatms = list[0][2:]
    print(minilatms)
    maxlatms = list[1]
    print(maxlatms)
    meanlatms = list[2][:-3]
    print(meanlatms)
    mk = "'"
    cm = "', '"
    mydb = mysql.connector.connect(
        host=utm_host,
        user=utm_user,
        password=utm_password,
        database=utm_database
    )
    mycursor = mydb.cursor(dictionary=True)
    insert_sql = "insert into netperf (minilatms, maxlatms, meanlatms) values (" + mk + minilatms + cm \
                 + maxlatms + cm + meanlatms + mk + ")"
    print(insert_sql)
    mycursor.execute(insert_sql)
    mydb.commit()


insert_info()

#coding=utf-8
import serial
import datetime
import platform
import pymysql
import threading
import socket
import configparser
import os
from concurrent.futures import ThreadPoolExecutor as Pool

#cur_path = os.path.dirname(os.path.realpath(__file__))
#config_path = os.path.join(cur_path,'config.ini')
conf = configparser.ConfigParser()
config_path = "C:/Users/jinp.jiang/Desktop/python/config.ini"
conf.read(config_path)

#Sync information
synchronizationID = conf.get('SyncID','synchronizationID')
triggerID = conf.get('SyncID','trigger_category_id')
port = int(conf.get('SyncID','port'))
duration = conf.get('SyncID','duration')
#Mysql information
myhost = conf.get('MYSQL','myhost')
myport = int(conf.get('MYSQL','myport'))
myuser = conf.get('MYSQL','myuser')
mypasswd = conf.get('MYSQL','mypasswd')
mydb = conf.get('MYSQL','mydb')

def sendDatatoBS(ip):
    port = 2324
    body = '<rc version="8" id="1" pre_buffer="0" synchronization_role="2" synchronization_set="{}" action="trigger" trigger_category_id="{}" duration="{}"/>\r\n\r\n'
    xmlfile = body.format(synchronizationID,triggerID,duration)
    print("sendHost:",ip,"\n\n","prot:",port,"\n\n","body:",xmlfile)    
    address = (ip,port) 
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(address)
    sendData = xmlfile.encode('utf-8')
    print("sendData：",sendData)
    client.send(sendData)
    #client.send(str.encode(xmlfile))
    #print(str.encode(xmlfile))
    #client.sendto(sendData,("ip",port))
    #clinet = socket(AF_INET,SOCK_DGRAM)
    feedback = client.recv(2048)
    print("feedback:",feedback)
    client.close()

def MDCIPList():
    conn = pymysql.connect(host=myhost,port=myport,user=myuser,passwd=mypasswd,db=mydb)
    cur = conn.cursor()
    cur.execute("""select IP from PlayerInfoDetails where Hostname = 'CN-STS-LX0114' """)
    playerIPList = cur.fetchone()
    print("\nList:",playerIPList,"\n")
    conn.commit()
    cur.close()
    conn.close()    
    return playerIPList

def concurrent():
    playerList = MDCIPList()
    #print(playerList[0])
    #sendDatatoBS(playerList[0])
    pool = Pool(max_workers=1)
    pool.map(sendDatatoBS,playerList)

def timerFun(scheduleTimer):
    print (scheduleTimer)
    flag = 0
    while True:
        now = datetime.datetime.now().replace(microsecond=0)
        #print (now)
        #now = datetime.datetime.now()
        if now == scheduleTimer and flag != 1:
            print (now)
            concurrent()
            flag = 1
        else:
            if flag == 1:
                scheduleTimer = scheduleTimer + datetime.timedelta(seconds=10)
                flag = 0

def serailSignal():
    sint = serial.Serial('/dev/ttyS0',9600,timeout=0.5)
    data = ''
    while True:
        while sint.inWaiting() > 0: 
            data += sint.read(1) 
        if data != '': 
            print (data)
            concurrent()

def serailSignal():
    now = datetime.datetime.now().replace(microsecond=0)
    sint = serial.Serial('/dev/ttyS0',9600,timeout=0.5)
    sint.flushInput()
    while True:
        data = sint.inWaiting()
        if data != 0:
            recv = sint.read(sint.in_waiting).decode("gkb")
            print (now,"---recv---",recv)
            concurrent()
        datetime.sleep(0.1)

if __name__ == '__main__':
    #scheduleTimer = datetime.datetime(2021,1,26,11,39,10)
    #print("run the timer task at {}".format(scheduleTimer))
    #timerFun(scheduleTimer)
    concurrent()
    #serailSignal()
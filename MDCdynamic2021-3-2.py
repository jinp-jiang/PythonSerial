#coding=utf-8
import sqlite3
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
#conf = configparser.ConfigParser()
#config_path = "./config.ini"
#conf.read(config_path)

#Sync information for ini
#synchronizationID = conf.get('SyncID','synchronizationID')
#triggerID = conf.get('SyncID','trigger_category_id')
#port = int(conf.get('SyncID','port'))
#duration = conf.get('SyncID','duration')
#Mysql information
#myhost = conf.get('MYSQL','myhost')
#myport = int(conf.get('MYSQL','myport'))
#myuser = conf.get('MYSQL','myuser')
#mypasswd = conf.get('MYSQL','mypasswd')
#mydb = conf.get('MYSQL','mydb')

#Sync information for redundant
#def info():
conn = sqlite3.connect('/home/STD-MO/Dynamic.db')
print("Opened database successfully")
c = conn.cursor()
c.execute('''select * from info''')
data = c.fetchall()
print(data)
playerIP = data[0][1]
campaignID = data[0][2]
adcopyID = data[0][3]
triggerID = data[0][4]
synchronizationID = data[0][5]
startTime = data[0][6]
endTime = data[0][7]
duration = data[0][8]
print(playerIP,campaignID,adcopyID,triggerID,synchronizationID,startTime,endTime,duration)
conn.commit()
conn.close()
#   return data
    
def record(triggerID):
    conn = sqlite3.connect('/home/STD-MO/Dynamic.db')
    print("Opened database successfully")
    c = conn.cursor()
    c.execute('''select adcopyID from info where triggerID = {}'''.format(triggerID))
    adcopyID = c.fetchall()
    adcopyID = adcopyID[0][0]
    now = datetime.datetime.now().replace(microsecond=0)
    c.execute('''insert into record(adcopyID,timestamp) values ('{}','{}')'''.format(int(adcopyID),now))
    print('Add record +1')
    conn.commit()
    conn.close()

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
    record(triggerID)

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
    #playerList = MDCIPList()
    #print(playerList[0])
    #sendDatatoBS(playerList[0])
    #pool = Pool(max_workers=1)
    #pool.map(sendDatatoBS,playerList)
    ip = "127.0.0.1"
    sendDatatoBS("127.0.0.1")

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

def serailSignal2():
    x=serial.Serial('/dev/ttyS0',9600,timeout=1)
    print(x.inWaiting())
    while True:
        while x.inWaiting()>0:
            myout=x.read(7)
            print(myout.decode('gbk'))
            data = myout.decode('gbk')
            datas=''.join(map(lambda x:('/x' if len(hex(x))>=4 else '/x0')+hex(x)[2:],myout))
            print(datas)
            new_datas=datas[2:].split('/x')
            print(new_datas)
            if data == "abcdefg":
                now = datetime.datetime.now().replace(microsecond=0)
                start = datetime.datetime.strptime(str(startTime),"%Y-%m-%d %H:%M:%S")
                end = datetime.datetime.strptime(str(endTime),"%Y-%m-%d %H:%M:%S")
                if start <= now <= end:
                    concurrent()
                    sleepTime = duration/1000
                    print(sleepTime,type(sleepTime))
                    time.sleep(sleepTime)
                else:
                    print("date error")
            else:
                print("info error")
    
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
    serailSignal2()
    #record()
    #concurrent()

#coding=utf-8
import serial
import binascii
import time
import datetime
import sys

x=serial.Serial('/dev/ttyS0',9600,timeout=1)
def faSong():
    while True:
        #time.sleep(1)
        now = datetime.datetime.now().replace(microsecond=0)
        print(now)
        myinput=bytes([0X01,0X03,0X00,0X00,0X00,0X01,0X84,0X0A])
        x.write(myinput)
        x.write(b'hello')
        print(x.readline())

if __name__ == '__main__':
    faSong()    

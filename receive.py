#coding=utf-8
import serial
import binascii
import time
import sys
def testSerial():
    while True:
        #ser = serial.Serial('/dev/ttyS0',9600,bytesize=8, parity='N', stopbits=1,timeout=20)
        ser  = serial.Serial('/dev/ttyS0',9600,timeout=0.5)
        if(ser.isOpen()):
            print('opend')
        else:
            print('unopen')
        #while ser.read(5)!= b'READY': pass
        ser.write("Hello word".encode('utf-8'))
        print(ser.readline())
        ser.close()

x=serial.Serial('/dev/ttyS0',9600,timeout=1)
def jieShou():
    print(x.inWaiting())
    while True:
        while x.inWaiting()>0:
            myout=x.read(7)
            print(myout.decode('gbk'))
            datas=''.join(map(lambda x:('/x' if len(hex(x))>=4 else '/x0')+hex(x)[2:],myout))
            print(datas)
            new_datas=datas[2:].split('/x')
            print(new_datas)

if __name__ == "__main__":
    jieShou()

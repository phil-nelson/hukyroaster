#!/usr/bin/python

import sys
import serial
import os
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
arduinoPort = None
for p in ports:
    #if 'Arduino' in p[1]:
    arduinoPort = p[0]
    print p[1] + ' found at ' + p[0]
    #break

if (arduinoPort is None):
    print "Arduino not connected?"
    sys.exit(-1)

arduino = serial.Serial(arduinoPort, 9600, timeout=2)

FIFO_READ = os.path.dirname(os.path.realpath(__file__)) + '/in.fifo'
FIFO_WRITE = os.path.dirname(os.path.realpath(__file__)) + '/out.fifo'

def sendToArduino(str):
    arduino.write(str)

def readFromArduino():
    l = arduino.readline()
    print("Got response: '" + l.strip() + "'")
    return l

def fifoSend(str):
    writer.write(str)
    writer.flush()

def readkPa():
    return open('kpa.txt').read().strip()

def parseCmd(cmd):
    print "Got command: '%s'" % cmd
    try:
        cmd, val = cmd.split(':')
    except ValueError:
        print "Bad command!";
        return

    if (cmd == 'FAN'):
        val = int(int(val) * 2.54)
        sendToArduino("FAN:%d\n" % val)
    elif (cmd == 'TMP'):
        sendToArduino("TMP:0\n")
        fifoSend(readFromArduino().strip() + ',' + readkPa() + ',0.0\n')
    elif (cmd == 'KPA'):
        sendToArduino("KPA:%s\n" % val)
    elif (cmd == 'MTR'):
        sendToArduino("MTR:%s\n" % val)
    elif (cmd == 'MZR'):
        sendToArduino("MZR:0\n")
    elif (cmd == 'KPQ'):
        sendToArduino('KPQ:0\n')
        response = readFromArduino().strip()
        #print "Current position %s" % response
        fifoSend(response + '\n')


if not os.path.exists(FIFO_READ):
    os.mkfifo(FIFO_READ)
if not os.path.exists(FIFO_WRITE):
    os.mkfifo(FIFO_WRITE)

writer = open(FIFO_WRITE, 'w+')

while True:
    with open(FIFO_READ) as reader:
        print 'got line!'
        parseCmd(reader.readline())

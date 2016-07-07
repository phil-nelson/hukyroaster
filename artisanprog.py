#!/usr/bin/python

import os
import sys

FIFO_WRITE = os.path.dirname(os.path.realpath(__file__)) + '/in.fifo'
FIFO_READ = os.path.dirname(os.path.realpath(__file__)) + '/out.fifo'

def sendCommand(str):
    writer = open(FIFO_WRITE, 'w')
    writer.write(str)
    writer.close()

def sendCommandAndGetResponse(str):
    reader = open(FIFO_READ, 'r')
    sendCommand(str)
    line = reader.readline()
    reader.close()
    return line

def loadkPaPositions():
    f = open(os.path.dirname(os.path.realpath(__file__)) + '/kPaPositions.txt', 'r')
    kPaPositions = {}
    for line in f:
        parts = line.split(':', 2)
        kPaPositions[float(parts[0])] = parts[1].strip()
    f.close()
    print "kPaPositions:"
    print kPaPositions
    return kPaPositions

if (len(sys.argv) == 1 or sys.argv[1] == 'TMP'):
    print sendCommandAndGetResponse("TMP:0").strip()
elif (sys.argv[1] == 'FAN'):
    sendCommand("FAN:%s" % sys.argv[2])
elif (sys.argv[1] == 'KPA'):
    kPaPositions = loadkPaPositions()
    sendCommand("KPA:%s" % kPaPositions[float(sys.argv[2])])
else:
    print "Unknown command!"

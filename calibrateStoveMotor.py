#!/usr/bin/python

import os
import sys
import tty, termios
import pickle

FIFO_WRITE = os.path.dirname(os.path.realpath(__file__)) + '/in.fifo'
FIFO_READ = os.path.dirname(os.path.realpath(__file__)) + '/out.fifo'

def sendCommand(str):
    writer = open(FIFO_WRITE, 'w')
    writer.write(str)
    writer.close()

def sendCommandAndGetResponse(str):
    reader = open(FIFO_READ, 'r')
    sendCommand(str)
    return reader.readline()

def getKeyPress():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def turn():
    print "1: full, 2: half, 3: quarter, 4: 1/8, 5: -full, 6: -half, 7: -quarter, 8: -1/8\n"

    positions = {1: '4076', 2: '2038', 3: '1019', 4: '510', 5: '-3000', 6: '-1500', 7: '-500', 8: '-250'}
    while (True):
        ch = getKeyPress()
        if (ord(ch) == 13):
            break
        try:
            num = int(ch)
        except ValueError:
            print "Invalid key!";
            continue

        if num not in positions:
            print "Invalid key!"
            continue
        steps = positions[int(ch)]
        sendCommand("MTR:" + steps + "\n")
        print "MTR:" + steps

kPas = [1, 1.5, 2, 2.5, 3, 3.5, 4]

kPaPositions = {}
for i in kPas:
    print "Set stove at %.1f kPa" % i
    turn()
    pos = sendCommandAndGetResponse("KPQ:0")
    print "Got position: " + pos.strip()
    kPaPositions[i] = pos.strip()

print kPaPositions
outfile = open('kPaPositions.pkl', 'wb')
pickle.dump(kPaPositions, outfile)
outfile.close()

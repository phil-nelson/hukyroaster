#!/usr/bin/python

'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from SimpleCV import *

def getImage(crop = False):
    img = cam.getImage()
    #img = Image('test.jpg')
    return img if not crop else img.crop(bb[0], bb[1], bb[2], bb[3])

# Let user draw a bounding box to crop to, returns bounding box
def getBoundingBox():
    downPos = 0
    upPos = 0
    state = 'INIT'
    while (disp.isNotDone()):
        img = getImage()
        down = disp.leftButtonDownPosition()
        up = disp.leftButtonUpPosition()

        if (down is not None):
            state = 'DRAWING_RECT'
            downPos = down
        if (up is not None):
            state = 'RECT_DRAWN'
            upPos = up

        if (state == 'RECT_DRAWN'):
            return disp.pointsToBoundingBox(upPos, downPos)
        elif (state == 'DRAWING_RECT'):
            bb = disp.pointsToBoundingBox(downPos, (disp.mouseX, disp.mouseY))
            img.drawRectangle(bb[0], bb[1], bb[2], bb[3], color=Color.GREEN, width=5)
        else:
            img.drawLine((disp.mouseX, 0), (disp.mouseX, img.height), color=Color.BLUE)
            img.drawLine((0, disp.mouseY), (img.width, disp.mouseY), color=Color.BLUE)
            img.drawText("Click and drag box surrounding gauge", 10, 10)

        img.save(disp)

# Get hue value of clicked pixel
def getClickedPixelHue():
    while (disp.isNotDone()):
        img = getImage(True)
	img.drawText("Click on the needle", 5, 5)

        up = disp.leftButtonUpPosition()
        if (up is not None):
            hsvimg = img.toHSV()
            return hsvimg.getPixel(up[0], up[1])[0]
        img.save(disp)

# Does stuff to calculate angle and draws needle blob on image
def getNeedleAngle(img):
        distimg = img.hueDistance(needleHue).stretch(0, 50).binarize()
        blobs = distimg.findBlobs()
        if (blobs is None):
            return -1
        blobs = blobs.sortArea()
        blobs[-1].drawOutline(layer=img.getDrawingLayer(), color=(255,0,0))
        return int(round(blobs[-1].angle() / 5.0) * 5.0)

# Ask user to place needle at different kPa angles and store angle/kPa values
def calibratekPaAngles():
    kPas = [0, 1, 1.5, 2, 2.5, 3, 3.5, 4]
    kPaAngles = {}
    for i in kPas:
        while (disp.isNotDone()):
            img = getImage(True)
            angle = getNeedleAngle(img)
            img.drawText("Place needle at %.1f kPa and click anywhere when done" % i, 10, 30)
            img.drawText("Angle: %d" % (angle), 10, 10)
            up = disp.leftButtonUpPosition()
            if (up is not None):
                kPaAngles[angle] = i
                break
            img.save(disp)
    return kPaAngles

# Monitor the needle, find angle/kPa, write to file
def doIt():
    img = getImage(True)
    disp = Display(img.size())
    while (disp.isNotDone()):
        img = getImage(True)
        angle = getNeedleAngle(img)
        kPa = -1 if angle == -1 else findkPa(angle)
        for i in kPaAngles:
            img.drawText("%d kPa: %.1f" % (kPaAngles[i], i), 2, 15 * kPaAngles[i])
        img.drawText("%.1f kPa" % kPa, color=(255,255,0), fontsize=24)
        img.drawText("Angle: %d" % angle, img.width - 60, 10, color=(0,255,0))
        img.save(disp)
        f = open('kpa.txt', 'w')
        f.write("%.1f\n" % kPa)
        f.close()
        time.sleep(1)

# Returns the closest kPa value to angle
def findkPa(angle):
    return kPaAngles[angle] if angle in kPaAngles else kPaAngles[min(kPaAngles.keys(), key=lambda k: abs(k - angle))]

cam = Camera(1)
img = getImage()
disp = Display(img.size())
bb = getBoundingBox()
needleHue = getClickedPixelHue()
kPaAngles = calibratekPaAngles()
print kPaAngles
doIt()

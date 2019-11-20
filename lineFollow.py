# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2 as cv
import maestro
import numpy as np

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

width = 256   #640
height = 256  #480

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(width, height))

newWidth = width
newHeight = int(0.4*height)
centerX = int(width/2)

def nothing(c):
    None

def getColors(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(hsv[y, x])

class controls():
    def __init__(self):
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.motors = 6000
        self.turn = 6000

    # Change head tilt
    def tilt(self, angle):
        self.headTilt = angle
        if(self.headTilt > 7900):
            self.headTilt = 7900
        if(self.headTilt < 1510):
            self.headTilt = 1510
        self.tango.setTarget(HEADTILT, self.headTilt)

    # Change drive speed
    # speed < 6000 is forward, speed > 6000 is reverse
    def drive(self, speed):
            self.motors = speed
            if(self.motors > 7900):
                self.motors = 7900
            if(self.motors < 1510):
                self.motors = 1510
            self.tango.setTarget(MOTORS, self.motors)

    # Change rotation speed
    # speed < 6000 turns right, speed > 6000 turns left
    def rotate(self, speed):
        self.turn = speed
        if(self.turn > 7400):
            self.turn = 7400
        if(self.turn < 2110):
            self.turn = 2110
        self.tango.setTarget(TURN, self.turn)

control = controls()
control.tilt(1510)

# Calculate "Center of Gravity" of image
def calcCOG(pic):
    totX = 0
    totY = 0
    cogX = 0
    cogY = 0
    count = 0

    for y in range(0, newHeight):
        for x in range(0, newWidth):
            if pic[y][x] == 255:
                totX = totX + x
                totY = totY + y
                count = count + 1

    # If no white pixels found, set cog's to large out
    # of bounds number so robot will stop
    if totX == 0 and totY == 0:
        cogX = 99999
        cogY = 99999

    if count != 0:
        cogX = totX / count
        cogY = totY / count

    return cogX, cogY


def navigate(cog):
    # If cog = 99999, robot sees nothing and stops
    if cog == 99999:
        control.drive(6000)
        control.rotate(6000)
        print("STOP")
    else:
        # Robot needs to turn right
        if cog - centerX > 25 and cog - centerX < 50:
            control.rotate(5000)
            print("right")
        elif cog - centerX >= 50:
            control.rotate(5000)
            print("right")

        # Robot needs to turn left
        if cog - centerX < -25 and cog - centerX > -50:
            control.rotate(7000)
            print("left")
        elif cog - centerX <= -50:
            control.rotate(7000)
            print("left")

        # Go straight
        if cog - centerX >= -25 and cog - centerX <= 25:
            control.drive(4950)
            print("straight")


# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    image = frame.array
    crop = image[height-newHeight:height, 0:width]
    pic = crop.copy()
    pic = cv.cvtColor(pic, cv.COLOR_BGR2HSV)
    hsv = pic.copy()
    pic = cv.inRange(pic, (24, 55, 200), (35, 150, 255))
    #pic = cv.normalize(crop, None, 0, 255, cv.NORM_MINMAX)
    pic = cv.GaussianBlur(pic, (21,21), 0)
    pic = cv.Canny(pic, 100, 170)

    # Calculate center of gravity
    x, y = calcCOG(pic)
    print("cogX = ", x, "   cogY = ", y)

    navigate(x)
    time.sleep(1)

    control.drive(6000)
    control.rotate(6000)

    # show the frame
    #cv.imshow("Frame", pic)

    #cv.setMouseCallback("Frame", getColors)
    key = cv.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break

cv.destroyAllWindows()

control.drive(6000)
control.rotate(6000)
control.tilt(6000)

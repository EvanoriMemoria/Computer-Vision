import client
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2 as cv
import numpy as np
import maestro
import time

IP = '10.200.22.237'
PORT = 5010
cl = client.ClientSocket(IP, PORT)
cl.start()

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

upFlag = 0
sideFlag = 0
foundFace = False
centered = False
bodyCentered = False
xCent = False
yCent = False
humanFound = False

timer = None

width = 640
height = 480

face_cascade = cv.CascadeClassifier('data/haarcascade_frontalface_default.xml')

camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(width, height))

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

    # Change head turn
    def hTurn(self, angle):
        self.headTurn = angle
        if(self.headTurn > 7900):
            self.headTurn = 7900
        if(self.headTurn < 1510):
            self.headTurn = 1510
        self.tango.setTarget(HEADTURN, self.headTurn)

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

    def reset(self):
        self.tango.setTarget(BODY, 6000)
        self.tango.setTarget(HEADTURN, 6000)
        self.tango.setTarget(TURN, 6000)
        self.tango.setTarget(MOTORS, 6000)

control = controls()
#control.tilt(headTilt+50);

def incrementTilt(faces, headTilt, headTurn):
    global upFlag
    global sideFlag
    global staticFaces

    #up and to the left
    if(upFlag == 0 and sideFlag == 0):
        control.tilt(headTilt+75)
        control.hTurn(headTurn-50)
    #right at the top
    elif(upFlag == 0 and sideFlag == 1):
        control.hTurn(headTurn+100)
    #down and to the left
    elif(upFlag == 1 and sideFlag == 0):
        control.tilt(headTilt-75)
        control.hTurn(headTurn-50)
    #right at the bottom
    elif(upFlag == 1 and sideFlag == 1):
        control.hTurn(headTurn+100)

    # All the way up to the left
    if(headTilt >= 7350 and headTurn <= 5100):
        upFlag = 0
        sideFlag = 1
    # all the way up to the right
    elif(headTilt >= 7350 and headTurn >= 6900):
        upFlag = 1
        sideFlag = 0
    # all the way down to the left
    elif(headTilt <= 4650 and headTurn <= 5100):
        upFlag = 1
        sideFlag = 1
    #all the way down to the right
    elif(headTilt <= 4650 and headTurn >= 6900):
        upFlag = 0
        sideFlag = 0

def moveToX(x):
    global xCent
    global width
    xCent = False
    centered = False

    if(x < width/2-60):
        control.hTurn(control.headTurn+120)
    elif(x > width/2+60):
        control.hTurn(control.headTurn-120)
    else:
        xCent = True

def moveToY(y):
    global yCent
    global height
    yCent = False
    #centered = False

    if(y < height/2-30):
        control.tilt(control.headTilt+150)
    elif(y > height/2+30):
        control.tilt(control.headTilt-150)
    else:
        yCent = True

def moveWheelsToFace():
    global centered
    global centerCounter
    global bodyCentered

    if(control.headTurn < 5800):
        #control.hTurn(control.headTurn+200)
        control.rotate(5000)
    elif(control.headTurn > 6200):
        #control.hTurn(control.headTurn-200)
        control.rotate(7000)
    else:
        bodyCentered = True

    if(bodyCentered == False):
        centered = False

def charge(w,h):
    faceArea = w*h
    if(faceArea > 10000):
        control.drive(7000)
    elif(faceArea < 5000):
        control.drive(5100)
    else:
        control.drive(6000)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    image = frame.array
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if(len(faces) != 0):
        foundFace = True
        if(humanFound == False):
            cl.sendData("Hello Human")
            humanFound = True
        timer = None
    else:
        if(timer == None):
            timer = time.time()
        elif(time.time()-timer >= 5):
            foundFace = False
            centered = False
            bodyCentered = False
            xCent = False
            yCent = False
            humanFound = False

    if(foundFace == False):
        incrementTilt(faces,control.headTilt,control.headTurn)

    #for (x,y,w,h) in faces:
    #    cv.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

    if(foundFace == True and centered == False):
        for (x,y,w,h) in faces:
            cv.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            rectCentX = x+w/2
            rectCentY = y+h/2
        if(len(faces) != 0):
            moveToX(int(rectCentX))
            moveToY(int(rectCentY))
        if(xCent and yCent):
            centered = True

    if(centered == True and len(faces) != 0):
        moveWheelsToFace()
        time.sleep(.3)
        control.rotate(6000)

    if(bodyCentered == True and len(faces) != 0):
        for (x,y,w,h) in faces:
            cv.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            charge(w,h)
            moveToY(y)
    else:
        control.drive(6000)

    # show the frame
    #cv.imshow("Frame", image)

    #cv.setMouseCallback("Frame", getColors)
    key = cv.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break

cv.destroyAllWindows()

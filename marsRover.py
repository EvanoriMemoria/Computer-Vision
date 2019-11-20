import client
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2 as cv
import numpy as np
import maestro
import time

IP = '10.200.4.23'
PORT = 5010
cl = client.ClientSocket(IP, PORT)
cl.start()

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

ARM1 = 6
ARM2 = 7
ARM3 = 8
ARM4 = 9
ARM5 = 10
ARM6 = 11

face_cascade = cv.CascadeClassifier('data/haarcascade_frontalface_default.xml')

width = 240   #640
height = 240  #480
state = 0

camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(width, height))

newWidth = width
newHeight = int(0.4*height)
centerX = int(width/2)

class controls():
    def __init__(self):
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.arm1 = 6000
        self.arm2 = 6000
        self.arm3 = 6000
        self.arm4 = 6000
        self.arm5 = 6000
        self.arm6 = 6000
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

    def armOne(self, angle):
        self.arm1 = angle
        if(self.arm1 > 7900):
            self.arm1 = 7900
        if(self.arm1 < 1510):
            self.arm1 = 1510
        self.tango.setTarget(ARM1, self.arm1)

    def armTwo(self, angle):
        self.arm2 = angle
        if(self.arm2 > 7900):
            self.arm2 = 7900
        if(self.arm2 < 1510):
            self.arm2 = 1510
        self.tango.setTarget(ARM2, self.arm2)

    def armThree(self, angle):
        self.arm3 = angle
        if(self.arm3 > 7900):
            self.arm3 = 7900
        if(self.arm3 < 1510):
            self.arm3 = 1510
        self.tango.setTarget(ARM3, self.arm3)

    def armFour(self, angle):
        self.arm4 = angle
        if(self.arm4 > 7900):
            self.arm4 = 7900
        if(self.arm4 < 1510):
            self.arm4 = 1510
        self.tango.setTarget(ARM4, self.arm4)

    def armFive(self, angle):
        self.arm5 = angle
        if(self.arm5 > 7900):
            self.arm5 = 7900
        if(self.arm5 < 1510):
            self.arm5 = 1510
        self.tango.setTarget(ARM5, self.arm5)

    def armSix(self, angle):
        self.arm6 = angle
        if(self.arm6 > 7900):
            self.arm6 = 7900
        if(self.arm6 < 1510):
            self.arm6 = 1510
        self.tango.setTarget(ARM6, self.arm6)

control = controls()
control.tilt(1510)

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

def line_up(pic):
    highestY = -1
    highestX = -1
    lowestY = -1
    lowestX = -1
    for y in range(0, height):
        for x in range(0, width):
            if pic[y][x] == 255:
                if highestY == -1:
                    highestY = y
                    highestX = x
                lowestY = y
                lowestX = x

    area = abs(lowestY - highestY) * abs(highestX - lowestX)

    if area < 1000:
        control.rotate(4900)
        time.sleep(1)
        control.rotate(6000)
    else:
        if lowestY-highestY > 40:
            if highestX < lowestX:
                control.rotate(4900)
                time.sleep(.5)
                control.rotate(6000)
            else:
                control.rotate(7300)
                time.sleep(.5)
                control.rotate(6000)
        else:
            control.rotate(6000)
            return True

def line_box(pic):
    highestY = -1
    highestX = -1
    lowestY = -1
    lowestX = -1
    for y in range(0, height):
        for x in range(0, width):
            if pic[y][x] == 255:
                if highestY == -1:
                    highestY = y
                    highestX = x
                lowestY = y
                lowestX = x

    area = abs(lowestY - highestY) * abs(highestX - lowestX)

    if area < 1000:
        control.rotate(4900)
        time.sleep(1)
        control.rotate(6000)
    else:
        control.rotate(6000)
        return True


def cross_area(pic,crop):
    counter = 0
    for y in range(0, newHeight):
        for x in range(0, width):
            if pic[y][x] == 255:
                counter = counter + 1
                if counter > 500:
                    break;
    print(counter)
    if(counter > 100):
        return True
    else:
        if(crop == "bot"):
            control.drive(4900)
            time.sleep(1)
            control.drive(6000)
        else:
            control.drive(4900)
            time.sleep(.5)
            control.drive(6000)

def navigate(cog):
    global width
    centerX = width/2
    # If cog = 99999, robot sees nothing and stops
    if cog == 99999:
        control.drive(6000)
        control.rotate(6000)
    else:
        # Robot needs to turn right
        if cog - centerX > 25 and cog - centerX < 50:
            control.rotate(5000)
        elif cog - centerX >= 50:
            control.rotate(5000)

        # Robot needs to turn left
        if cog - centerX < -25 and cog - centerX > -50:
            control.rotate(7000)
        elif cog - centerX <= -50:
            control.rotate(7000)

        # Go straight
        if cog - centerX >= -25 and cog - centerX <= 25:
            control.drive(4950)
    return cog

def getColors(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(hsv[y, x])

# Raise arm ready to grab
def raiseArm():
    control.armOne(7000) #7000 down, 4000 up
    time.sleep(.3)
    control.armTwo(5000) #6000 straight arm, 7500 center of body

# Close hand to grab
def grab():
    control.armSix(6500) #6000 open, 6500 closed

# Lower arm with hand closed
def lowerArm():
    control.armTwo(7000)
    time.sleep(.3)
    control.armOne(4000)

# Raise arm, drop item, lower arm.
def drop():
    raiseArm()
    time.sleep(.5)
    control.armSix(4000)
    time.sleep(4)
    lowerArm()

def ice_grab(pic):
    highestY = -1
    highestX = -1
    lowestY = -1
    lowestX = -1
    for y in range(0, height):
        for x in range(0, width):
            if pic[y][x] == 255:
                if highestY == -1:
                    highestY = y
                    highestX = x
                lowestY = y
                lowestX = x

    area = abs(lowestY - highestY) * abs(highestX - lowestX)

    if area > 1000:
        cl.sendData("I see the color!")
        time.sleep(2)
        grab()
        time.sleep(1)
        lowerArm()
        return True

def charge(w,h):
    faceArea = w*h
    if(faceArea > 10000):
        control.drive(7000)
    elif(faceArea < 5000):
        control.drive(5100)
    else:
        control.drive(6000)

def find_color(pic, color, direction):
    global state
    if(color == "orange"):
        lowH = 15
        lowS = 25
        lowV = 200
        highH = 35
        highS = 150
        highV = 255
    if(color == "pink"):
        lowH = 50
        lowS = 5
        lowV = 255
        highH = 255
        highS = 100
        highV = 255
    if(color == "green"):
        lowH = 30
        lowS = 100
        lowV = 200
        highH = 50
        highS = 255
        highV = 255

    kernel = np.ones((5,5),np.uint8)
    pic = cv.cvtColor(pic, cv.COLOR_BGR2HSV)
    pic = cv.inRange(pic, (lowH, lowS, lowV), (highH, highS, highV))
    pic = cv.erode(pic, kernel, iterations=1)
    pic = cv.dilate(pic, kernel, iterations=1)

    if(direction == 1):
        if(line_up(pic)):
            state = state + 1
    elif(direction == 2):
        if(cross_area(pic, "bot")):
            state = state + 1
    elif direction == 3:
        if(ice_grab(pic)):
            state = state + 1
    elif direction == 4:
        x, y = calcCOG(pic)
        print("cogX = ", x, "   cogY = ", y)
        if(navigate(x) == 99999):
            control.drive(6000)
            control.rotate(6000)
            drop()
            state = state + 1
        time.sleep(1)
    elif direction == 5:
        if(line_box(pic)):
            state = state + 1

    return pic

# this might be dangerous
control.drive(5500)
time.sleep(.5)
control.drive(6000)

# Arm initializations
control.hTurn(6000)
control.armTwo(7000)
time.sleep(.3)
control.armOne(4000)
#control.armOne(4000) #7000 up, 4000 down
#time.sleep(.3)
#control.armTwo(7000) #7000 straight arm
control.armThree(6000)
control.armFour(6000)
control.armFive(6000)
control.armSix(4000) #5800 closed, 6500 open

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    image = frame.array
    pic = image

    cropBot = image[height-newHeight:height, 0:width]
    cropTop = image[0:newHeight, 0:width]
    print("state: ", state)

    if state == 0:
        #line up with pink line
        pic = find_color(image, "pink", 1)
    elif state == 1:
        #enter rock area
        pic = find_color(cropBot, "orange", 2)
        #cl.sendData("Dodging Rocks")
    elif state == 2:
        #line up with orange line on far side of rocky area
        pic = find_color(image, "orange", 1)
    elif state == 3:
        #cross into mining area
        cl.sendData("Entering Mining Area")
        control.drive(4500)
        time.sleep(2.5)
        control.drive(6000)
        state = state + 1
    elif state == 4:
        control.tilt(7000)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if(len(faces) != 0):
            control.rotate(6000)
            cl.sendData("Ice please")
            for (x,y,w,h) in faces:
                cv.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            state = state + 1
        else:
            control.rotate(4900)
            time.sleep(1)
            control.rotate(6000)
            time.sleep(1)
    elif state == 5:
        #do the arm stuff
        raiseArm()
        control.tilt(1510)
        time.sleep(.5)
        find_color(image, "green", 3)
    elif state == 6:
        pic = find_color(image, "orange", 1)
    elif state == 7:
        pic = find_color(cropBot, "pink", 2)
    elif state == 8:
        pic = find_color(image, "pink", 1)
    elif state == 9:
        control.drive(4800)
        time.sleep(2)
        control.drive(6000)
        state = state + 1
        cl.sendData("I am in the start area")
    elif state == 10:
        find_color(image, "green", 5)
    elif state == 11:
        control.drive(4900)
        time.sleep(2.5)
        control.drive(6000)
        drop()

        #find_color(image, "green", 4)

    # show the frame
    #cv.setMouseCallback("Frame", getColors)
    cv.imshow("Frame", image)

    #cv.setMouseCallback("Frame", getColors)
    key = cv.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        control.drive(6000)
        control.rotate(6000)
        break

cv.destroyAllWindows()

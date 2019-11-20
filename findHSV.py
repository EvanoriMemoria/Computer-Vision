# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2 as cv
import maestro
import numpy as np

width = 640   #640
height = 480  #480

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(width, height))

kernel = np.ones((4,4),np.uint8)

def nothing(c):
    None

def getColors(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(hsv[y, x])

time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    image = frame.array
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    lowH = 30
    lowS = 100
    lowV = 200
    highH = 50
    highS = 255
    highV = 255

    pic = cv.inRange(hsv, (lowH, lowS, lowV), (highH, highS, highV))
    pic = cv.erode(pic, kernel, iterations=1)
    pic = cv.dilate(pic, kernel, iterations=1)
    # show the frame
    cv.imshow("Frame", pic)

    cv.setMouseCallback("Frame", getColors)
    key = cv.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break

cv.destroyAllWindows()

# todo
# 0. Access Camera
# 1. detect hand
# 2. save movement in a deque (is queue better?)
# 3. draw a line on hand indicating hand is detected
# 4. connect to flask so it's displayed on the web
# 5. render video guide
# 6. detect hand on that video guide
# 7. store movement in a dequeue
# 8. Match guide video movement to user video movement

import cv2
import numpy as np
from matplotlib import pyplot as plt
import time

def nothing(x):
    pass

def maskImage(frame, lh, ls, lv, uh, us, uv):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #tried this using trackbar on a daylight
    #not sure if it's correct
    low_bound = np.array([75, 43, 0])
    high_bound = np.array([129, 101, 208])

    low_bound = np.array([lh, ls, lv])
    high_bound = np.array([uh, us, uv])
    mask = cv2.inRange(hsv, low_bound, high_bound)

    #remove noise and all
    mask = cv2.erode(mask, None, iterations =2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask

# try with canny detection
def getCanny(frame, th1, th2):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(frame, th1, th2, apertureSize=3)
    print("length canny =" , len(canny))
    return canny

#try with getcontour
def getContour(frame):
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print(len(contours))
    return contours

# Main:
# From main, we access camera, declare user Dequeue
# using a while loop for all frame, we:
#     - call a function to detect hand and update dequeque
def Main():
    vs = cv2.VideoCapture(0)
    time.sleep(0.5) # give some time to warm up

    cv2.namedWindow('Tracking')
    vs.set(3, 600)
    vs.set(4, 450)

    cv2.createTrackbar("minArea", "Tracking", 5000, 20000, nothing)

    cv2.createTrackbar('LH', 'Tracking', 75, 255, nothing)
    cv2.createTrackbar('LS', 'Tracking', 43, 255, nothing)
    cv2.createTrackbar('LV', 'Tracking', 0, 255, nothing)

    cv2.createTrackbar('UH', 'Tracking', 129, 255, nothing)
    cv2.createTrackbar('US', 'Tracking', 101, 255, nothing)
    cv2.createTrackbar('UV', 'Tracking', 208, 255, nothing)
    
    while True:
        ret, frame = vs.read()
        if not ret:
            print("no frame to read")
            break
        
        cv2.imshow('Tracking', frame)

        # TRY - canny edge detection // contour detection
        minArea = cv2.getTrackbarPos('minArea', 'Tracking')
        lh = cv2.getTrackbarPos('LH', 'Tracking')
        ls = cv2.getTrackbarPos('LS', 'Tracking')
        lv = cv2.getTrackbarPos('LV', 'Tracking')

        uh = cv2.getTrackbarPos('UH', 'Tracking')
        us = cv2.getTrackbarPos('US', 'Tracking')
        uv = cv2.getTrackbarPos('UV', 'Tracking')

        mask = maskImage(frame, lh, ls, lv, uh, us, uv)
         #clean frame
        mask = cv2.erode(mask, None, iterations =2)
        mask = cv2.dilate(mask, None, iterations=2)
        #canny = getCanny(frame, th1, th2)
        contour = getContour(mask)

        #cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
        for c in contour:
            (x, y, w, h) = cv2.boundingRect(c)
            if cv2.contourArea(c) < minArea:
                continue
            cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Detected: hand", (x -10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    

        cv2.imshow('Contour', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 'q' or key == 27:
            break
    
    vs.release()
    cv2.destroyAllWindows()

Main()

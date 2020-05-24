# todo
# 0. ok - Access Camera
# 1. ok - detect hand
# 2. ok - save movement in a deque (is queue better?)
# 3. ok - draw a line on hand indicating hand is detected
# 4. connect to flask so it's displayed on the web
# 5. render video guide
# 6. detect hand on that video guide
# 7. store movement in a dequeue
# 8. Match guide video movement to user video movement

import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
from collections import deque

def nothing(x):
    pass

def maskImage(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lh = cv2.getTrackbarPos('LH', 'Tracking')
    ls = cv2.getTrackbarPos('LS', 'Tracking')
    lv = cv2.getTrackbarPos('LV', 'Tracking')

    uh = cv2.getTrackbarPos('UH', 'Tracking')
    us = cv2.getTrackbarPos('US', 'Tracking')
    uv = cv2.getTrackbarPos('UV', 'Tracking')

    low_bound = np.array([lh, ls, lv])
    high_bound = np.array([uh, us, uv])
    mask = cv2.inRange(hsv, low_bound, high_bound)

    #remove noise and all
    mask = cv2.erode(mask, None, iterations =2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask

#try with getcontour
def getContour(frame):
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours

def populateDeque(frame, contour, minArea, hand1_loc, hand2_loc):
    index = 0
    for c in contour:
        #has to be bigger than the minimum area of a hand
        if cv2.contourArea(c) < minArea:
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        # show that hand is detected
        cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)
        
        moment = cv2.moments(c)
        center = (int(moment["m10"] / moment["m00"]), int (moment["m01"] / moment["m00"]))
        #store upper x, y, w, h
        if index == 0:
            hand1_loc.appendleft([x, y, w, h, center])
            cv2.putText(frame, "Detected: hand1", (x -10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        if index == 1:
            hand2_loc.appendleft([x, y, w, h, center])
            cv2.putText(frame, "Detected: hand2", (x -10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        else: 
            hand2_loc.appendleft([0,0,0,0, (0,0)])
        index +=1

def draw_movement(frame, hand1_loc, hand2_loc):
    maxLength = len(hand1_loc) if len(hand1_loc) > len(hand2_loc) else len(hand2_loc)

    for i in range (1, maxLength):
        #draw hand1 location
        if len(hand1_loc)> i:
            if hand1_loc[i-1] is None or hand1_loc[i] is None:
                continue
            thickness = int(np.sqrt(50/ float(i + 1)) * 1.5)
            cv2.line(frame, hand1_loc[i-1][4], hand1_loc[i][4], (0, 0, 255), thickness)

        #draw hand2 location
        if len(hand2_loc)> i:
            if hand2_loc[i-1] is None or hand2_loc[i] is None:
                continue
            thickness = int(np.sqrt(50/ float(i + 1)) * 1.5)
            cv2.line(frame, hand2_loc[i-1][4], hand2_loc[i][4], (0, 255, 0), thickness)

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
    
    hand1_loc = deque(maxlen= 50)
    hand2_loc = deque(maxlen= 50)

    reach_target = False

    while True:
        ret, frame = vs.read()
        if not ret:
            print("no frame to read")
            break

        if reach_target:
            time.sleep(2.0)
            break
    
        minArea = cv2.getTrackbarPos('minArea', 'Tracking')

        mask = maskImage(frame)
        contour = getContour(mask)
        cv2.imshow('Tracking', mask)

        populateDeque(frame, contour, minArea, hand1_loc, hand2_loc)
        draw_movement(frame, hand1_loc, hand2_loc)

        #draw target
        if not reach_target:
            frame = cv2.rectangle(frame, (0, 0), (650, 70), (255, 0, 0), -1)
            frame = cv2.putText(frame, "Target", (275, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
            print("target not reached")

        if(len(hand1_loc) > 1):
            last_posY = hand1_loc[len(hand1_loc) - 1][1]
            last_posX = hand1_loc[len(hand1_loc) - 1][1]

            print(last_posX, last_posY)
            #user has hit target
            if last_posY <= 70:
                reach_target = True
                frame = cv2.rectangle(frame, (0, 0), (650, 70), (255, 0, 0), -1)
                frame = cv2.putText(frame, "You reached the target!", (275, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
                print("target reached")

        cv2.imshow('Contour', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 'q' or key == 27:
            break
    
    vs.release()
    cv2.destroyAllWindows()

Main()
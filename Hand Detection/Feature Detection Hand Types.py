import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)

orb = cv.ORB_create()

bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

des1 = None
delay = 0
while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    ###print(hsv[len(hsv)/2, len(hsv[0])/2])
    mask1 = cv.inRange(hsv, np.array([150, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contour = sorted(contours, key=cv.contourArea, reverse=True)[0]
    x,y,w,h = cv.boundingRect(contour)
    hand = frame[y:y+h, x:x+w]
    cv.imshow('hand', hand)
    kp = orb.detect(hand, None)
    kp, des2 = orb.compute(hand, kp)
    keypoints = cv.drawKeypoints(hand, kp, None, color=(0,255,0), flags=0)
    cv.imshow('keypoints', keypoints)
    if des1 is not None and des2 is not None:
        matches = None
        matches = bf.knnMatch(des1,des2, k=1)
        ##matches = sorted(matches, key = lambda x:x.distance)
        good = 0
        for m in matches:
            if len(m) != 0:
                good += 1
        cv.rectangle(frame, (x, y), (x+w, y+h), (0,min((float(good)/len(matches)) * 255, 255), 0),3)
    else:
        cv.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)
    if delay > 10:
        des1 = des2
        delay = 0
    delay += 1
    ##cv.drawContours(frame, [contour], 0, (0, 255, 0), 3)

    
    for x in range(-20, 20):
        frame[len(frame)/2 + x, len(frame[0])/2] = [255, 0, 0]
        frame[len(frame)/2, len(frame[0])/2 + x] = [255, 0, 0]
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

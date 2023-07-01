import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
cv.namedWindow('frame')

def nothing(x):
    pass

cv.createTrackbar('top','frame',0,255, nothing)
cv.createTrackbar('bot','frame',0,255, nothing)

while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask1 = cv.inRange(hsv, np.array([120, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    for i in range(min(3, len(contours))):
        cnt = contours[i]
        x,y,w,h = cv.boundingRect(cnt)
        cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        hand = frame[y:y+h,x:x+w].copy()
        mask = cv.inRange(hand, np.array([0, 0, 100]), np.array([255, 120, 255]))
        mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
        edge_contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
        edge_contours = sorted(edge_contours, key=cv.contourArea, reverse=True)
        cv.drawContours(hand, edge_contours[:2], -1, (0, 255, 0), 3)
        cv.imshow("hand{}".format(i), hand)
    cv.drawContours(frame, contours, -1, (0, 255, 0), 3)
    
    for x in range(-20, 20):
        frame[len(frame)/2 + x, len(frame[0])/2] = [255, 0, 0]
        frame[len(frame)/2, len(frame[0])/2 + x] = [255, 0, 0]
    cv.imshow('frame', frame)
    ##cv.imshow('contours', contour)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

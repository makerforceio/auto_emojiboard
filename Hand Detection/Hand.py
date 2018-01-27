import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)

while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    print(hsv[len(hsv)/2, len(hsv[0])/2])
    mask1 = cv.inRange(hsv, np.array([130, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contour = sorted(contours, key=cv.contourArea, reverse=True)[0]
    for cnt in contours:
        x,y,w,h = cv.boundingRect(cnt)
        cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        cv.drawContours(frame,[box],0,(0,0,255),2)
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

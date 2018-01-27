import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
hand_template = cv.imread('Raised_Hand_Emoji.png')

while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    ##print(hsv[len(hsv)/2, len(hsv[0])/2])
    mask1 = cv.inRange(hsv, np.array([150, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contour = sorted(contours, key=cv.contourArea, reverse=True)[0]
    x,y,w,h = cv.boundingRect(contour)
    print(contour)
    hand = frame[y:y+h, x:x+w]
    cv.imshow('hand', hand)
    ##resizeness = min(w/hand_template.shape[0], h/hand_template.shape[1])
    ##template = cv.resize(hand_template,(int(hand_template.shape[0]*resizeness), int(hand_template.shape[1]*resizeness)), interpolation = cv.INTER_CUBIC)
    template = cv.resize(hand_template,(w, h), interpolation = cv.INTER_CUBIC)
    cv.imshow('template', template)
    res = cv.matchTemplate(frame,template,cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    cv.rectangle(frame, min_loc, (min_loc[0] + w, min_loc[1] + h), (255, 255, 0), 3)
    ##cv.drawContours(frame, [contour], 0, (0, 255, 0), 3)

    
    for x in range(-20, 20):
        frame[len(frame)/2 + x, len(frame[0])/2] = [255, 0, 0]
        frame[len(frame)/2, len(frame[0])/2 + x] = [255, 0, 0]
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

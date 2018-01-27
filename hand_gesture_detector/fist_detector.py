#!/bin/env/python

import numpy as np
import cv2

fist_cascade = cv2.CascadeClassifier('xml/closed_palm.xml')
cap = cv2.VideoCapture(0)

while(True):
    (ret, frame) = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    fists = fist_cascade.detectMultiScale(gray, 1.5, 5)

    for (x,y,w,h) in fists:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    cv2.imshow('img', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

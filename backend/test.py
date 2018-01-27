import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)

while True:
   ret, frame = cap.read()
   if not ret:
      break
   #print(frame.shape)
   frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
   cv2.imshow('frame', frame)
   cv2.waitKey(100)
   #cv2.destroyAllWindows()

cap.release()
cv2.destroyAllWindows()

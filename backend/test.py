import numpy as np
import cv2
import time
import facialemotions as emo

cap = cv2.VideoCapture(0)

while True:
   ret, frame = cap.read()
   if not ret:
      break
   frame = emo.extract_face(frame)
   #emo.extract_emotion(frame)
   cv2.imshow('frame', frame)
   cv2.waitKey(100)
   #cv2.waitKey(3000)

cap.release()
cv2.destroyAllWindows()

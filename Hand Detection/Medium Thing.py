import numpy as np
import cv2 as cv
import math

cap = cv.VideoCapture(0)

while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask1 = cv.inRange(hsv, np.array([130, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    for contour in contours[:3]:
        hull_idxs = cv.convexHull(contour, returnPoints=False)
        prev_point = None
        good = np.array([])
        for i in range(len(hull_idxs)):
            x, y = contour[hull_idxs[i],0][0]
            x_prev, y_prev = contour[hull_idxs[i-1],0][0]
            dist = np.sqrt(np.square(x-x_prev) + np.square(y-y_prev))
            if dist > 10:
                cv.rectangle(frame, (x-2, y-2), (x+2,y+2), (255, 0, 0), 3)
                ##if prev_point is not None:
                    ##cv.line(frame, prev_point, (x, y), (255, 0, 0), 3)
                good = np.append(good, hull_idxs[i])
                prev_point = (x, y)
        good = good.astype(int)
        if len(good) == 0:
            continue
        defects = cv.convexityDefects(contour, good)
        defectNeighbors = {good[i] : [] for i in range(len(good))}
        if defects is None:
            continue
        for defect in defects:
            defect = defect[0]
            defectNeighbors[defect[0]].append(defect[2])
            defectNeighbors[defect[1]].append(defect[2])

        count = 0
        for k in defectNeighbors.keys():
            x, y = contour[k, 0]
            point = (x, y)
            values = defectNeighbors[k]
            if len(values) == 2:
                a = np.square(contour[values[0], 0][0] - x) + np.square(contour[values[0], 0][1] - y)
                b = np.square(contour[values[1], 0][0] - x) + np.square(contour[values[1], 0][1] - y)
                c = np.square(contour[values[1], 0][0] - contour[values[0], 0][0]) + np.square(contour[values[1], 0][1] - contour[values[0], 0][1])
                ratio = (a+b-c)/(2*np.sqrt(a)*np.sqrt(b))
                if -1 <= ratio <= 1 and math.acos(ratio) < 0.2*math.pi:
                    count += 1
                    for v in values:
                        x, y = contour[v, 0]
                        point2 = (x, y)
                        cv.line(frame, point, point2, (255, 0, 0), 3)
        cv.putText(frame,"{}".format(count), prev_point, cv.FONT_HERSHEY_SIMPLEX, 4,(255,0,0),2,cv.LINE_AA)
        cv.drawContours(frame, [contour], 0, (0, 255, 0), 3)

    
    for x in range(-20, 20):
        frame[len(frame)/2 + x, len(frame[0])/2] = [255, 0, 0]
        frame[len(frame)/2, len(frame[0])/2 + x] = [255, 0, 0]
    cv.imshow('frame', frame)
    ##cv.imshow('contours', contour)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

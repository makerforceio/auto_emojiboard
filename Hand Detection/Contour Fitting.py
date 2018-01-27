import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)
hand_contours = []
for i in ("Raised_Hand_Emoji.png",):
    hand_template = cv.imread(i)
    hand_mask = cv.inRange(hand_template, np.array([0, 0, 0]), np.array([244, 244, 244]))
    hand_contour = cv.findContours(hand_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    hand_contour = sorted(hand_contour, key=cv.contourArea, reverse=True)[0]
    if i == "Raised_Hand_Emoji.png":
        hand_contour = hand_contour / 3
    hand_contours.append(hand_contour)

while(True):
    ret, frame = cap.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    ##print(hsv[len(hsv)/2, len(hsv[0])/2])
    mask1 = cv.inRange(hsv, np.array([130, 10, 0]), np.array([180, 255, 255]))
    mask2 = cv.inRange(hsv, np.array([0, 10, 0]), np.array([20, 255, 255]))
    mask = mask1 + mask2
    mask = cv.blur(mask, (10, 10))
    mask = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)[1]
    hsv = cv.bitwise_and(frame, frame, mask=mask)

    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    for hand_contour in hand_contours:
        diffs = np.array([])
        offsets = np.array([])
        for i in range(min(3, len(contours))):
            x_offset, y_offset = 0, 0
            for _ in range(3):
                contour = contours[i]
                x_diff, y_diff = 0, 0
                for point in contour:
                    point = point[0]
                    diff = (hand_contour[:,0,0] - point[0] + x_offset)
                    x_diff += diff[np.abs(diff).argmin()]
                    diff = (hand_contour[:,0,1] - point[1] + y_offset)
                    y_diff += diff[np.abs(diff).argmin()]
                x_diff = x_diff / len(contour)
                y_diff = y_diff / len(contour)
                x_offset -= x_diff
                y_offset -= y_diff
            diff = 0
            for point in contour:
                point = point[0]
                diff += np.sqrt(np.square(np.abs(hand_contour[:,0,0] - point[0] + x_offset).min()) +
                                np.square(np.abs(hand_contour[:,0,1] - point[1] + y_offset).min()))

            diff = diff / len(contour)
            diffs = np.append(diffs, diff)
            offsets = np.append(offsets, [x_offset, y_offset])

        idx = diff.argmin()
        contour = contours[idx]
        x,y,w,h = cv.boundingRect(contour)
        cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        offset = offsets[idx*2:idx*2+2]
        modified_contour = hand_contour + offset
        cv.drawContours(frame, [modified_contour.astype(int), contour], -1, (255, 0, 0), 3)
    
    cv.drawContours(frame, contours, -1, (255, 0, 0), 3)
    
    for x in range(-20, 20):
        frame[len(frame)/2 + x, len(frame[0])/2] = [255, 0, 0]
        frame[len(frame)/2, len(frame[0])/2 + x] = [255, 0, 0]
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

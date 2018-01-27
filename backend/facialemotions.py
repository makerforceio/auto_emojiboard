import os
import cv2
import base64
import keys
import http.client, urllib.request, urllib.parse, urllib.error
import requests

cascade_path = 'haarcascade_frontalface_default.xml'
cascade_path = 'haarcascade_frontalface_alt.xml'

face_cascade = cv2.CascadeClassifier(cascade_path)


def extract_face(img, output_size=(64, 64)):
    faces = face_cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    if len(faces) == 0:
        return img
        # return cv2.resize(img, output_size)
    x, y, w, h = faces[0]
    face = img[y:y+h, x:x+w]
    return cv2.resize(face, output_size)


headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': keys.keys1
}


def extract_emotion(img):
    try:
        cv2.imwrite('test.jpg', img)
        with open('test.jpg', 'rb') as f:
            bin_img = f.read()
            #print(bin_img)
            #bin_img = base64.encode(bin_img)
        url = keys.endpoint + '/emotion/v1.0/recognize'
        response = requests.post(url, headers=headers, data=bin_img)
        print(response.content)
        print(response.headers)
        print(response.json)
        print(response.reason)
        print(response.status_code)
        print(response.text)
    except Exception as e:
        print('[Errno {0}] {1}'%(e.errno, e.strerror))
    finally:
        os.remove('test.jpg')

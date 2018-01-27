import os
import cv2
import base64
import keys
import http.client, urllib.request, urllib.parse, urllib.error
import requests
import json

#cascade_path = 'haarcascade_frontalface_default.xml'
cascade_path = 'haarcascade_frontalface_alt.xml'

face_cascade = cv2.CascadeClassifier(cascade_path)


def extract_face(img, output_size=(128, 128)):
    faces = face_cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    if len(faces) == 0:
        #return img
        return cv2.resize(img, output_size)
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
        url = keys.endpoint + '/emotion/v1.0/recognize'
        response = requests.post(url, headers=headers, data=bin_img)
        x = response.json()
        print(x)
        x = x[0]['scores']
        print(x)
        for key in x:
            x[key] = int(float(x[key])*100)
        print(x)
    except Exception as e:
        print(e)
    finally:
        os.remove('test.jpg')
        return x

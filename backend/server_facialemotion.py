import numpy as np
import cv2
import time
import socket
import requests
import operator
import threading
import facialemotions as emo
from threading import Thread, Event, ThreadError


emojis = {
  'anger': b'\xF0\x9F\x98\xA0,\xF0\x9F\x98\xA1',
  'contempt': b'\xF0\x9F\x98\x8C',
  'disgust': b'\xF0\x9F\x98\x96',
  'fear': b'\xF0\x9F\x98\xA8,\xF0\x9F\x98\xB1',
  'happiness': b'\xF0\x9F\x98\x84,\xF0\x9F\x98\x83',
  'neutral': b'\xF0\x9F\x98\x91',
  'sadness': b'\xF0\x9F\x98\x94,\xF0\x9F\x98\xA2',
  'surprise': b'\xF0\x9F\x98\xB1,\xF0\x9F\x98\xB2'
}


class Cam():

  def __init__(self, ip):
    url = 'http://' + ip + ':8080/video'
    self.stream = requests.get(url, stream=True)
    self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.publish.connect((ip, 8081))
    self.last_image = None
    self.thread_cancelled = False
    self.thread = Thread(target=self.run)
    self.thread_img = Thread(target=self.process_image)
    print("camera initialised")

  def start(self):
    self.thread.start()
    self.thread_img.start()
    print("camera stream started")

  def run(self):
    bytes = ''.encode()
    while not self.thread_cancelled:
      try:
        bytes += self.stream.raw.read(1024)
        b = bytes.rfind(b'\xff\xd9')
        a = bytes.rfind(b'\xff\xd8', 0, b-1)
        if a != -1 and b != -1 and a < b:
          jpg = bytes[a:b+2]
          bytes = bytes[b+2:]
          img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),
                             cv2.IMREAD_COLOR)
          self.last_image = img
          #cv2.imshow('cam', img)
          if cv2.waitKey(1) == 27:
            exit(0)
      except ThreadError:
        self.thread_cancelled = True

  def process_image(self):
    while not self.thread_cancelled:
      try:
        if self.last_image is None:
            time.sleep(1)
            continue
        img = self.last_image.copy()
        img = np.flip(img, axis=1)
        img = np.swapaxes(img, 0, 1)
        img_face = emo.extract_face(img)
        self.last_emotion = emo.extract_emotion(img_face)

        print(self.last_emotion)
        if isinstance(self.last_emotion, dict):
          if 'error' in self.last_emotion:
            continue
          utf = []
          for key, value in sorted(self.last_emotion.items(), key=operator.itemgetter(1)):
            utf.insert(0, emojis[key])
          ls = b','.join(utf) + b'\n'
          self.publish.send(ls)
      except ThreadError:
        self.thread_cancelled = True

  def is_running(self):
    return self.thread.isAlive()

  def shut_down(self):
    self.thread_cancelled = True
    while self.thread.isAlive():
      time.sleep(1)
    return True


if __name__ == "__main__":
  ip = '172.17.57.22'
  cam = Cam(ip)
  cam.start()

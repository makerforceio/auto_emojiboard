import numpy as np
import cv2
import time
import requests
import threading
import facialemotions as emo
from threading import Thread, Event, ThreadError

class Cam():

  def __init__(self, url):
    self.stream = requests.get(url, stream=True)
    self.last_image = None
    self.thread_cancelled = False
    self.thread = Thread(target=self.run)
    self.thread_img = Thread(target=self.process_image)
    print("camera initialised")

  def start(self):
    self.thread.start()
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
          cv2.imshow('cam', img)
          if cv2.waitKey(1) == 27:
            exit(0)
      except ThreadError:
        self.thread_cancelled = True

  def process_image(self):
    while not self.thread_cancelled:
      try:
        img = self.last_image.copy()
        img = np.flip(img, axis=1)
        img = np.swapaxes(img, 0, 1)
        img_face = emo.extract_face(img)
        self.last_emotion = emo.extract_emotion(img_face)
        print(self.last_emotion)
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
  url = 'http://172.17.59.202:8080/video'
  cam = Cam(url)
  cam.start()

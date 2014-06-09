import numpy as numpy
import cv2

class FaceDetector(object):
	def __init__(self):
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		detections = []
		for (x,y,w,h) in faces:
			roi_gray = gray[y:y+h, x:x+w]
			cv2.resize(roi_gray, (400,400))
			detections.append(roi_gray)

		return detections
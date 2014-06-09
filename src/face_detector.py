import numpy as numpy
import cv2

class FaceDetector(object):
	def __init__(self):
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	def detect(img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		detections = []
		for (x,y,w,h) in faces:
			roi_color = img[y:y+h, x:x+w]
			detections.append(roi_color)

		return detections
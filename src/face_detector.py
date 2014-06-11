import numpy as numpy
import cv2
import pickle

class FaceDetector(object):
	def __init__(self):
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = self.face_cascade.detectMultiScale(gray,1.1,1)
		detections = []
		for (x,y,w,h) in faces:
			roi_gray = gray[y:y+h, x:x+w]
			cv2.resize(roi_gray, (400,400))
			detections.append(roi_gray)

		return detections

if __name__ == '__main__':
	images = pickle.load(open('pickles2.p', 'r'))
	face_detector = FaceDetector()
	
	for img in images:
		if img.any():
			faces = face_detector.detect(img)
			for f in faces:
				cv2.imshow('Detection', f)
				k = cv2.waitKey(0)

			#cv2.imshow('Image', img)
			#k = cv2.waitKey(0)

			if k==27:
				break

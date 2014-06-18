import numpy as numpy
import cv2

class FaceDetector(object):
	def __init__(self):
		self.face_cascade = cv2.CascadeClassifier('src/haarcascade_frontalface_default.xml')

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = self.face_cascade.detectMultiScale(gray,1.5,3)
		delta = 5
		max_h, max_w = gray.shape
		detections = []
		for (x,y,w,h) in faces:
			centerx = x + w/2
			centery = y + h/2
			y1 = centery - 61*2
			y2 = centery + 61*2
			x1 = centerx - 46*2
			x2 = centerx + 46*2
			#y1 = max(0, y-30)
			#y2 = min(y+delta+h, max_h)
			#x1 = max(0, x-delta)
			#x2 = min(x+delta+w, max_w)
			roi_gray = gray[y1:y2, x1:x2]
			roi_gray = cv2.resize(roi_gray, (112,92))
			#detections.append(roi_gray)
			detections.append((y1,y2,x1,x2))

		return detections

	def to_string(self, player):
		if player == 0:
			return 'Eduardo Vargas'
		if player == 1:
			return 'Alexis Sanchez'
		if player == 2:
			return 'Claudio Bravo'
		if player == 3:
			return 'Arturo Vidal'

if __name__ == '__main__':
	import pickle
	
	images = pickle.load(open('pickles2_2.p', 'r'))
	face_detector = FaceDetector()
	
	for img in images:
		if img.any():
			faces = face_detector.detect(img)
			for f in faces:
				cv2.imshow('Detection', f)
				k = cv2.waitKey(0)

			cv2.imshow('Image', img)
			k = cv2.waitKey(0)

			if k==27:
				break

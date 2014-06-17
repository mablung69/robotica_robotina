import cv2
import numpy as np
from enums import Sign
from skimage.feature import hog
from numpy import linalg as LA
import sys

class SignalDetector(object):
	def __init__(self):
		self.template = {}
		self.hog_features = {}
		
		I = cv2.imread('../Templates/turn_left.jpg')
		self.hog_features[Sign.turn_left] = self.compute_hog(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.turn_left] = I

		I = cv2.imread('../Templates/turn_right.jpg')
		self.hog_features[Sign.turn_right] = self.compute_hog(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.turn_right] = I

		I = cv2.imread('../Templates/dont_turn_left.jpg')
		self.hog_features[Sign.dont_turn_left] = self.compute_hog(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.dont_turn_left] = I

		I = cv2.imread('../Templates/dont_turn_right.jpg')
		self.hog_features[Sign.dont_turn_right] = self.compute_hog(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.dont_turn_right] = I

		self.method = cv2.TM_CCOEFF
		self.scales = [1, 1.2]

			

	def template_detect(self, img, test=True):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		#_, gray = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
		score 		= 0
		result		= None
		for scale in self.scales:
			for signal, template in self.template.items():
				local_img = gray.copy()
				local_img = cv2.resize(local_img, (0,0), fx=scale, fy=scale)
				#print local_img.shape
				#print template.shape
				res = cv2.matchTemplate(local_img,template,self.method)
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
				
				if max_val > score:
					result = signal
					score  = max_val
					h, w = template.shape
					temp = template
					i = local_img

		if test:
			top_left = max_loc
			bottom_right = (top_left[0] + w, top_left[1] + h)
			cv2.rectangle(i,top_left, bottom_right, 0, 2)
			cv2.imshow('Signal Detection', i)
			cv2.imshow('Signal', temp)
		return result, score

	def circle_detect(self, img, test=True):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.medianBlur(gray,9)
		circles = cv2.HoughCircles(gray,cv2.cv.CV_HOUGH_GRADIENT,1,20,
                            param1=200,param2=100,minRadius=10,maxRadius=0)
		signals = []

		
		if circles != None:
			for i in circles[0,:]:
				delta = 5
				top = (int(i[0]-i[2]-delta),int(i[1]-i[2]-delta))
				bottom = (int(i[0]+i[2]+delta),int(i[1]+i[2]+delta))
				signals.append(img[top[1]:bottom[1],top[0]:bottom[0]])
				#print 'Top: ', top
				#print 'Bottom: ', bottom
				if test:
					cv2.rectangle(img, top, bottom, (0,255,0), 2)
					cv2.imshow('detected circles',img)
		
		return signals

	def compute_hog(self, img):
		feature = []
		img  = cv2.resize(img, (170,170))
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		h, w = gray.shape


		feature = hog(gray, pixels_per_cell=(85,85), cells_per_block=(2, 2))
		# feature.extend(hog(gray[0:h/2,0:w/2], pixels_per_cell=(85,85)))
		# feature.extend(hog(gray[0:h/2,w/2:w], pixels_per_cell=(85,85)))
		# feature.extend(hog(gray[h/2:h,0:w/2], pixels_per_cell=(85,85)))
		# feature.extend(hog(gray[h/2:h,w/2:w], pixels_per_cell=(85,85)))

		#feature = np.asarray(feature)
		#print feature.shape
		return feature

	def knn_predict(self, img):
		features = self.compute_hog(img)
		min_dist = sys.maxint
		sign     = None
		for c, f in self.hog_features.items():
			dist = LA.norm(features - f)
			if dist < min_dist:
				sign = c
				min_dist = dist
		return sign, min_dist
		

if __name__ == '__main__':
	import pickle

	images = pickle.load(open('pickles2_2.p', 'r'))
	signal_detector = SignalDetector()

	for img in images:
		if img.any():
			signals = signal_detector.circle_detect(img)
			if len(signals) > 0:
				for s in signals:
					#cv2.imshow('Signal', s)
					print '\nTemplate prediction: ', signal_detector.template_detect(s)
					print 'HOG prediction: ', signal_detector.knn_predict(s)
				k = cv2.waitKey(0)
				if k==27:
					break
			
		

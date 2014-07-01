import cv2
import sys
import numpy as np

from enums import Sign
from skimage.feature import hog
from skimage.transform import integral_image
from numpy import linalg as LA
from sklearn.svm import SVC
from skimage.feature import local_binary_pattern


class SignalDetector(object):
	def __init__(self):
		self.template = {}
		self.hog_features = {}
		self.integral_features = {}
		self.cls = []
		
		I = cv2.imread('../Templates/turn_left.png')
		self.hog_features[Sign.turn_left] = self.compute_hog(I)
		self.integral_features[Sign.turn_left] = self.integral_image(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.turn_left] = I
		self.cls.append(Sign.turn_left)

		I = cv2.imread('../Templates/turn_right.png')
		self.hog_features[Sign.turn_right] = self.compute_hog(I)
		self.integral_features[Sign.turn_right] = self.integral_image(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.turn_right] = I
		self.cls.append(Sign.turn_right)

		I = cv2.imread('../Templates/dont_turn_left.png')
		self.hog_features[Sign.dont_turn_left] = self.compute_hog(I)
		self.integral_features[Sign.dont_turn_left] = self.integral_image(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.dont_turn_left] = I
		self.cls.append(Sign.dont_turn_left)

		I = cv2.imread('../Templates/dont_turn_right.png')
		self.hog_features[Sign.dont_turn_right] = self.compute_hog(I)
		self.integral_features[Sign.dont_turn_right] = self.integral_image(I)
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		self.template[Sign.dont_turn_right] = I
		self.cls.append(Sign.dont_turn_right)

		self.cls = np.array(self.cls)
		self.svm = SVC()
		self.svm.fit(self.hog_features.values(), self.cls)
		#self.svm.fit(self.integral_features.values(), self.cls)



	def circle_detect(self, img, test=False):
		gray = img[:,:,1]
		#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.medianBlur(gray,9)
		circles = cv2.HoughCircles(gray,cv2.cv.CV_HOUGH_GRADIENT,1,100,
                            param1=50,param2=50,minRadius=20,maxRadius=0)
		signals = []

		
		if circles != None:
			for i in circles[0,:]:
				delta = 10
				top = (int(i[0]-i[2]-delta),int(i[1]-i[2]-delta))
				bottom = (int(i[0]+i[2]+delta),int(i[1]+i[2]+delta))
				signals.append((top, bottom))
				#print 'Top: ', top
				#print 'Bottom: ', bottom
				if test:
					cv2.rectangle(img, top, bottom, (0,255,0), 2)
					cv2.imshow('detected circles',img)
		
		return signals

	def compute_hog(self, img):
		feature = []
		gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray  = cv2.resize(gray, (170,170))
		#gray  = cv2.medianBlur(gray, 9)
		_,gray = cv2.threshold(gray,120,255,cv2.THRESH_BINARY)
		h, w = gray.shape
		#feature = hog(gray, pixels_per_cell=(85,170), cells_per_block=(1, 1)) # (85,85)
		feature = hog(gray, pixels_per_cell=(5,5), cells_per_block=(17, 17))
		#feature = local_binary_pattern(gray, 8, 3).flatten()

		return feature

	def integral_image(self, img):
		feature = []
		gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray  = cv2.resize(gray, (170,170))
		#gray  = cv2.medianBlur(gray, 9)
		_,gray = cv2.threshold(gray,70,255,cv2.THRESH_BINARY_INV)
		h,w = gray.shape
		integral = integral_image(gray)
		cv2.imshow('sign', gray)
		cv2.waitKey(0)

		# feature.append((float)(integral[84,169]))
		# feature.append((float)(integral[169,169] - integral[84,169]))
		feature.append((float)(integral[h-1,w/2]))
		feature.append((float)(integral[h-1,w-1] - integral[h-1,w/2]))

		feature.append((float)(integral[h/4,w-1]))
		feature.append((float)(integral[h-1,w-1] - integral[h*3/4, w*3/4]))
		# feature.append((float)(integral[h/2,w/2]))
		# feature.append((float)(integral[h/2, w-1] - integral[h/2,w/2]))
		# feature.append((float)(integral[h-1,w/2]  - integral[h/2,w/2]))
		# feature.append((float)(integral[h-1,w-1] + integral[h/2,w/2] - integral[h-1,w/2] - integral[h/2,w-1]))

		for i,f in enumerate(feature):
			feature[i] = (feature[i]/integral[h-1,w-1])

		# feature = np.array(integral, dtype='float').reshape(170*170)
		# feature = feature/feature[170*170-1]
		feature = np.array(feature)
		print feature
		return feature


	def knn_predict(self, img):
		#features = self.compute_hog(img)
		features = self.integral_image(img)
		min_dist = sys.maxint
		sign     = None
		#for c, f in self.hog_features.items():
		for c, f in self.integral_features.items():
			dist = LA.norm(features - f)
			print 'class = ', c
			print 'score = ', dist 
			if dist < min_dist:
				sign = c
				min_dist = dist
		return sign, min_dist
		#return self.svm.predict(features), 0
		

if __name__ == '__main__':
	import glob
	path = '../signals_imgs/*'
	signal_detector = SignalDetector()

	for folder in glob.glob(path):
		for img_name in glob.glob(str.format('{0}/*.png', folder)):
			I = cv2.imread(img_name, 1)
			signals = signal_detector.circle_detect(I)
			for top, bottom in signals:
				s = I[top[1]:bottom[1], top[0]:bottom[0]]
				sign_prediction, score = signal_detector.knn_predict(s)
				print Sign.to_string(sign_prediction), ' : ', score

			cv2.imshow('Signals', I)

			k = cv2.waitKey(0)
			if k == 27:
				break
		if k == 27:
			break

			
		

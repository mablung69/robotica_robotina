import cv2
import numpy as np
from enums import Sign

class SignalDetector(object):
	def __init__(self):
		self.template = {}
		
		I = cv2.imread('../Templates/turn_left.jpg')
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		#_,I = cv2.threshold(I,127,255,cv2.THRESH_BINARY)
		self.template[Sign.turn_left] = I

		I = cv2.imread('../Templates/turn_right.jpg')
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		#_,I = cv2.threshold(I,127,255,cv2.THRESH_BINARY)
		self.template[Sign.turn_right] = I

		I = cv2.imread('../Templates/dont_turn_left.jpg')
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		#_,I = cv2.threshold(I,127,255,cv2.THRESH_BINARY)
		self.template[Sign.dont_turn_left] = I

		I = cv2.imread('../Templates/dont_turn_right.jpg')
		I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
		#_,I = cv2.threshold(I,127,255,cv2.THRESH_BINARY)
		self.template[Sign.dont_turn_right] = I

		self.method = cv2.TM_CCOEFF
		self.scales = [1]

	def template_detect(self, img, test=True):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		#_, gray = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
		score 		= 0
		result		= None
		for scale in self.scales:
			for signal, template in self.template.items():
				local_img = gray.copy()
				local_img = cv2.resize(local_img, (0,0), fx=scale, fy=scale)
				print local_img.shape
				print template.shape
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

	def sift_detect(self, img, test=True):
		gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		score  = 0
		result = None

		sift = cv2.SIFT()
		for signal, template in self.template.items():
			pass

if __name__ == '__main__':
	import pickle

	images = pickle.load(open('pickles2.p', 'r'))
	signal_detector = SignalDetector()

	for img in images:
		if img.any():
			print signal_detector.sift_detect(img)
			k = cv2.waitKey(0)
			if k==27:
				break
			
		

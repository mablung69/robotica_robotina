import cv2
import numpy as np
from enums import Sign

class SignalDetector(object):
	def __init__(self):
		self.template = {}
		self.template[Sign.turn_left]  		= cv2.imread('../Templates/turn_left.jpg')
		self.template[Sign.turn_right] 		= cv2.imread('../Templates/turn_right.jpg')
		self.template[Sign.dont_turn_left]  = cv2.imread('../Templates/dont_turn_left.jpg')
		self.template[Sign.dont_turn_right] = cv2.imread('../Templates/dont_turn_right.jpg')
		self.methos = cv2.TM_CCOEF
		self.scales = [1]

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		score 		= 0
		result		= None
		for scale in self.scales:
			for signal, template in self.template.items():
				local_img = gray.copy()
				local_img = cv2.resize(local_img, (0,0), fx=scale, fy=scale)
				res = cv2.matchTemplate(local_img,template,self.method)
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
				
				if max_val > score:
					result = signal
					score  = max_val

		return result, score

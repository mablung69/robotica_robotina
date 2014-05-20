import numpy as np
import sys
import cv2

class RobotinaImage:
	def __init__(self, maze=False, friend=False):
		self.maze = maze
		self.friend = friend
		self.min_area = 50
		self.lower = np.array([170,160,60])
		self.upper = np.array([180,256,256])
		self.track_window = None
		self.hist_track = None
		self.track_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 10 )
		self.img = None

	def obtain_max_depth_center(self,img):
		[size_x,size_y]=img.shape
		middle_x=size_x/2
		middle_y=3*size_y/4
		center_img=img[middle_x-10:middle_x+10,middle_y-10:middle_y+10]
		center_img= center_img[~np.isnan(center_img)]
		print 'Center image', center_img
		max_depth=-1
		if len(center_img)>1:
			max_depth=max(center_img)
		return max_depth;

	def image_analisis(self, img):
		if self.friend:
			return self.rgb_analisis(img), self.img
		else:
			return self.deph_analisis(img)


	def deph_analisis(self, depth):
		try:

			h,w = depth.shape
			max_depth = -1
			max_depth_idx = -1
			idx = 0
			delta = int(w/3)
			arr = []
			for i in range(0, 3):
				segment = depth[:, idx:idx+delta]
				arr.append( segment[~np.isnan(segment)].min() )
				idx = idx+delta+1
				if segment[~np.isnan(segment)].max() > max_depth:
					max_depth = segment[~np.isnan(segment)].max()
					max_depth_idx = i
		except:
			return 0 , 0

		return arr[0] - arr[2], arr[1]


	def rgb_analisis(self, img):
		#TODO what happend if the object is lost?
		if self.track_window == None:
			self.detect_object(img)
			if self.track_window == None:
				return None
		else:
			hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			dst = cv2.calcBackProject([hsv],[0],self.hist_track,[0,180],1)

			# apply meanshift to get the new location
			# print dst
			# print self.track_window

			ret, self.track_window = cv2.CamShift(dst, self.track_window, self.track_crit)

			# Draw it on image
			pts = cv2.cv.BoxPoints(ret)
			pts = np.int0(pts)
			cv2.polylines(img,[pts],True, (0,255,0),2)
			self.img = img
			# cv2.imshow('track',img)
			# cv2.waitKey(1)
			print 'Object tracked'

		return self.track_window[0] + self.track_window[2]/2


	def detect_object(self, img):
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		mask   = cv2.inRange(hsv, self.lower, self.upper)
		mask   = cv2.blur(mask,(7,7))

		img_filter  = cv2.bitwise_and(img, img, mask= mask)
		gray = cv2.cvtColor(img_filter, cv2.COLOR_BGR2GRAY)
		contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

		max_idx  = -1
		max_area = -1
		for i, cnt in enumerate(contours):
			area = cv2.contourArea(cnt)
			if area > max_area and area > self.min_area:
				max_idx = i
				max_area = area

		if max_idx > -1:
			cnt = contours[max_idx]
			x,y,h,w = cv2.boundingRect(cnt)
			self.track_window = (x,y,h,w)

			cv2.rectangle(img,(x,y),(x+h,y+w),(0,255,0),2)
			self.img = img
			# cv2.imshow('track', img)
			# cv2.waitKey(1)

			hsv_roi = hsv[y:y+w, x:x+h]
			mask_roi = mask[y:y+w, x:x+h]

			mask_roi = cv2.inRange(hsv_roi, self.lower, self.upper)
			self.hist_track = cv2.calcHist([hsv_roi],[0], mask_roi,[180],[0,180])
			cv2.normalize(self.hist_track,self.hist_track,0,255,cv2.NORM_MINMAX)
			return self.track_window
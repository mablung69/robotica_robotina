import numpy as numpy
import cv2
import os
import sys
import sklearn
from sklearn.decomposition import PCA
from sklearn.svm import SVC
import pickle

class FaceDetector(object):
	def __init__(self):
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = self.face_cascade.detectMultiScale(gray,1.2,3)
		delta = 5
		max_h, max_w = gray.shape
		detections = []
		maxArea=0
		ind_maxarea=-1
		ind_now=0
		if len(faces)>0:
			for f1 in faces:
				contained_by_one=False
				for f2 in faces:
					if self.is_contained(f2,f1):
						contained_by_one=True
				if not contained_by_one:
					detections.append(f1)
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
		      
	def is_contained(self,detect1,detect2):
		(x1,y1,w1,h1)=detect1
		(x2,y2,w2,h2)=detect2
		if x1<x2 and y1>y2 and w1+y1<y2 and x1+h1<h2:
			return True
		else:
			return False

def saveTraining(clasifiers,reductor):
	print ">>SAVING TRAINING DATA"
	with open("jugadores_clfs", 'wb') as output_file:
		pickle.dump(clasifiers,output_file,pickle.HIGHEST_PROTOCOL)
	with open("jugadores_rds", 'wb') as output_file:
		pickle.dump(reductor,output_file,pickle.HIGHEST_PROTOCOL)
	print ">>SAVED"
	
def loadTraining(name_exp):
	print ">>LOADING TRAINING DATA"
	with open("jugadores_clfs", 'rb') as input_file:
		clf = pickle.load(input_file)
	with open("jugadores_rds", 'rb') as input_file:
		pca = pickle.load(input_file)
	return [clf,pca]

if __name__ == '__main__':
	#import pickle
	
	#images = pickle.load(open('pickles2_2.p', 'r'))
	face_detector = FaceDetector()
	
	Data=[]
	targets_data=[]
	path="jugadors_imgs"
	dirList_DATA=os.listdir(path)
	for folder in dirList_DATA:
		folder_DATA=os.listdir(path+"/"+folder)
		for fname in folder_DATA:
			if fname.endswith(".png"):
				dir_path=path+"/"+folder+"/"+fname
				print "\t>>", dir_path
				image=cv2.imread(dir_path)
				faces = face_detector.detect(image)
				for (x,y,w,h) in faces:
					sub_img=image[y:y+h,x:x+w]
					sub_img = cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
					sub_img=cv2.resize(sub_img,(200,200))
					print numpy.prod(sub_img.shape)
					sub_img=numpy.resize(sub_img,(1,numpy.prod(sub_img.shape)))
					Data.append(sub_img)
					targets_data.append(int(folder))
					cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
				cv2.imshow('Image', image)
				#k = cv2.waitKey(0)
				#if k==27:
				#	break
	
	print len(Data)
	print Data[0].shape[1]
	mat=numpy.zeros((len(Data),Data[0].shape[1]))
	for index_data in xrange(0,len(Data)):
		mat[index_data,:]=Data[index_data]
	
	print mat
	pca=PCA(n_components=20)
	transformed_data=pca.fit_transform(mat)
	
	clf=SVC()
	clf.fit(transformed_data,targets_data)
	
	saveTraining(clf,pca)
	
	prediction=clf.predict(transformed_data)
	print targets_data
	print prediction
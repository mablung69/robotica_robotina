import numpy as np
import cv2
import os
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.decomposition import SparseCoder
from numpy import linalg as LA
import pickle
import glob
import sys

class FaceDetector(object):
	def __init__(self, test=False):
		if test:
			self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		# 	self.svm = pickle.load(open('models/public_svm.model', 'rb'))
		# 	self.pca = pickle.load(open('models/public_pca.model', 'rb'))
		# 	self.cls = pickle.load(open('models/public_data.cls', 'rb'))
		# 	self.data = pickle.load(open('models/public_data.data', 'rb'))
		else:
			self.face_cascade = cv2.CascadeClassifier('src/haarcascade_frontalface_default.xml')
			# self.svm = pickle.load(open('src/models/public_svm.model', 'rb'))
			# self.pca = pickle.load(open('src/models/public_pca.model', 'rb'))
			# self.cls = pickle.load(open('src/models/public_data.cls', 'rb'))
			# self.data = pickle.load(open('src/models/public_data.data', 'rb'))

	def detect(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		faces = self.face_cascade.detectMultiScale(gray,1.3,3,cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT)
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
			return 'Alexis Sanchez'
		if player == 1:
			return 'Claudio Bravo'
	
	def is_contained(self,detect1,detect2):
		(x1,y1,w1,h1)=detect1
		(x2,y2,w2,h2)=detect2
		if x1<x2 and y1>y2 and w1+y1<y2 and x1+h1<h2:
			return True
		else:
			return False

	def predict_reconstruction(self, img):
		gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray  = cv2.resize(gray, (100,100))
		gray  = np.array(gray).reshape(100*100)
		X = self.pca.transform(gray)

		D = np.array(self.pca.components_)
		D = np.matrix(D)
		X = np.matrix(X)
		reco = (X*D).transpose()
		
		idx = -1
		min_dist = sys.maxint
		for i, d in enumerate(self.data):
			d = np.array(d, dtype='float').reshape(100*100, 1)
			dist = LA.norm(d - reco)
			if dist < min_dist:
				idx = i
				min_dist = dist

		return self.cls[idx], min_dist

	def predict_svm(self, img):
		gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray  = cv2.resize(gray, (100,100))
		gray  = np.array(gray).reshape(1,100*100)
		#X = self.pca.transform(gray)

		D = np.array(self.pca.components_)
		dictionary = SparseCoder(D, transform_algorithm='omp', transform_n_nonzero_coefs=10, transform_alpha=None)
		features = dictionary.transform(gray)
		label = self.svm.predict(features)
		score = None

		return label, score

	def predict(self, img):
		return self.predict_svm(img)

def slp_train_pca(folder, output):
	path = str.format('{0}/*', folder)
	data = []
	for folder in glob.glob(path):
		for img_path in glob.glob(folder + '/*.jpg'):
			print 'Loading: ', img_path
			img = cv2.imread(img_path, 0)
			img = np.array(img).reshape(img.shape[0]*img.shape[1])
			data.append(img)
	data = np.array(data)
	pca = PCA(n_components=10)
	pca.fit(data)
	pickle.dump(pca, open(output, 'wb'))

def slp_gen_data(folder, output):
	path = str.format('{0}/*', folder)
	data = []
	cls  = []
	c    = 0
	for folder in glob.glob(path):
		for img_path in glob.glob(folder + '/*.jpg'):
			print 'Loading: ', img_path
			img = cv2.imread(img_path, 0)
			img = np.array(img).reshape(img.shape[0]*img.shape[1])
			data.append(img)
			cls.append(c)
		c = c + 1
	data = np.array(data)
	pickle.dump(data, open(output+'.data', 'wb'))
	pickle.dump(cls, open(output+'.cls', 'wb'))

def slp_train_svm(folder, output):
	path = str.format('{0}/*', folder)
	data = []
	cls  = []
	c    = 0
	for folder in glob.glob(path):
		for img_path in glob.glob(folder + '/*.jpg'):
			print 'Loading: ', img_path
			img = cv2.imread(img_path, 0)
			img = np.array(img).reshape(img.shape[0]*img.shape[1])
			data.append(img)
			cls.append(c)
		c = c + 1
	data = np.array(data)
	pca = PCA(n_components=10)
	pca.fit(data)
	
	D = np.array(pca.components_)
	dictionary = SparseCoder(D, transform_algorithm='omp', transform_n_nonzero_coefs=10, transform_alpha=None)
	features = dictionary.transform(data)
	svm = LinearSVC()
	svm.fit(features, cls)
	pickle.dump(svm, open(output, 'wb'))

def saveTraining(clasifiers,reductor):
	print ">>SAVING TRAINING DATA"
	with open("jugadores_clfs", 'wb') as output_file:
		pickle.dump(clasifiers,output_file,pickle.HIGHEST_PROTOCOL)
	with open("jugadores_rds", 'wb') as output_file:
		pickle.dump(reductor,output_file,pickle.HIGHEST_PROTOCOL)
	print ">>SAVED"
	
def loadTraining():
	print ">>LOADING TRAINING DATA"
	with open("src/jugadores_clfs", 'rb') as input_file:
		clf = pickle.load(input_file)
		print "Imported clasifier"
	with open("src/jugadores_rds", 'rb') as input_file:
		pca = pickle.load(input_file)
		print "Imported pca"
	return [clf,pca]

def Test():
	[clf,pca]=loadTraining()
	# face_detector = FaceDetector()
	# cv_image=cv2.imread('../jugadors_imgs/1/imagen3.png')
	
	# detections = face_detector.detect(cv_image)
	# best_detection = None
	# best_confidence = 100000
	# Data=[]
	# for (x,y,w,h) in detections:
	# 	sub_img=cv_image[y:y+h,x:x+w]
	# 	sub_img=cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
	# 	sub_img=cv2.resize(sub_img,(200,200))
	# 	sub_img=numpy.resize(sub_img,(1,numpy.prod(sub_img.shape)))
	# 	Data.append(sub_img)

	# mat=numpy.zeros((len(Data),Data[0].shape[1]))
	# for index_data in xrange(0,len(Data)):
	# 	mat[index_data,:]=Data[index_data]

	Data=[]
	for (x,y,w,h) in detections:
		sub_img=cv_image[y:y+h,x:x+w]
		sub_img=cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
		sub_img=cv2.resize(sub_img,(200,200))
		sub_img=np.resize(sub_img,(1,np.prod(sub_img.shape)))
		Data.append(sub_img)

	mat=np.zeros((len(Data),Data[0].shape[1]))
	for index_data in xrange(0,len(Data)):
		mat[index_data,:]=Data[index_data]

	# mat=pca.transform(mat)
	# array_probs = clf.predict_proba(mat)

	# selected=[]        
	# for i in xrange(0,array_probs.shape[0]):
	# 	ind=numpy.argmin(array_probs[0,:])
	# 	selected.append([array_probs[i,ind],ind])
	selected=[]        
	for i in xrange(0,array_probs.shape[0]):
		ind=np.argmin(array_probs[0,:])
		selected.append([array_probs[i,ind],ind])

	# best_proba=1
	# ind_best_proba=-1
	# for i in xrange(0,len(selected)):
	# 	if(selected[i][0]<best_proba):
	# 		best_proba=selected[i][0]
	# 		ind_best_proba=i

	# p_label=selected[ind_best_proba][1]
	# p_confidence=selected[i][0]

	# x=detections[ind_best_proba][0]
	# y=detections[ind_best_proba][1]
	# w=detections[ind_best_proba][2]
	# h=detections[ind_best_proba][3]
	# cv2.rectangle(cv_image,(x,y),(x+w,y+h),(255,0,0),2)
	# player = face_detector.to_string(p_label)
	# print "Encontrado: ", player
	# cv2.putText(cv_image,player,(x,y),cv2.FONT_HERSHEY_PLAIN, 2,(0,0,255))
	# cv2.imshow('image',cv_image)
	#cv2.rectangle(cv_image,(x,y),(x,y,x+w,y+h), (0,255,0), 2)

def Train():
	#images = pickle.load(open('pickles2_2.p', 'r'))
	face_detector = FaceDetector()
	
	Data=[]
	targets_data=[]
	path="../jugadors_imgs"
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
					print np.prod(sub_img.shape)
					sub_img=np.resize(sub_img,(1,np.prod(sub_img.shape)))
					Data.append(sub_img)
					targets_data.append(int(folder))
					cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
				cv2.imshow('Image', image)
				#k = cv2.waitKey(0)
				#if k==27:
				#	break
	
	print len(Data)
	print Data[0].shape[1]
	mat=np.zeros((len(Data),Data[0].shape[1]))
	for index_data in xrange(0,len(Data)):
		mat[index_data,:]=Data[index_data]
	
	print mat
	pca=PCA(n_components=20)
	transformed_data=pca.fit_transform(mat)
	
	clf=SVC(probability=True)
	clf.fit(transformed_data,targets_data)
	
	saveTraining(clf,pca)
	
	prediction=clf.predict_proba(transformed_data)
	print prediction

if __name__ == '__main__':
	#Test()
	path = '../futbol_crop'
	slp_train_pca(path, 'models/public_pca.model')
	slp_train_svm(path, 'models/public_svm.model')
	slp_gen_data(path, 'models/public_data')

	from enums import Player

	face_detector = FaceDetector(test=True)

	test_path = '../jugadors_imgs/*.png'
	for img_path in glob.glob(test_path):
		I = cv2.imread(img_path, 1)
		detections = face_detector.detect(I)
		for (x,y,w,h) in detections:
			face = I[y:y+h,x:x+w]
			face_prediction, score = face_detector.predict(face)
			
			player = Player.to_string(face_prediction)
			cv2.rectangle(I,(x,y),(x+w,y+h),(255,0,0),2)
			cv2.putText(I,player,(x,y),cv2.FONT_HERSHEY_PLAIN, 2,(0,0,255))
			print str.format('{0}: {1}', player, score)
		cv2.imshow('Player', I)
		k = cv2.waitKey(0)
		if k == 27:
			break



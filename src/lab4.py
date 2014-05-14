import math
import sys
from planner import Planner
from astar import shortest_path
from localization import Localization
from turtle_bot import get_robot
from enums import Action
import cv2
import cv2.cv as cv
import numpy as np

def step(current, last, robot, has_wall, distance=1.2, angle=math.pi/2):
	turn = current[2] - last[2]
	print 'Turn: ', turn
	if turn == 0:
		if has_wall:
			robot.move_maze_wall(0.3)
		else:
			robot.move_maze_distance(1.2,0.3)
	elif turn >-3 and turn < 3:
		robot.turn_angle(turn*angle,0.2)
	elif turn == 3:
		robot.turn_angle(-angle,0.2)
	elif turn == -3:
		robot.turn_angle(angle,0.2)

#def step_predicting_location(robot):

def do_observation_round():
	obs=[0,0,0,0]
	while robot.current_max_depth == None:
		robot.wait(0.5)

	for i in xrange(0,4):
		actual_depth=robot.current_max_depth;
		obs_init[i]=int((actual_depth-0.6)/1.2);
		robot.turn_angle(math.pi/2,0.2)
	return obs

def do_observation_front(robot):
	while robot.current_max_depth == None:
		robot.wait(0.5)
		print '>> Main::do observation front: Waiting for kinect'
	actual_depth=robot.current_max_depth
	print 'Actual depth: ', actual_depth
	obs_init=max(int(round((actual_depth-0.5)/0.8,0)),0)
	print 'Observation: ', obs_init
	return obs_init

def moving_predicting_location(robot,file_name):
	loc= Localization(file_name)
	init_obs=do_observation_round();
	print obs_init
	print valid
	return start


def find_space(robot,loc):
	while robot.current_max_depth == None:
		robot.wait(0.5)
	found=False
	while ~found:
		obs_act=do_observation_front(robot)
		action=None
		if obs_act==0:
			action=Action.turn_left
		else:
			action=Action.move
			found=True
		robot.apply_action(action,obs_act)
		obs_act = do_observation_front(robot)
		loc.add_observation(obs_act,action=action)
		robot.wait(1)
		print '>> Main::find space. Locations: ', loc.locations
	return obs	

def move_robot(robot,path,walls):
	last_state = path[0]
	for i in range(1,len(path)):
		print '\n Last state: ', last_state
		print ' Current state: ', path[i]

		current_walls = walls[(path[i][0],path[i][1])]
		has_wall = current_walls[path[i][2]] == 1

		print 'has_wall ' , has_wall 

		step(path[i],last_state,robot,has_wall)

		last_state = path[i]
		robot.wait(0.5)
		robot.play_sound(3)	

def metal_detector(img):
	haar_cascade = cv2.CascadeClassifier('haar/cascade.xml')
	roi = [480/2, 640/3, 480, 640*2/3]
	img = img[roi[0]:roi[2],roi[1]:roi[3]]

	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	detections = haar_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=2, 
				minSize=(5, 5), flags = cv.CV_HAAR_SCALE_IMAGE)
	
	gray = np.float32(gray)
	dst = cv2.cornerHarris(gray,2,3,0.04)
	dst = cv2.dilate(dst,None)
	
	img[dst>0.05*dst.max()]=[0,0,255]
	for (x,y,w,h) in detections:
		cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

	cv2.imshow('CROP', img)

	try:
		x_ = x + w/2
		w_ = img.shape[1]/2
		print x_ - w_
		return x_ - w_
	except Exception:
		return None

if __name__=="__main__":
	robot = get_robot()
	filename = "map3.map"

	loc=Localization(filename)
	observation = do_observation_front(robot)
	loc.add_observation(observation)
	
	print '>>Main. Locations: ', loc.locations

	while len(loc.locations) != 1:
		action,_ = loc.plan_action()
		robot.apply_action(action, observation)
		observation = do_observation_front(robot)
		loc.add_observation(observation, action=action)
		print 'ACTION: ', action

	print 'Final Location: ', loc.locations
	robot.play_sound(6)

	start=loc.locations.pop()

	#obtaining optimal path 
	planifier=Planner();
	[path,walls]=plan.do_planning(filename,start)
	
	move_robot(robot,path,walls)

	robot.play_sound(5)

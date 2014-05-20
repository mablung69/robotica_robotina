#import Packages
import math
import sys
import cv2
import cv2.cv as cv
import numpy as np
import thread
import time

#import Clases
from localization import Localization
from planner import Planner

#import Enums
from enums import Action,Excecute_Params

#import Methods
from Robot.turtle_bot import get_robot
from robot_operations import do_observation_front,get_action

def show_image(threadName,robot, delay = 0):

	while True:
		k = cv2.waitKey(1)

		if robot.current_cv_rgb_image != None:
			img = np.asarray(robot.current_cv_rgb_image)
			height, width, depth = img.shape
			p1 = ( width / 2 - robot.current_w_corr_win / 2 , height / 2 - robot.h_corr_win / 2 )
			p2 = ( width / 2 + robot.current_w_corr_win / 2 , height / 2 + robot.h_corr_win / 2 )
			cv2.rectangle(img, p1, p2 , (0,0,255))
			cv2.imshow("Image", np.asarray(img))

		if k == 27:
			cv2.destroyAllWindows()
			break
		
		time.sleep(delay)

#main
if __name__=="__main__":

	robot = get_robot()
	filename = Excecute_Params.file_name

	thread.start_new_thread( show_image, ("Thread-1",robot, ) )

	#obtaining start Localization
	loc=Localization(filename)
	observation = do_observation_front(robot)
	loc.add_observation(observation)
	
	print '>>Main. Locations: ', loc.locations

	while len(loc.locations) != 1:
		action,_ = loc.plan_action()
		if not robot.apply_action(action, observation):
			action = action + 1
			robot.apply_action(action, observation)
		observation = do_observation_front(robot)
		loc.add_observation(observation, action=action)
		robot.play_sound(2)
		print 'ACTION: ', action
		print 'PARTIAL LOCATIONS: ', loc.locations

	print 'Final Location: ', loc.locations
	robot.wait(5)
	robot.play_sound(6)

	start=loc.locations.pop()

	#obtaining optimal path 
	planifier=Planner();
	[path,walls]=planifier.do_planning(filename,start)

	last_state = path[0]
	for i in range(1,len(path)):
		print '\n Last state: ', last_state
		print ' Current state: ', path[i]
		action=get_action(path[i],last_state)
		robot.apply_action(action, observation)
		observation = do_observation_front(robot)
		last_state = path[i]
		robot.play_sound(5)	

	robot.play_sound(6)

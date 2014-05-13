import math
import sys
from planner import Planner
from astar import shortest_path
from localization import Localization
from turtle_bot import get_robot
from enums import Action


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
	actual_depth=robot.current_max_depth
	print 'Actual depth: ', actual_depth
	obs_init=max(int(round((actual_depth-0.4)/0.8,0)),0)
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

if __name__=="__main__":
	robot = get_robot()
	filename = "map3.map"

	loc=Localization(filename)
	loc.add_observation(do_observation_front(robot))
	
	print '>>Main. Locations: ', loc.locations

	while(len(loc.locations)!=1):
		find_space(robot,loc)

	print "LOC:", loc.locations

	moving_predicting_location(robot,filename)

	#planifier=Planner();
	#start=None
	#[path,walls] = planifier.do_planning(filename,start)

	#Now we have to move the robot

	#move_robot(robot,path,walls)

	#robot.play_sound(5)

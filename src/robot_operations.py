def do_observation_front(robot):
	while robot.current_max_depth == None:
		robot.wait(0.5)
		print '>>do_observation_front: Waiting for kinect'
	actual_depth=robot.current_max_depth
	print 'Actual depth: ', actual_depth
	obs_init=max(int(round((actual_depth-0.5)/0.8,0)),0)
	print 'Observation: ', obs_init
	return obs_init

def get_action(current, last):
	turn = current[2] - last[2]
	print 'Turn: ', turn
	action=None
	if turn == 0:
		return Action.move
	elif turn==-1:  
		return Action.turn_right
	elif turn==1:
		return Action.turn_left
	elif turn == 3:
		return Action.turn_right
	elif turn == -3:
		return Action.turn_left
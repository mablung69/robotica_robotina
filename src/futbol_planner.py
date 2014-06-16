from enums import Orientation, Action, Sign, Player
from graph import DirectedGraph
from astar import shortest_path
from planner import Planner

import Queue

class FutbolPlanner(object):
	def __init__(self, graph, start, node_distance):
		self.player_position = {}
		self.graph 			 = graph
		self.visited 		 = set()
		self.sign_position 	 = {}
		self.actual_position = start
		self.node_distance 	 = node_distance
		self.target 		 = None
		self.path 			 = None

		self.visited.add(start)
		self.target = self.bfs_search()


	def apply_action(self, action):
		if action == Action.move:
			if self.actual_position[2] == Orientation.up:
				self.actual_position = (self.actual_position[0]+1,self.actual_position[1],self.actual_position[2])
			elif self.actual_position[2] == Orientation.left:
				self.actual_position = (self.actual_position[0],self.actual_position[1]-1,self.actual_position[2])
			elif self.actual_position[2] == Orientation.down:
				self.actual_position = (self.actual_position[0]-1,self.actual_position[1],self.actual_position[2])
			elif self.actual_position[2] == Orientation.right:
				self.actual_position = (self.actual_position[0],self.actual_position[1]+1,self.actual_position[2])
		elif action == Action.turn_right:
			#print '>> Localization:applied_action Turning right ', self.actual_position
			self.actual_position = (self.actual_position[0],self.actual_position[1],(self.actual_position[2]-1)%4)
		elif action == Action.turn_left:
			#print '>> Localization:applied_action Turning left ', self.actual_position
			self.actual_position = (self.actual_position[0],self.actual_position[1],(self.actual_position[2]+1)%4)

		self.visited.add(self.actual_position)
		if self.actual_position == self.target:
			self.target = self.bfs_search()

	def add_player(self, player):
		self.player_position[player] = self.actual_position

	def add_sign(self, sign):
		self.sign_position.setdefault(sign, [])
		self.sign_position[sign].append(self.actual_position)

		if sign in [Sign.dont_turn_left, Sign.dont_turn_right]:
			from_node = self.actual_position
			if sign == Sign.dont_turn_left:
				from_node = (from_node[0], from_node[1], (from_node[2]+1)%4)
			elif sign == Sign.dont_turn_right:
				from_node = (from_node[0], from_node[1], (from_node[2]-1)%4)

			if from_node[2] == Orientation.up:
				to_node = (from_node[0]+1, from_node[1], from_node[2])
			elif from_node[2] == Orientation.left:
				to_node = (from_node[0], from_node[1]-1, from_node[2])
			elif from_node[2] == Orientation.down:
				to_node = (from_node[0]-1, from_node[1], from_node[2])
			else:
				to_node = (from_node[0], from_node[1]+1, from_node[2])
			self.graph.disconect(from_node, to_node)

		if sign in [Sign.turn_left, Sign.turn_right]:
			stop_list = [self.actual_position]
			target = self.bfs_search(stop_list=stop_list)
			if target != False:
				self.target = target


	def bfs_search(self, stop_list=[]):

		local_visit = set()
		print "VISITED: ",self.visited
		queue = Queue.Queue()
		queue.put(self.actual_position)
		while not queue.empty():
			node = queue.get()
			if not node in self.visited and self.node_distance[node] == 0:
				self.target = node
				print "FROM: ",self.actual_position," TO: ",self.target
				return node

			local_visit.add(node)

			for s in self.graph.edges[node]:

				if not s in stop_list and not s in local_visit:
					print "CHECKING: ",s
					queue.put(s)

		return False

	def plan_action(self):
		planner = Planner()
		planner.graph = self.graph
		print "SANTIAGO TARGET: ",self.target
		path = planner.solve(self.actual_position, [self.target])
		self.current_plan = path

		if len(path) <= 1:
			return False
		else:
			next_state = path[1]
			turn = next_state[2] - self.actual_position[2]
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

if __name__=="__main__":

	import multiprocessing
	from localization import Localization
	from planner import Planner
	from mapper import Mapper
	from file_loader import FileLoader
	from enums import Action
	import properties
	import time

	pool = multiprocessing.Pool(processes=1)

	filename = properties.file_name

	f_loader = FileLoader()
	f_loader.read_map(filename)
	f_loader.generate_undirected_graph()
	f_loader.generate_directed_graph()
	f_loader.estimate_distances()

	location 		= f_loader.starts[0]
	goals    		= f_loader.goals
	max_col  		= f_loader.max_cols
	max_row  		= f_loader.max_rows
	graph    		= f_loader.directed_graph
	node_distance 	= f_loader.node_distance

	#thread.start_new_thread( show_image, ("Thread-1",robot, ) )
	
	futbol_planner   = FutbolPlanner(graph, location, node_distance)
	futbol_planner.graph.push_map(futbol_planner.actual_position)

	while True:
		#observation = max(robot.get_observation(),0)
		#mapper.add_observation(observation)

		action = futbol_planner.plan_action()

		futbol_planner.graph.push_map(futbol_planner.actual_position)

		if type(action) == type(1):
			futbol_planner.apply_action(action)
		else:
			break

		if futbol_planner.actual_position == (0,0,0):
			pass

		if len(futbol_planner.player_position) > 3:
			futbol_planner.graph.push_map(futbol_planner.actual_position)
			break

		if futbol_planner.target == False:
			break

		time.sleep(1)


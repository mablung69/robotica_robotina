from enums import Orientation, Action, Sign, Player, RobotState
from graph import DirectedGraph
from astar import shortest_path
from planner import Planner
from soundx import Soundx as Sound
import copy
import sys
import time

import Queue

class FutbolPlanner(object):
	def __init__(self, graph, start, node_distance, goals, keys, walls):
		self.player_position = {}
		self.keys_found = []
		self.keys_available = 0
		self.graph 			 = graph
		self.original_graph  = copy.deepcopy(graph)
		self.visited 		 = set()
		self.sign_position 	 = {}
		self.actual_position = start
		self.node_distance 	 = node_distance
		self.target 		 = None
		self.path 			 = None
		self.walls = walls

		self.current_state = RobotState.searching
		self.current_plan = None
		self.goals = goals
		self.keys = keys

		self.visited.add(start)
		self.target = self.bfs_search()
		self.waiting_for_door = False

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
		elif action == Action.open_door:
			pass

		self.visited.add(self.actual_position)
		self.check_for_key()

		if self.actual_position == self.target and self.current_state == RobotState.searching:
			self.target = self.bfs_search()
		if self.actual_position == self.target and self.current_state == RobotState.returning:
			self.current_state = RobotState.searching
			self.target = self.bfs_search()


	def add_player(self, player):
		if self.current_state == RobotState.searching:
			if not player in self.player_position:

				print 'Adding player: ', self.actual_position, ' - ', player

				self.player_position[player] = self.actual_position
				self.current_state = RobotState.returning
				self.target = self.get_nearest_goal()


	def add_key(self):
		self.keys_found.append( (self.actual_position[0],self.actual_position[1]) )
		s = Sound()
		s.play_action(Action.keys)
		self.keys_available += 1
		time.sleep(0.5)
		s.play_action(Action.thanks)

	def check_for_key(self):
		n_pos = ( (self.actual_position[0],self.actual_position[1]) )
		if (n_pos in self.keys) and not (n_pos in self.keys_found):
			self.add_key()

	def get_keys_available(self):

		return list(set(self.keys) - set(self.keys_found))

	def add_sign(self, sign):
		if self.current_state == RobotState.searching:

			self.sign_position[self.actual_position] = sign

			print 'Adding sign: ', self.actual_position, ' - ', sign

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
				elif from_node[2] == Orientation.right:
					to_node = (from_node[0], from_node[1]+1, from_node[2])

				self.graph.disconect(from_node, to_node)
				self.target = self.bfs_search()

			if sign in [Sign.turn_left, Sign.turn_right]:
				stop_list = []
				for i in xrange(0,4):
					stop_list.append((self.actual_position[0],self.actual_position[1],(self.actual_position[2]+i)%4))
				if sign == Sign.turn_left:
					stop_list.remove((self.actual_position[0],self.actual_position[1],(self.actual_position[2]+1)%4))
				elif sign == Sign.turn_right:
					stop_list.remove((self.actual_position[0],self.actual_position[1],(self.actual_position[2]-1)%4))

				target = self.bfs_search(stop_list=stop_list)
				if target != False:
					self.target = target
				else:
					target = self.bfs_search()
					if target != False:
						self.target = target


	def bfs_search(self, stop_list=[]):

		if(self.current_state == RobotState.searching):
			return self.do_bfs(stop_list)
		elif(self.current_state == RobotState.searching):
			return self.get_nearest_goal()
		else:
			return self.get_nearest_goal()

	def do_bfs(self,stop_list):
		local_visit = set()
		#print "VISITED: ",self.visited
		queue = Queue.Queue()
		queue.put(self.actual_position)
		while not queue.empty():
			node = queue.get()
			if not node in self.visited and self.node_distance[node] == 0:
				self.target = node
				#print "FROM: ",self.actual_position," TO: ",self.target
				return node
			local_visit.add(node)
			for s in self.graph.edges[node]:
				#print s, local_visit
				#print (3,3,0) in self.visited
				if not s in stop_list and not s in local_visit:
					queue.put(s)
		return self.actual_position


	def get_nearest_goal(self):

		best_goal = False
		best_path_dist = 999999
		for goal in self.goals:
			for oddy in xrange(0,4):
				g = (goal[0],goal[1],oddy)
				self.target = g
				path,keys = self.best_plan(self.original_graph,self.keys_available)

				if(len(path) < best_path_dist):
					best_goal = g
					best_path_dist = len(path)

		return best_goal

	def best_plan(self, graph, keys):
		best_path = None
		best_keys = sys.maxint
		for k in xrange(0,keys+1):
			path,keys_used = self.get_best_plan_with_keys_recursive(graph, k)
			if best_path == None:
				best_path = path
			if len(path) < len(best_path):
				best_path = path
				best_keys = keys_used
			if( len(path) == len(best_path) and keys_used < best_keys ):
				best_path = path
				best_keys = keys_used
		return best_path, best_keys

	def get_best_plan_with_keys_recursive(self,graph, keys):

		if keys == 0:
			planner = Planner()
			planner.graph = graph
			path = planner.solve(self.actual_position, [self.target])
			return path, self.keys_available - keys

		best_plan = None
		best_plan_dist = 999999
		best_keys_num = 9999999
		removed_walls = []

		for node, walls in self.walls.items():
			aux = None
			for i,w in enumerate(walls):

				if walls[Orientation.up] == 1 and i == Orientation.up:
					aux = (node[0]+1,node[1], Orientation.up)
				elif walls[Orientation.left] == 1 and i == Orientation.left:
					aux = (node[0],node[1]-1, Orientation.left)
				elif walls[Orientation.down] == 1 and i == Orientation.down:
					aux = (node[0]-1,node[1], Orientation.down)
				elif walls[Orientation.right] == 1 and i == Orientation.right:
					aux = (node[0],node[1]+1, Orientation.right)

				if aux in graph.nodes:
					graph.add_edge( (node[0],node[1],i),aux)

					path, keys_used = self.get_best_plan_with_keys_recursive(graph,keys - 1)

					graph.disconect( (node[0],node[1],i),aux)

					if(len(path) < best_plan_dist ):
						best_plan_dist = len(path)
						best_keys_num = keys_used
						best_plan = path
					if( len(path) == best_plan_dist and keys_used < best_keys_num ):
						best_plan_dist = len(path)
						best_keys_num = keys_used
						best_plan = path

		return best_plan, best_keys_num

	def plan_action(self):
		planner = Planner()

		if self.current_state == RobotState.searching:
			planner.graph = self.graph
			path = planner.solve(self.actual_position, [self.target])

		elif self.current_state == RobotState.returning:
			planner.graph = self.original_graph
			path,keys_used = self.best_plan(self.original_graph, self.keys_available)

		self.current_plan = path

		if len(path) <= 1:
			return Action.nothing
		else:
			next_state = path[1]
			turn = next_state[2] - self.actual_position[2]

			if( not (next_state in self.graph.edges[self.actual_position]) and
					( abs(next_state[0] - self.actual_position[0]) +
						abs(next_state[1] - self.actual_position[1]) == 1 ) and turn == 0):

				if self.waiting_for_door == False:
					print "Waiting For Door!"
					self.waiting_for_door = True
					return Action.open_door
				else:
					self.keys_available -= 1
					print 'USING KEY ! left: ',self.keys_available
					self.waiting_for_door = False

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

	def check_ending(self):
		return False

if __name__=="__main__":

	import multiprocessing
	from localization import Localization
	from planner import Planner
	from mapper import Mapper
	from file_loader import FileLoader
	from enums import Action, Sign
	import properties
	import time

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
	walls = f_loader.walls
	keys = f_loader.keys

	signals = {}
	signals[(1,0,1)] = Sign.turn_left
	signals[(0,2,2)] = Sign.dont_turn_left
	signals[(1,3,3)] = Sign.dont_turn_left
	signals[(2,2,3)] = Sign.turn_right
	signals[(3,0,0)] = Sign.turn_right

	players = {}
	players[(0,1,2)] = Player.alexis
	players[(3,3,0)] = Player.claudio


	futbol_planner   = FutbolPlanner(graph, location, node_distance, goals, keys , walls)
	futbol_planner.graph.push_map(futbol_planner.actual_position,
																plan=futbol_planner.current_plan,
																signals=futbol_planner.sign_position,
																goals=futbol_planner.goals,
																keys=futbol_planner.get_keys_available(),
																players=futbol_planner.player_position)

	while True:
		print 'Iteration: ', futbol_planner.actual_position, ' ', RobotState.to_string(futbol_planner.current_state)
		print 'Target', futbol_planner.target
		print 'Keys', futbol_planner.keys_available
		action = futbol_planner.plan_action()
		print 'Action', Action.to_string(action)

		futbol_planner.graph.push_map(futbol_planner.actual_position,
																	plan=futbol_planner.current_plan,
																	signals=futbol_planner.sign_position,
																	goals=futbol_planner.goals,
																	keys=futbol_planner.get_keys_available(),
																	players=futbol_planner.player_position)

		if type(action) == type(1):
			futbol_planner.apply_action(action)
		else:
			break

		if len(futbol_planner.player_position) > 3:
			futbol_planner.graph.push_map(futbol_planner.actual_position,
																		plan=futbol_planner.current_plan,
																		signals=futbol_planner.sign_position,
																		goals=futbol_planner.goals,
																		keys=futbol_planner.get_keys_available(),
																		players=futbol_planner.player_position)
			break

		if futbol_planner.target == False:
			print 'Target False !'
			break

		if futbol_planner.actual_position in signals.keys():
			futbol_planner.add_sign(signals[futbol_planner.actual_position])

		if futbol_planner.actual_position in players.keys():
			futbol_planner.add_player(players[futbol_planner.actual_position])

		time.sleep(0.02)

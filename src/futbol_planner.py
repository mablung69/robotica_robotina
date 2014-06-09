from enums import Orientation, Action, Sign, Player
from graph import DirectedGraph
from astar import shortest_path

class FutbolPlanner(object):
	def __init__(self, graph, start):
		self.player_position = {}
		self.graph 			 = graph
		self.visited 		 = set()
		self.sign_position 	 = {}
		self.actual_position = start
		self.target 		 = None
		self.path 			 = None

		self.visited.add(start)

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


	def bfs_search(self):
		pass
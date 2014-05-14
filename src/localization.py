from enums import Orientation,Action
from graph import UndirectedGraph

class Localization(object):
	def __init__(self,file_name):
		self.locations = set()
		self.graph=self.create_map(file_name)
		self.distances = {}
		self.node_distance = {}
		
		self.estimate_distances()
		

	def add_observation(self, observation, action=None):
		if len(self.locations) == 0:
			for initial_location in self.distances[observation]:
				self.locations.add(initial_location)
		else:
			# Update current locations
			new_locations = set()
			for location in self.locations:
				new_node = self.apply_action(action, location)
				new_locations.add(new_node)
			self.locations = new_locations

			remove_list = []
			for initial_location in self.locations:
				#applied_action = self.apply_action(action, initial_location)
				remove = True
				for posible_location in self.distances[observation]:
					if posible_location == initial_location:# in self.graph.edges[initial_location] and posible_location == applied_action:
						remove = False
						break
				if remove:
					remove_list.append(initial_location)
			for node in remove_list:
				self.locations.remove(node)

	def apply_action(self, action, node):
		if action == Action.move:
			if node[2] == Orientation.up:
				return (node[0]+1,node[1],node[2])
			if node[2] == Orientation.left:
				return (node[0],node[1]-1,node[2])
			if node[2] == Orientation.down:
				return (node[0]-1,node[1],node[2])
			if node[2] == Orientation.right:
				return (node[0],node[1]+1,node[2])
		elif action == Action.turn_right:
			#print '>> Localization:applied_action Turning right ', node
			return (node[0],node[1],(node[2]-1)%4)
		elif action == Action.turn_left:
			#print '>> Localization:applied_action Turning left ', node
			return (node[0],node[1],(node[2]+1)%4)

	def plan_action(self):
		min_length  = -1
		best_action = None
		actions = [Action.move, Action.turn_left, Action.turn_right]

		for action in actions:
			new_observations = {}
			for location in self.locations:
				new_location = self.apply_action(action, location)
				try:
					observation = self.node_distance[new_location]
					new_observations.setdefault(observation, [])
					new_observations[observation].append[location]
				except Exception:
					pass

			posible_observations = len(new_observations.keys())
			if (posible_observations > min_length) or (posible_observations == min_length and action == Action.move):
				best_action = action
				min_length = posible_observations

		return best_action, min_length


	def estimate_distances(self):
		#print '> Exploring distances'
		nodes = self.graph.nodes

		for node in nodes:
			#print '\t>>Localization::estimate_distances Node ', node
			distance = 0
			orientation = node[2]
			aux_node  = node
			test_node = node

			while True:
				if orientation == Orientation.up:
					test_node = (aux_node[0] + 1, aux_node[1], aux_node[2])
				elif orientation == Orientation.left:
					test_node = (aux_node[0], aux_node[1] - 1, aux_node[2])
				elif orientation == Orientation.down:
					test_node = (aux_node[0] - 1, aux_node[1], aux_node[2])
				elif orientation == Orientation.right:
					test_node = (aux_node[0], aux_node[1] + 1, aux_node[2])

				if not test_node in self.graph.edges[aux_node]: #BUG
					break
				aux_node = test_node
				distance = distance + 1

			self.distances.setdefault(distance, [])
			self.distances[distance].append(node)
			self.node_distance[node] = distance
			

	def create_map(self, file_name):
		walls = {}	

		print 'Reading File'
		f = open(file_name, 'r')

		# Reading walls: [row, col, up, left, down, right]
		print '\t> Parsing walls'
		[MAX_ROW, MAX_COL] = f.readline().split(' ')
		MAX_ROW = int(MAX_ROW)
		MAX_COL = int(MAX_COL)

		for i in range(0, MAX_ROW*MAX_COL):     
			data = f.readline().split(' ')
			print 'data: ', data
			data = map(int, data)
			walls[(data[0],data[1])] = (data[2],data[3],data[4], data[5])
		f.close()

		# Generating graph
		print 'Generating graph'
		graph = UndirectedGraph()
		for i in range(0, MAX_ROW):
			for j in range(0, MAX_COL):
				graph.add_node((i,j,Orientation.up))
				graph.add_node((i,j,Orientation.left))
				graph.add_node((i,j,Orientation.down))
				graph.add_node((i,j,Orientation.right))
				
				graph.add_edge((i,j,Orientation.up), (i,j,Orientation.left))
				graph.add_edge((i,j,Orientation.left), (i,j,Orientation.down))
				graph.add_edge((i,j,Orientation.down), (i,j,Orientation.right))
				graph.add_edge((i,j,Orientation.right), (i,j,Orientation.up))

		for node, ws in walls.items():
			if ws[0] == 0:
				graph.add_edge((node[0],node[1],Orientation.up), (node[0]+1,node[1],Orientation.up))
			if ws[1] == 0:
				graph.add_edge((node[0],node[1],Orientation.left), (node[0],node[1]-1,Orientation.left))
			if ws[2] == 0:
				graph.add_edge((node[0],node[1],Orientation.down), (node[0]-1,node[1],Orientation.down))
			if ws[3] == 0:
				graph.add_edge((node[0],node[1],Orientation.right), (node[0],node[1]+1,Orientation.right))

		return graph

if __name__=="__main__":
	'''
		Supuestos de test: mapa en forma de T y comienza en (3,1,3)
	'''
	
	position = (2,0,1)
	loc = Localization('lab4.map')
	loc.add_observation(0)
	path = [position]
	print loc.locations

	while len(loc.locations) != 1:
		action,_ = loc.plan_action()
		if loc.apply_action(action, position) in loc.graph.edges[position]:
			position = loc.apply_action(action, position)
		else:
			action = action+1
			if not loc.apply_action(action, position) in loc.graph.edges[position]:
				raise Exception('Error')
			position = loc.apply_action(action, position)

		observation = loc.node_distance[position]
		loc.add_observation(observation, action=action)
		path.append(position)

	print 'Path: ', path
	print 'Final Location: ', loc.locations

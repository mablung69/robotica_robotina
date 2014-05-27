from enums import Orientation, Action
from graph import DirectedGraph
from planner import Planner

class Mapper(object):
	def __init__(self, max_cols, max_rows, location, goal, debug=False):
		self.max_rows = max_rows
		self.max_cols = max_cols
		self.debug = debug
		self.goal = goal

		self.location = location
		self.graph = self.init_map()
		
	def init_map(self):
		graph = DirectedGraph()
		orientations = [Orientation.up, Orientation.left, Orientation.down, Orientation.right]
		
		if self.debug:
			print '> Mapper::init_map Adding all nodes'

		# Add all nodes to graph
		for r in xrange(0, self.max_rows):
			for c in xrange(0, self.max_cols):
				for o in orientations:
					graph.add_node((r,c,o))

		# Add turn right and left to all node. 
		# Add move to all posible nodes
		for node in graph.nodes:
			graph.add_edge(node, (node[0], node[1], (node[2]+1)%4))
			graph.add_edge(node, (node[0], node[1], (node[2]-1)%4))

			if node[2] == Orientation.up and (node[0]+1, node[1], node[2]) in graph.nodes:
				graph.add_edge(node, (node[0]+1, node[1], node[2]))
			elif node[2] == Orientation.left and (node[0], node[1]-1, node[2]) in graph.nodes:
				graph.add_edge(node, (node[0], node[1]-1, node[2]))
			elif node[2] == Orientation.down and (node[0]-1, node[1], node[2]) in graph.nodes: 
				graph.add_edge(node, (node[0]-1, node[1], node[2]))
			elif node[2] == Orientation.right and (node[0], node[1]+1, node[2]) in graph.nodes:
				graph.add_edge(node, (node[0], node[1]+1, node[2]))
		return graph

	def plan_action(self):
		planner = Planner()
		planner.graph = self.graph
		path = planner.solve(self.location, self.goal)

		print '[DEBUG] Path: ', path

		if len(path) <= 1:
			return False
		else:
			next_state = path[1]
			turn = next_state[2] - self.location[2]
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
		

	def apply_action(self, action):
		if self.debug:
			print '> Mapper::apply_action \n\t-From ', self.location
		
		if action == Action.turn_left:
			self.location = (self.location[0], self.location[1], (self.location[2]+1)%4)
		elif action == Action.turn_right:
			self.location = (self.location[0], self.location[1], (self.location[2]-1)%4)
		elif action == Action.move:
			if self.location[2] == Orientation.up:
				self.location = (self.location[0]+1, self.location[1], self.location[2])
			if self.location[2] == Orientation.left:
				self.location = (self.location[0], self.location[1]-1, self.location[2])
			if self.location[2] == Orientation.down:
				self.location = (self.location[0]-1, self.location[1], self.location[2])
			if self.location[2] == Orientation.right:
				self.location = (self.location[0], self.location[1]+1, self.location[2])
		if self.debug:
			print '\t-To ', self.location

	def add_observation(self, observation):
		orientation = self.location[2]
		
		if orientation == Orientation.up:
			observed_location = (self.location[0]+observation, self.location[1], orientation)
			hipothesis_location = (self.location[0]+observation+1, self.location[1], orientation)
			if hipothesis_location in self.graph.nodes:
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)
				
				observed_location = (self.location[0]+observation, self.location[1], (orientation+2)%4)
				hipothesis_location = (self.location[0]+observation+1, self.location[1], (orientation+2)%4)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)


		elif orientation == Orientation.left:
			observed_location = (self.location[0], self.location[1]-observation, orientation)
			hipothesis_location = (self.location[0], self.location[1]-observation-1, orientation)
			if hipothesis_location in self.graph.nodes:
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)

				observed_location = (self.location[0], self.location[1]-observation, (orientation+2)%4)
				hipothesis_location = (self.location[0], self.location[1]-observation-1, (orientation+2)%4)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)


		elif orientation == Orientation.down:
			observed_location = (self.location[0]-observation, self.location[1], self.location[2])
			hipothesis_location = (self.location[0]-observation-1, self.location[1], orientation)
			if hipothesis_location in self.graph.nodes:
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)

				observed_location = (self.location[0]-observation, self.location[1], (orientation+2)%4)
				hipothesis_location = (self.location[0]-observation-1, self.location[1], (orientation+2)%4)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)


		else: #self.location[2] == Orientation.right:
			observed_location = (self.location[0], self.location[1]+observation, self.location[2])
			hipothesis_location = (self.location[0], self.location[1]+observation+1, orientation)
			if hipothesis_location in self.graph.nodes:
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)

				observed_location = (self.location[0], self.location[1]+observation, (orientation+2)%4)
				hipothesis_location = (self.location[0], self.location[1]+observation+1, (orientation+2)%4)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)

			

if __name__ == "__main__":
	from file_loader import FileLoader
	from time import sleep

	f_loader = FileLoader()
	f_loader.read_map('Mapas/With_Start/lab4.map')
	f_loader.generate_undirected_graph()
	f_loader.estimate_distances()

	location = f_loader.starts[0]
	goals    = f_loader.goals
	max_col  = f_loader.max_cols
	max_row  = f_loader.max_rows
	
	mapper   = Mapper(max_col,max_row,location,goals)
	mapper.init_map()

	print 'Location: ', mapper.location
	print 'Goals: ', mapper.goal

	test_path = [mapper.location]
	test_observation = []
	sleep(1)

	while True:

		observation = f_loader.node_distance[mapper.location]
		mapper.add_observation(observation)

		print '\n[DEBUG] Path ', test_path
		print '[DEBUG] Location ', mapper.location
		print '[DEBUG] Observation ', observation
		print '[DEBUG] Edges ', mapper.graph.edges[mapper.location]

		mapper.graph.write_map("../web_server/test.json",mapper.location)	
		sleep(1)
		
		action = mapper.plan_action()

		print '[DEBUG] Action ', action

		if type(action) == type(1):
			mapper.apply_action(action)
		else:
			break


		test_path.append(mapper.location)
		test_observation.append(observation)





	print 'Output PATH: ', test_path
	print 'Output OBSERVATION: ', test_observation





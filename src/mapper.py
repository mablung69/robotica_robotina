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
		planner = Planner
		planner.graph = self.graph
		path = planner.solve(self.location, self.goal)
		return path

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

	def add_observation(self, obsevation):
		orientation = self.location[2]
		for i in xrange(0,2):
			if orientation == Orientation.up:
				observed_location = (self.location[0]+obsevation, self.location[1], orientation)
				hipothesis_location = (self.location[0]+obsevation+1, self.location[1], orientation)
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)

			elif orientation == Orientation.left:
				observed_location = (self.location[0], self.location[1]-obsevation, orientation)
				hipothesis_location = (self.location[0], self.location[1]-obsevation-1, orientation)
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)

			elif orientation == Orientation.down:
				observed_location = (self.location[0]-obsevation, self.location[1], self.location[2])
				hipothesis_location = (self.location[0]-obsevation-1, self.location[1], orientation)
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)

			else: #self.location[2] == Orientation.right:
				observed_location = (self.location[0], self.location[1]+obsevation, self.location[2])
				hipothesis_location = (self.location[0], self.location[1]+obsevation+1, orientation)
				if hipothesis_location in self.graph.edges[observed_location]:
					self.graph.edges[observed_location].remove(hipothesis_location)
				if observed_location in self.graph.edges[hipothesis_location]:
					self.graph.edges[hipothesis_location].remove(observed_location)

			orientation = (orientation+2)%4

if __name__ == "__main__":
	from file_loader import FileLoader
	f_loader = FileLoader()
	f_loader.read_map('Mapas/With_Start/lab4_2.map')

	location = f_loader.starts[0]
	goals    = f_loader.goals
	mapper   = Mapper(3,3,location,goals)



from enums import Orientation
from graph import UndirectedGraph, DirectedGraph

class FileLoader(object):
	def __init__(self):
		self.walls  = {}
		self.starts = []
		self.goals  = []
		self.keys   = []

		self.max_cols = None
		self.max_rows = None

		self.undirected_graph = UndirectedGraph()
		self.directed_graph = DirectedGraph()
		self.distance_node = {}
		self.node_distance = {}


	def read_map(self, file_name):
		print 'Reading File'
		f = open(file_name, 'r')

		# Reading walls: [row, col, up, left, down, right]
		print '\t> Parsing walls'

		[self.max_rows, self.max_cols] = f.readline().split(' ')
		self.max_rows = int(self.max_rows)
		self.max_cols = int(self.max_cols)

		for i in range(0, self.max_rows*self.max_cols):
			data = f.readline().split(' ')
			print 'data: ', data
			data = map(int, data)
			self.walls[(data[0],data[1])] = (data[2],data[3],data[4], data[5])

		# Reading starts
		print '\t> Parsing ', f.readline()
		MAX_START = int(f.readline())

		for i in range(0, MAX_START):
			data = f.readline().split(' ')
			if data[2][0] == 'u':
				orientation = 0
			elif data[2][0] == 'l':
				orientation = 1
			elif data[2][0] == 'd':
				orientation = 2
			else:
				orientation = 3
			self.starts.append((int(data[0]),int(data[1]),orientation))

		# Reading Goals
		print '\t> Parsing ', f.readline()
		MAX_GOALS = int(f.readline())

		for i in range(0, MAX_GOALS):
			data = f.readline().split(' ')
			row = int(data[0])
			col = int(data[1])
			self.goals.append((row,col))

		# Reading Keys
		print '\t> Parsing ', f.readline()
		MAX_KEYS = int(f.readline())

		for i in range(0, MAX_KEYS):
			data = f.readline().split(' ')
			row = int(data[0])
			col = int(data[1])
			self.keys.append((row,col))

		f.close()

	def generate_undirected_graph(self):
		orientations = [Orientation.up, Orientation.left, Orientation.down, Orientation.right]

		for w in self.walls.keys():
			row = w[0]
			col = w[1]

			for o in orientations:
				self.undirected_graph.add_node((row,col,o))

			self.undirected_graph.add_edge((row,col,Orientation.up),    (row,col,Orientation.left))
			self.undirected_graph.add_edge((row,col,Orientation.left),  (row,col,Orientation.down))
			self.undirected_graph.add_edge((row,col,Orientation.down),  (row,col,Orientation.right))
			self.undirected_graph.add_edge((row,col,Orientation.right), (row,col,Orientation.up))

		for node, ws in self.walls.items():
			if ws[0] == 0:
				self.undirected_graph.add_edge((node[0],node[1],Orientation.up), (node[0]+1,node[1],Orientation.up))
			if ws[1] == 0:
				self.undirected_graph.add_edge((node[0],node[1],Orientation.left), (node[0],node[1]-1,Orientation.left))
			if ws[2] == 0:
				self.undirected_graph.add_edge((node[0],node[1],Orientation.down), (node[0]-1,node[1],Orientation.down))
			if ws[3] == 0:
				self.undirected_graph.add_edge((node[0],node[1],Orientation.right), (node[0],node[1]+1,Orientation.right))

	def generate_directed_graph(self):
		orientations = [Orientation.up, Orientation.left, Orientation.down, Orientation.right]

		for w in self.walls.keys():
			row = w[0]
			col = w[1]

			for o in orientations:
				self.directed_graph.add_node((row,col,o))

			self.directed_graph.add_edge((row,col,Orientation.up),    (row,col,Orientation.left))
			self.directed_graph.add_edge((row,col,Orientation.left),    (row,col,Orientation.up))

			self.directed_graph.add_edge((row,col,Orientation.left),  (row,col,Orientation.down))
			self.directed_graph.add_edge((row,col,Orientation.down),  (row,col,Orientation.left))

			self.directed_graph.add_edge((row,col,Orientation.down),  (row,col,Orientation.right))
			self.directed_graph.add_edge((row,col,Orientation.right),  (row,col,Orientation.down))

			self.directed_graph.add_edge((row,col,Orientation.right), (row,col,Orientation.up))
			self.directed_graph.add_edge((row,col,Orientation.up), (row,col,Orientation.right))

		for node, ws in self.walls.items():
			if ws[0] == 0:
				self.directed_graph.add_edge((node[0],node[1],Orientation.up), (node[0]+1,node[1],Orientation.up))
			if ws[1] == 0:
				self.directed_graph.add_edge((node[0],node[1],Orientation.left), (node[0],node[1]-1,Orientation.left))
			if ws[2] == 0:
				self.directed_graph.add_edge((node[0],node[1],Orientation.down), (node[0]-1,node[1],Orientation.down))
			if ws[3] == 0:
				self.directed_graph.add_edge((node[0],node[1],Orientation.right), (node[0],node[1]+1,Orientation.right))

	def estimate_distances(self):
		#print '> Exploring distances'
		nodes = self.undirected_graph.nodes

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

				if not test_node in self.undirected_graph.edges[aux_node]: #BUG
					break
				aux_node = test_node
				distance = distance + 1

			self.distance_node.setdefault(distance, [])
			self.distance_node[distance].append(node)
			self.node_distance[node] = distance

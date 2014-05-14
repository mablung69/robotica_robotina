import math
from graph import DirectedGraph
from astar import shortest_path
from enums import Orientation
from localization import Localization

class Planner(object):

	def __init__(self):
		pass

	def build_graph(self,file_name):
		walls = {}
		start = []
		goals = []

		print '> Reading File'
		f = open(file_name, 'r')

		# Reading walls: [row, col, up, left, down, right]
		print '> Parsing walls'
		[MAX_ROW, MAX_COL] = f.readline().split(' ')
		MAX_ROW = int(MAX_ROW)
		MAX_COL = int(MAX_COL)

		for i in range(0, MAX_ROW*MAX_COL):		
			data = f.readline().split(' ')
			print 'data: ', data
			data = map(int, data)
			walls[(data[0],data[1])] = (data[2],data[3],data[4], data[5])

		# Reading Goals
		print '> Parsing ', f.readline()
		MAX_GOALS = int(f.readline())

		for i in range(0, MAX_GOALS):
			data = f.readline().split(' ')
			row = int(data[0])
			col = int(data[1])
			if data[2][0] == 'u':
				orientation = Orientation.up
			elif data[2][0] == 'l':
				orientation = Orientation.left
			elif data[2][0] == 'd':
				orientation = Orientation.down
			else:
				orientation = Orientation.right
			
			goals.append((row,col,orientation))

		MAX_DEPH = int(f.readline())
		f.close()

		print '> Goals: ', goals

		print '> Generating graph'
		# Generating graph
		graph = DirectedGraph()

		for i in range(0, MAX_ROW):
			for j in range(0, MAX_COL):
				graph.add_node((i,j,Orientation.up))
				graph.add_node((i,j,Orientation.left))
				graph.add_node((i,j,Orientation.down))
				graph.add_node((i,j,Orientation.right))
				
				graph.add_edge((i,j,Orientation.up), (i,j,Orientation.left))
				graph.add_edge((i,j,Orientation.up), (i,j,Orientation.right))

				graph.add_edge((i,j,Orientation.left), (i,j,Orientation.down))
				graph.add_edge((i,j,Orientation.left), (i,j,Orientation.up))

				graph.add_edge((i,j,Orientation.down), (i,j,Orientation.right))
				graph.add_edge((i,j,Orientation.down), (i,j,Orientation.left))
				
				graph.add_edge((i,j,Orientation.right), (i,j,Orientation.up))
				graph.add_edge((i,j,Orientation.right), (i,j,Orientation.down))

		for node, ws in walls.items():
				if ws[0] == 0:
					graph.add_edge((node[0],node[1],Orientation.up), (node[0]+1,node[1],Orientation.up))
				if ws[1] == 0:
					graph.add_edge((node[0],node[1],Orientation.left), (node[0],node[1]-1,Orientation.left))
				if ws[2] == 0:
					graph.add_edge((node[0],node[1],Orientation.down), (node[0]-1,node[1],Orientation.down))
				if ws[3] == 0:
					graph.add_edge((node[0],node[1],Orientation.right), (node[0],node[1]+1,Orientation.right))

		return [graph,goals,walls]

	def do_planning(self,file_name,start):
		[graph,goals,walls]=self.build_graph(file_name)
		solution=self.solve(graph,start,goals)
		print '\t Path:  ', solution
		return [solution,walls]

	def solve(self,graph,start,goals):
		print '==> Solving shortest path with A* Algorithm'

		print '\t Start: ', start
		print '\t Goal:  ', goals

		for node, edges in graph.edges.items():
			print node, ': ', edges

		dist = lambda c1, c2: math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2)
		path = shortest_path(graph, start, goals[0], dist)

		return path

if __name__=="__main__":

	plan= Planner()
	path=plan.do_planning("map2.map",(0,1,2))
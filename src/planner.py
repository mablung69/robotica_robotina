import math
from graph import DirectedGraph
from astar import shortest_path

class Planner(object):

	def __init__(self):
		self.graph = DirectedGraph()

	def do_planning(self,file_name,start):
		[graph,goals,walls]=self.build_graph(file_name)
		solution=self.solve(graph,start,goals)
		#print '\t Path:  ', solution
		return [solution,walls]

	def solve(self,start,goals):
		# print '==> Solving shortest path with A* Algorithm'

		# print '\t Start: ', start
		# print '\t Goal:  ', goals

		# for node, edges in self.graph.edges.items():
		# 	print node, ': ', edges

		dist = lambda c1, c2: math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2)
		path = shortest_path(self.graph, start, goals[0], dist)

		return path

if __name__=="__main__":

	plan= Planner()
	path=plan.do_planning("map2.map",(0,1,2))
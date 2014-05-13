# a* algorithm
"""
    A* uses a best-first search and finds the least-cost path from a given 
    initial node to one goal node (out of one or more possible goals).
     
    It uses a distance-plus-cost heuristic function (usually denoted f(x)) to 
    determine the order in which the search visits nodes in the tree. The 
    distance-plus-cost heuristic is a sum of two functions:
     
        * the path-cost function, which is the cost from the starting node to 
          the current node (usually denoted g(x))
     
        * and an admissible "heuristic estimate" of the distance to the goal 
          (usually denoted h(x)).
     
    The h(x) part of the f(x) function must be an admissible heuristic; that is,
    it must not overestimate the distance to the goal. Thus, for an application 
    like routing, h(x) might represent the straight-line distance to the goal, 
    since that is physically the smallest possible distance between any two 
    points or nodes.
     
    If the heuristic h satisfies the additional condition h(x) \le d(x,y) + h(y)
    for every edge x, y of the graph (where d denotes the length of that edge),
    then h is called monotone, or consistent. In such a case, A* can be 
    implemented more efficiently roughly speaking, no node needs to be 
    processed more than once (see closed set below)and A* is equivalent to 
    running Dijkstra's algorithm with the reduced cost 
    d'(x,y): = d(x,y) - h(x) + h(y).
     
    Note that A* has been generalized into a bidirectional heuristic search 
    algorithm; see bidirectional search.
     
    -source wikipedia: http://en.wikipedia.org/wiki/A*_algorithm
"""
 
from graph import DirectedGraph
 
def astar(graph, initial_node, goal_node, h):
    closed_set = set() # set of nodes already evaluated
    nodes = set() # set of tentative nodes to be evaluated
    nodes.add(initial_node)

    # goal_node = goal_nodes.pop()
    # goal_nodes.add(goal_node)
 
    visited = {} # map of navigated nodes
    g_score = {initial_node: 0} # distance from start along optimal path
    h_score = {initial_node: h(initial_node, goal_node)} # heuristic estimate
    f_score = {initial_node: h_score[initial_node]} # estimated dist
 
    while nodes:
        x = None
        for node in nodes:
            if x is None:
                x = node
            elif f_score[node] < f_score[x]:
                x = node
 
        nodes.remove(x)
        if x == goal_node:
            return visited
 
        closed_set.add(x)
        for y in graph.edges[x]:
            if y in closed_set:
                continue
            tentative_g_score = g_score[x] + graph.distances[(x, y)]
 
            flag = False
            if y not in nodes or tentative_g_score < g_score[y]:
                nodes.add(y)
                flag = True
 
            if flag:
                visited[y] = x
 
                g_score[y] = tentative_g_score
                h_score[y] = h(y, goal_node)
                f_score[y] = g_score[y] + h_score[y]
 
    return False
 
def shortest_path(graph, initial_node, goal_node, h):
    paths = astar(graph, initial_node, goal_node, h)
    route = [goal_node]

    while goal_node != initial_node:
        route.append(paths[goal_node])
        goal_node = paths[goal_node]
 
    route.reverse()
    return route
 
 
 # Testing algorithm
if __name__ == '__main__':
    import math
    sldist = lambda c1, c2: math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2)
    g = Graph()
    g.add_node((0, 0))
    g.add_node((1, 1))
    g.add_node((1, 0))
    g.add_node((0, 1))
    g.add_node((2, 2))
 
    g.add_edge((0, 0), (1, 1), 1.5)
    g.add_edge((0, 0), (0, 1), 1.2)
    g.add_edge((0, 0), (1, 0), 1)
    g.add_edge((1, 0), (2, 2), 2)
    g.add_edge((0, 1), (2, 2), 2)
    g.add_edge((1, 1), (2, 2), 1.5)
 
    assert shortest_path(g, (0, 0), (2, 2), sldist) == [(0, 0), (1, 1), (2, 2)]
 
    g.distances[((0, 0), (1, 1))] = 2
    g.distances[((1, 1), (0, 0))] = 2
 
    assert shortest_path(g, (0, 0), (2, 2), sldist) == [(0, 0), (1, 0), (2, 2)]
 
    g.distances[((0, 0), (1, 0))] = 1.3
    g.distances[((1, 0), (0, 0))] = 1.3
 
    assert shortest_path(g, (0, 0), (2, 2), sldist) == [(0, 0), (0, 1), (2, 2)]
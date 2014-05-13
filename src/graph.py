class DirectedGraph(object):
    """
    A simple directed, weighted graph
    """
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.distances = {}
 
    def add_node(self, value):
        print '\t>>DirectedGraph::Adding node: ', value
        self.nodes.add(value)
 
    def add_edge(self, from_node, to_node, distance=1):
        print '\t>>DirectedGraph::Adding edge: ', from_node, ' - ', to_node
        self._add_edge(from_node, to_node, distance)
 
    def _add_edge(self, from_node, to_node, distance):
        self.edges.setdefault(from_node, [])
        self.edges[from_node].append(to_node)
        self.distances[(from_node, to_node)] = distance

class UndirectedGraph(object):
    """
    A simple undirected, weighted graph
    """
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.distances = {}

    def add_node(self, value):
        print '\t>>UndirectedGraph::Adding node: ', value
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance=1):
        print '\t>>UndirectedGraph::Adding edge: ', from_node, ' - ', to_node
        self._add_edge(from_node, to_node, distance)
        self._add_edge(to_node, from_node, distance)

    def _add_edge(self, from_node, to_node, distance):
        self.edges.setdefault(from_node, [])
        self.edges[from_node].append(to_node)
        self.distances[(from_node, to_node)] = distance
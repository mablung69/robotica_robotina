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

    def write_map(self,path,location=(0,0,0),plan=[]):
        try:
            import json

            data = self.get_map(location,plan)

            with open(path, 'w') as outfile:
                json.dump(data, outfile)
        except:
            pass

    def push_map(self,location=(0,0,0),plan=[]):
        try:
            import pusher
            import json

            data = self.get_map(location,plan)

            p = pusher.Pusher(app_id='76093', key='60ac382824573be1ddd2', secret='d43a1c915d852c869dc0')
            p['robotina'].trigger('map',{'map': json.dumps(data)})
        except:
            pass
    
    def get_map(self,location,plan):
        
        map_nodes = {}
        graph = self

        max_rows = 0
        max_cols = 0

        for node in graph.nodes:
            if not map_nodes.has_key(str((node[0],node[1]))):
                walls = []
          
                #Top wall
                if (node[0]+1, node[1], 0) in graph.nodes and (node[0]+1,node[1],0) in graph.edges[(node[0],node[1],0)]:
                    walls.append(0)
                else:
                    walls.append(1)
                #Left wall
                if (node[0], node[1]-1, 1) in graph.nodes and (node[0], node[1]-1, 1) in graph.edges[(node[0],node[1],1)]:
                    walls.append(0)
                else:
                    walls.append(1)
                #Bot wall
                if (node[0]-1, node[1], 2) in graph.nodes and (node[0]-1, node[1], 2) in graph.edges[(node[0],node[1],2)]:
                    walls.append(0)
                else:
                    walls.append(1)
                #Right wall
                if (node[0], node[1]+1, 3) in graph.nodes and (node[0], node[1]+1, 3) in graph.edges[(node[0],node[1],3)]:
                    walls.append(0)
                else:
                    walls.append(1)

                if node[0] + 1 > max_rows:
                    max_rows = node[0] + 1

                if node[1] + 1 > max_cols:
                    max_cols = node[1] + 1

                map_nodes[str((node[0],node[1]))] = walls
        
        return { "size": [max_rows, max_cols], "map": map_nodes, "location": location, "plan": plan }



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

if __name__ == '__main__':
    from file_loader import FileLoader
    loader=FileLoader()

    loader.read_map("Mapas/With_Start/lab4.map")
    loader.generate_directed_graph()

    print loader.directed_graph.get_map()

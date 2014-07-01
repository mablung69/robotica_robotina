
def get_combinations(walls, k):

  ret_array = []

  for i in xrange(0, 2**len(walls) ):

    arr = is_valid(i,k,len(walls))

    if arr :
      array = []
      for i in arr:
        array.append(walls[i])
      ret_array.append(array)
  return ret_array

def is_valid(num,k,max_walls):
  counter = []
  for i in xrange(0,max_walls):
    if( (1 << i) & num > 0 ):
      counter.append(i)
    if len(counter) > k:
      return False
  return counter

if __name__=="__main__":

  test = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]

  k = 1

  comb = get_combinations(test,k)

  for item in comb:
    print item

##

def get_best_plan_with_keys(self):
  walls_list = []
  best_plan = None
  best_plan_dist = 999999

  for node, walls in self.walls.items():
    for i,w in enumerate(walls):
      if w == 1:
        if walls[Orientation.up] == 1 and i == Orientation.up:
          aux = (node[0]+1,node[1], Orientation.up)
        elif walls[Orientation.left] == 1 and i == Orientation.left:
          aux = (node[0],node[1]-1, Orientation.left)
        elif walls[Orientation.down] == 1 and i == Orientation.down:
          aux = (node[0]-1,node[1], Orientation.down)
        elif walls[Orientation.right] == 1 and i == Orientation.right:
          aux = (node[0],node[1]+1, Orientation.right)

        if aux in graph.nodes:
          walls_list.append( (node[0],node[1],i) )

  print 'starting combination'

  combs = self.get_combinations(walls_list,self.keys_available)

  print len(combs)
  print combs

  for comb in combs:
    planner = Planner()
    planner.graph = graph

    self.add_comb(comb)

    path = planner.solve(self.actual_position, [self.target])

    self.remove_comb(comb)

    if(len(path) < best_plan_dist):
      best_plan_dist = len(path)
      best_plan = path

  return best_plan


def add_comb(self,comb):
  for node in comb:
    n_from = node
    n_to = ()
    if node[2] == Orientation.up:
      n_to = (node[0]+1,node[1], Orientation.up)
    elif node[2] == Orientation.left:
      n_to = (node[0],node[1]-1, Orientation.left)
    elif node[2] == Orientation.down:
      n_to = (node[0]-1,node[1], Orientation.down)
    elif node[2] == Orientation.right:
      n_to = (node[0],node[1]+1, Orientation.right)
    self.graph.add_edge( n_from, n_to)

def remove_comb(self,comb):
  for node in comb:
    n_from = node
    n_to = ()
    if node[2] == Orientation.up:
      n_to = (node[0]+1,node[1], Orientation.up)
    elif node[2] == Orientation.left:
      n_to = (node[0],node[1]-1, Orientation.left)
    elif node[2] == Orientation.down:
      n_to = (node[0]-1,node[1], Orientation.down)
    elif node[2] == Orientation.right:
      n_to = (node[0],node[1]+1, Orientation.right)
    self.graph.disconect( n_from, n_to)

def get_combinations(self,walls, k):

  ret_array = []

  for i in xrange(0,2**len(walls)):

    arr = self.is_valid(i,k,len(walls))

    if arr :
      array = []
      for i in arr:
        array.append(walls[i])
      ret_array.append(array)
  return ret_array

def is_valid(self,num,k,max_walls):
  counter = []
  for i in xrange(0,max_walls):
    if( (1 << i) & num > 0 ):
      counter.append(i)
    if len(counter) > k:
      return False
  return counter

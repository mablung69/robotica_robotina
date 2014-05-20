def wolrdInit():

    s="<sdf version='1.4'>\n  <world name='default'>\n    <!-- A global light source -->\n    <include>\n      <uri>model://sun</uri>\n    </include>\n    <!-- A ground plane -->\n    <include>\n      <uri>model://ground_plane</uri>\n    </include>\n    <!-- Own physics settings to speed up simulation -->\n    <physics type='ode'>\n      <max_step_size>0.01</max_step_size>\n      <real_time_factor>1</real_time_factor>\n      <real_time_update_rate>100</real_time_update_rate>\n      <gravity>0 0 -9.8</gravity>\n    </physics>\n    <!-- <pose>x y z roll pitch yaw</pose> -->\n"
    return s

def wolrdEnd():

    s="  </world>\n</sdf>"
    return s

def writeWall(num, pos):

    s="    <include>\n      <uri>model://maze_wall</uri>\n      <name>wall_" + str(num) + "</name>\n      <pose> " + pos + " </pose>\n    </include>\n"
    return s

def writeWallRotated(num, pos):

    s="    <include>\n      <uri>model://maze_wall_rotated</uri>\n      <name>wall_rotated_" + str(num) + "</name>\n      <pose> " + pos + " </pose>\n    </include>\n"
    return s

#path corresponde a la direccion donde quieren que se cree el archivo word
path=""
f = open('map2.map', 'r')
o = open(path+'maze2.world', 'w')

(m, n) = map(int, f.readline().strip().split(' '))


maze=[]
for i in xrange(m):
    temp=[]
    for j in xrange(n):
        temp.append("")
    maze.append(temp)

#leemos el archivo
line = f.readline()
while not line.strip() =="START":

    (x, y, w) = map(str, line.strip().split(' ',2))
    maze[int(x)][int(y)]=w
    line = f.readline()

#creamos el archivo .word
x=0
y=0
z=1.2
wall=0
wall_r=0
s=""
s+=wolrdInit()
for i in xrange(m):
    for j in xrange(n):
        (u, l, d, r) = map(int, maze[i][j].strip().split(' '))
        if u==1 or d==1:
            if u==1:
                s+=writeWall(wall, str(x+(z)*(j)) + " " + str(y+(z)*i +z) + " 0 0 0 0")
                wall+=1
            if d==1:
                s+=writeWall(wall, str(x+(z)*(j)) + " " + str(y+(z)*i) + " 0 0 0 0")
                wall+=1
        if l==1 or r==1:
            if l==1:
                s+=writeWallRotated(wall_r, str(x+(z)*(j)) + " " + str(y+(z)*i) + " 0 0 0 0")
                wall_r+=1
            if r==1:
                s+=writeWallRotated(wall_r, str(x+(z)*(j) + z) + " " + str(y+(z)*i) + " 0 0 0 0")
                wall_r+=1
#print s
s+=wolrdEnd()
o.write(s)

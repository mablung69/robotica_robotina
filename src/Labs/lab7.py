#import Packages
import math
import sys
import cv2
import cv2.cv as cv
import numpy as np
import thread
import time
import multiprocessing
import pickle

#import Clases
from ..localization import Localization
from ..planner import Planner
from ..mapper import Mapper
from ..futbol_planner import FutbolPlanner
from ..file_loader import FileLoader

#import Enums
from ..enums import Action, RobotState
from .. import properties

#import Methods
from ..Robot.turtle_bot import get_robot
from ..robot_operations import do_observation_front,get_action

def show_image(threadName,robot, delay = 0):

  while True:
    k = cv2.waitKey(1)

    if robot.cv_image != None:
      img = robot.cv_image
      height, width, depth = img.shape
      p1 = ( width / 2 - robot.current_w_corr_win / 2 , height / 2 - robot.h_corr_win / 2 )
      p2 = ( width / 2 + robot.current_w_corr_win / 2 , height / 2 + robot.h_corr_win / 2 )
      cv2.rectangle(img, p1, p2 , (0,0,255))
      cv2.imshow("Image", img)

    if k == 27:
      cv2.destroyAllWindows()
      break

    time.sleep(delay)

def push(mapper,loc,plan,signs,goals,keys,players):

  mapper.graph.push_map(loc,plan=plan,signals=signs,goals=goals,keys=keys,players=players)

#main
if __name__=="__main__":

  pool = multiprocessing.Pool(processes=1)

  robot = get_robot()
  filename = properties.file_name

  f_loader = FileLoader()
  f_loader.read_map(filename)
  f_loader.generate_undirected_graph()
  f_loader.generate_directed_graph()
  f_loader.estimate_distances()

  location 		= f_loader.starts[0]
  goals    		= f_loader.goals
  max_col  		= f_loader.max_cols
  max_row  		= f_loader.max_rows
  graph    		= f_loader.directed_graph
  node_distance 	= f_loader.node_distance
  walls = f_loader.walls
  keys = f_loader.keys

  thread.start_new_thread( show_image, ("Thread-1",robot, ) )

  robot.node_distance = node_distance
  futbol_planner = FutbolPlanner(graph, location, node_distance, goals, keys , walls)
  robot.planner = futbol_planner
  action = futbol_planner.plan_action()

  if robot.get_observation() <= 0:
    robot.apply_action(Action.recognize,0)

  while True:
    print 'Iteration: ', futbol_planner.actual_position, ' ', RobotState.to_string(futbol_planner.current_state)
    robot.play_sound(6)
    observation = max(robot.get_observation(),0)
    #mapper.add_observation(observation)

    pool.apply_async( push, [futbol_planner,
                            futbol_planner.actual_position,
                            futbol_planner.current_plan,
                            futbol_planner.sign_position,
                            futbol_planner.goals,
                            futbol_planner.keys,
                            futbol_planner.player_position],callback=None )

    if type(action) == type(1):
      futbol_planner.apply_action(action)
      robot.apply_action(action,observation)

      if robot.get_observation() <= 0:
        robot.apply_action(Action.recognize,0)

      if robot.last_signal != None:
        futbol_planner.add_sign(robot.last_signal)
        robot.last_signal = None

      if robot.last_player != None:
        futbol_planner.add_player(robot.last_player)
        robot.last_player = None

      action = futbol_planner.plan_action()

    else:
      break

    if futbol_planner.check_ending():
      pool.apply_async( push, [futbol_planner,
                              futbol_planner.actual_position,
                              futbol_planner.current_plan,
                              futbol_planner.sign_position,
                              futbol_planner.goals,
                              futbol_planner.keys,
                              futbol_planner.player_position],callback=None )
      break

  robot.play_sound(6)

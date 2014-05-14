import sys
import time
import numpy as np
import math
import cv2
from cv2 import cv
from cv_bridge import CvBridge, CvBridgeError 
import rospy
import pygame
from kobuki_msgs.msg import BumperEvent
from kobuki_msgs.msg import Led
from kobuki_msgs.msg import Sound
from kobuki_msgs.msg import WheelDropEvent
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
from tf import transformations as trans
from RobotinaImage import RobotinaImage
from enums import Action

_turtlebot_singleton = None

import pickle


def get_robot():
    global _turtlebot_singleton
    if _turtlebot_singleton is None:
        _turtlebot_singleton = Turtlebot()
    return _turtlebot_singleton


class Turtlebot(object):
    max_linear = 0.25
    min_linear = 0.05
    max_angular = 2.0
    d1 = 0.7
    d2 = 0.6
    deltaD = d1-d2
    speed_const = max_linear / deltaD
    v0 = speed_const * d2
    

    def __init__(self):

        rospy.init_node('pyturtlebot', anonymous=True)
        rospy.myargv(argv=sys.argv)

        self.horrible = None
        self.image_procesor = RobotinaImage(maze=True)
        self.current_maze_state = True

        self.__x = None
        self.__y = None
        self.__angle = None
        self.__cumulative_angle = 0.0
        self.__have_odom = False
        self.bridge = CvBridge()

        self.on_bumper = None
        self.current_state = None
        self.current_substate = None

        self.current_min_dist = None
        self.stop_dist = 0.8
        self.speed_const = 0.7 / 1.4

        self.movement_enabled = True
        self.current_laser_msg = None
        
        self.current_cv_image = None
        self.current_cv_rgb_image = None
        self.current_mask = None
        self.current_depth_msg = None
        self.current_max_depth=None
        self.current_rgb_image = None

        self.current_img_track = []
        self.current_depth_track = []
        self.current_target_x = None
        self.current_target_y = None
        self.current_target_depth = None
        self.current_laser_depth = [-1, -1, -1]

        self.current_maze_depth = None

        self.crop_h = 480
        self.crop_w = 480

        self.__cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist)
        self.__bumper_sub = rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, self.__bumper_handler)
        self.__odom_sub = rospy.Subscriber('/odom', Odometry, self.__odom_handler)
        self.__wheeldrop_sub = rospy.Subscriber('/mobile_base/events/wheel_drop',
                                                WheelDropEvent, self.__wheeldrop_handler)
        self.__scan_sub = rospy.Subscriber('/scan', LaserScan, self.__scan_handler)
        self.__sound_pub = rospy.Publisher('/mobile_base/commands/sound', Sound)
        self.__led_pubs = {
            '1': rospy.Publisher('/mobile_base/commands/led1', Led),
            '2': rospy.Publisher('/mobile_base/commands/led2', Led),
        }
        
        #-----KINECT HANDLERS---#

        #para simulador
        self.__depth_img = rospy.Subscriber('/camera/depth/image_raw',Image ,self.__depth_handler)
        #for real
        #self.__depth_img = rospy.Subscriber('/camera/depth/image',Image ,self.__depth_handler)
        
        self.__rgb_img= rospy.Subscriber('/camera/rgb/image_color',Image,self.__rgb_handler)


    def move(self, linear=0.0, angular=0.0):
        """Moves the robot at a given linear speed and angular velocity

        The speed is in meters per second and the angular velocity is in radians per second

        """
        self.__exit_if_movement_disabled()
        # Bounds checking
        if abs(linear) > self.max_linear:
            self.say("Whoa! Slowing you down to within +/-{0} m/s...".format(self.max_linear))
            linear = self.max_linear if linear > self.max_linear else linear
            linear = -self.max_linear if linear < -self.max_linear else linear
        if abs(angular) > self.max_angular:
            self.say("Whoa! Slowing you down to within +/-{0} rad/s...".format(self.max_angular))
            angular = self.max_angular if angular > self.max_angular else angular
            angular = -self.max_angular if angular < -self.max_angular else angular
        # Message generation
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        # Announce and publish
        #self.say("Moving ('{linear}' m/s, '{angular}' rad/s)...".format(linear=linear, angular=angular))
        self.__cmd_vel_pub.publish(msg)

    def move_distance(self, distance, velocity=1.0):
        """Moves a given distance in meters

        You can also give it a speed in meters per second to travel at:

            robot.move_distance(1, 0.5)  # Should take 2 seconds
        """
        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)
        while not self.__have_odom and not rospy.is_shutdown():
            self.say("Waiting for odometry")
            r.sleep()

        msg = Twist()
        msg.linear.x = velocity
        x0 = self.__x
        y0 = self.__y
        r = rospy.Rate(100)
        while not rospy.is_shutdown():
            d = ((self.__x - x0)**2 + (self.__y - y0)**2)**0.5
            if d >= distance:
                break

            self.__cmd_vel_pub.publish(msg)
            r.sleep()
        msg.linear.x = 0.0
        self.__cmd_vel_pub.publish(msg)

    def turn_angle(self, angle, velocity=1.0):
        """Turns the robot a given number of degrees in radians

        You can easily convert degress into radians with the radians() function:

            robot.turn_angle(radians(45))  # Turn 45 degrees

        You can also give an angular velocity to turn at, in radians per second:

            robot.turn_angle(radians(-45), radians(45))  # Turn back over a second
        """
        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)
        while not self.__have_odom and not rospy.is_shutdown():
            self.say("Waiting for odometry")
            r.sleep()

        msg = Twist()
        if angle >= 0:
            msg.angular.z = np.abs(velocity)
        else:
            msg.angular.z = -np.abs(velocity)
        angle0 = self.__cumulative_angle
        r = rospy.Rate(100)
        while not rospy.is_shutdown():
            a_diff = self.__cumulative_angle - angle0
            if (angle > 0 and a_diff >= angle) or (angle < 0 and a_diff <= angle):
                break

            self.__cmd_vel_pub.publish(msg)
            r.sleep()
        msg.angular.z = 0.0
        self.__cmd_vel_pub.publish(msg)

    def stop(self):
        """Stops the robot"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.say("Stopping the robot!")
        self.__cmd_vel_pub.publish(msg)

    def wait(self, seconds):
        """This function will wait for a given number of seconds before returning"""
        self.say("Waiting for '{0}' seconds.".format(seconds))
        time.sleep(seconds)

    def say(self, msg):
        """Prints a message to the screen!"""
        print(msg)
        sys.stdout.flush()

    sounds = {
        'turn on': Sound.ON,
        'turn off': Sound.OFF,
        'recharge start': Sound.RECHARGE,
        'press button': Sound.BUTTON,
        'error sound': Sound.ERROR,
        'start cleaning': Sound.CLEANINGSTART,
        'cleaning end': Sound.CLEANINGEND,
    }

    def play_sound(self, sound_type):
        """Plays a sound on the Turtlebot

        The available sound sequences:
            - 0 'turn on'
            - 1 'turn off'
            - 2 'recharge start'
            - 3 'press button'
            - 4 'error sound'
            - 5 'start cleaning'
            - 6 'cleaning end'

        You can either pass the string or number above
        """
        if not isinstance(sound_type, (int, str)):
                self.say("!! Invalid sound type, must be an Integer or a String!")
                return
        if isinstance(sound_type, str):
            try:
                sound_type = self.sounds[sound_type]
            except KeyError:
                self.say("!! Invalid sound '{0}', must be one of: {1}"
                         .format(sound_type, self.sounds.keys()))
                return
        self.__sound_pub.publish(Sound(sound_type))

    led_colors = {
        'off': Led.BLACK,
        'black': Led.BLACK,
        'green': Led.GREEN,
        'orange': Led.ORANGE,
        'red': Led.RED,
    }

    def set_led(self, led, color):
        """Set the color of an LED

        You can set LED 1 or LED 2 to any of these colors:

        - 'off'/'black'
        - 'green'
        - 'orange'
        - 'red'

        Example:

            robot.set_led(1, 'green')
            robot.wait(1)
            robot.set_led(1, 'off')
        """
        if str(led) not in self.__led_pubs:
            self.say("!! Invalid led '{0}', must be either '1' or '2'".format(led))
            return
        if color not in self.led_colors:
            self.say("!! Invalid led color '{0}', must be one of: {1}".format(color, self.led_colors))
            return
        self.__led_pubs[str(led)].publish(Led(self.led_colors[color]))

    def reset_movement(self):
        self.movement_enabled = True

    def __odom_handler(self, msg):
        self.__x = msg.pose.pose.position.x
        self.__y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        a = trans.euler_from_quaternion([q.x, q.y, q.z, q.w])[2]

        # cumulative angle doesn't wrap. assumes we've not moved more than pi radians
        # since last odom message
        if self.__have_odom:
            a_diff = a - self.__angle
            if a_diff > np.pi:
                a_diff -= 2*np.pi
            elif a_diff < -np.pi:
                a_diff += 2*np.pi
            self.__cumulative_angle += a_diff

        self.__angle = a
        self.__have_odom = True

    def __scan_handler(self, msg):
        self.current_laser_msg = msg

    def __bumper_handler(self, msg):
        if msg.state != BumperEvent.PRESSED:
            return
        if msg.bumper not in [BumperEvent.CENTER, BumperEvent.LEFT, BumperEvent.RIGHT]:
            return
        if self.on_bumper is not None:
            self.on_bumper.__call__()

    def __exit_if_movement_disabled(self):
        if not self.movement_enabled:
            self.say("Movement currently disabled")
            sys.exit()

    def __wheeldrop_handler(self, msg):
        if msg.state == WheelDropEvent.DROPPED:
            self.movement_enabled = False

    def __depth_handler(self, data):
        try:
            self.current_depth_msg = data
            self.current_cv_image = self.bridge.imgmsg_to_cv(data,"32FC1")            

            h = 5
            w = 5
            img = np.asarray(self.current_cv_image)
            max_h, max_w = img.shape
            
            # Depth 1/4 of width
            #img_aux = img[max_h*1/2-h:max_h*1/2+h, max_w*1/4-w:max_w*1/4+w]
            #img_aux = img_aux[~np.isnan(img_aux)]
            #if len(img_aux)>1:
            #    self.current_laser_depth[0] = max(img_aux) / 1000
            #else:
            #    self.current_laser_depth[0] = -1

            # Depth 2/4

            img_aux = img[max_h*1/2-h:max_h*1/2+h, max_w/2-w:max_w/2+w]
            left_aux = img_aux[:,0]
            right_aux = img_aux[:,2*w-1]
            img_aux = img_aux[~np.isnan(img_aux)]
            if len(img_aux)>1:
                self.current_max_depth = max(img_aux) / 1000
            else:
                self.current_max_depth = -1

            #center
            self.current_laser_depth[1] = self.current_max_depth

            left_aux = left_aux[~np.isnan(left_aux)]
            right_aux = right_aux[~np.isnan(right_aux)]
            if len(img_aux)>1:
                #Left
                self.current_laser_depth[0] = max(left_aux) / 1000
                #Right
                self.current_laser_depth[2] = max(right_aux) / 1000
            else:
                self.current_laser_depth[0] = -1
                self.current_laser_depth[2] = -1

            # Depth 3/4 of width
            #img_aux = img[max_h*1/2-h:max_h*1/2+h, max_w*3/4-w:max_w*3/4+w]
            #img_aux = img_aux[~np.isnan(img_aux)]
            #if len(img_aux)>1:
            #    self.current_laser_depth[2] = max(img_aux) / 1000
            #else:
            #    self.current_laser_depth[2] = -1            

        except CvBridgeError, e:
            print e

    def __rgb_handler(self,data):
        
        self.current_rgb_image=data
        self.current_cv_rgb_image = self.bridge.imgmsg_to_cv(data,"bgr8")
        #self.__track_red()

     

    def __track_red(self):

        img = np.asarray(self.current_cv_rgb_image)
        x, self.horrible = self.image_procesor.image_analisis(img)

        # img = cv2.blur(img,(5,5))
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # lower = np.array([170,160,60])
        # upper = np.array([180,256,256])

        # mask = cv2.inRange(hsv, lower, upper)
        # mask = cv2.blur(mask,(5,5))
        
        # self.current_mask = mask
        
        # M=cv2.moments(mask)
        
        if x != None:
            if self.current_state == "searching":
                self.current_state = "following"

            centroid_x= x
            # centroid_y= int(M['m01']/M['m00'])
            # self.current_target_x = centroid_x
            # self.current_target_y = centroid_y
        
        else:
            self.current_state = "searching"
        print self.current_state

    def move_searh_n_destroy(self, lin_velocity, angle_velocity):

        if self.current_substate == None:
            self.current_substate = "turning"
        if self.current_state == None:
            self.current_state = "following"
        
        #print self.current_state
        #print "MINDIST: ",self.current_min_dist

        #lin_velocity = min(self.max_linear, lin_velocity)
        if self.current_state == "searching":

            if self.current_substate == "moving":
                pass#self.move(linear= lin_velocity)
            elif self.current_substate == "turning":
                pass#self.move(angular= angle_velocity, linear=0)
            elif self.current_substate == "backwards":
                pass#self.move_distance(.1,-lin_velocity)
                #self.move(angular= angle_velocity)

        elif self.current_state == "following":
            #print (str(self.current_target_x) + "   "+ str(self.current_target_depth))
            if self.current_target_x != None and self.current_target_depth != None:
                                
                
                factor_a = float(self.current_target_x) - 320.0                
                factor_l =  (float(self.current_target_depth) - self.stop_dist ) / 2.0 

                if abs(float(self.current_target_depth) - self.stop_dist) < 0.2 :
                    lin_velocity = 0 
                
                #print "Vel: "+ str(lin_velocity * factor_l)
                #print "Target: ", float(self.current_target_depth)
                #print "Stop at: ", float(self.stop_dist)

                #self.move(linear = lin_velocity, angular = angle_velocity * -1 * factor_a / 320.0 )

    def move_maze(self, lin_velocity, angle_velocity):
        threshold = 0.15
        if self.current_maze_state != None:
            angle_velocity = angle_velocity
            _min = 0.2
            if self.current_max_depth < 0.5:
                self.move( angular = angle_velocity * np.sign(self.current_maze_state))
            else:
                if self.current_maze_state > threshold:
                    self.move(linear = lin_velocity , angular = angle_velocity * self.current_maze_state +_min)
                elif self.current_maze_state < -threshold:
                    self.move(linear = lin_velocity , angular = angle_velocity * self.current_maze_state -_min)
                else:
                    lin_velocity = lin_velocity
                    self.move(linear = lin_velocity , angular= 0)
                    #self.move(linear = lin_velocity*self.current_maze_depth + .1 , angular= 0)

    def turn_maze_angle(self, angle, velocity=1.0):
        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)
        while not self.__have_odom and not rospy.is_shutdown():
            self.say("Waiting for odometry")
            r.sleep()

        msg = Twist()
        if angle >= 0:
            msg.angular.z = np.abs(velocity)
        else:
            msg.angular.z = -np.abs(velocity)
        angle0 = self.__cumulative_angle
        r = rospy.Rate(100)
        while not rospy.is_shutdown():
            a_diff = self.__cumulative_angle - angle0
            if (angle > 0 and a_diff >= angle) or (angle < 0 and a_diff <= angle):
                break

            self.__cmd_vel_pub.publish(msg)
            r.sleep()

        msg.angular.z = 0.0
        self.__cmd_vel_pub.publish(msg)

        #if self.current_max_depth < 0.8:
        #    self.correct_short_angle(velocity)

    def move_maze_distance(self, distance,lin_velocity):
        print '>> Tuttlebot::Move maze distance(distance, velocity)', distance, ' , ', lin_velocity
        
        self.__exit_if_movement_disabled()
        r = rospy.Rate(100)

        while self.current_max_depth == None:
            self.say("Waiting for kinect")
            r.sleep()

        msg = Twist()
        msg.linear.x = lin_velocity

        d0 = self.current_max_depth
        while not rospy.is_shutdown():
            delta = d0 - self.current_max_depth
            print self.current_laser_depth
            if delta >= distance:
                break
            self.__cmd_vel_pub.publish(msg)
            r.sleep()

        msg.linear.x = 0.0
        self.__cmd_vel_pub.publish(msg)    
        self.say(0)

        if self.current_max_depth < 0.8:
            self.align_wall(lin_velocity)

    def align_wall(self, lin_velocity):
        self.__exit_if_movement_disabled()
        r = rospy.Rate(100)

        while self.current_max_depth == None:
            self.say("Waiting for kinect")
            r.sleep()

        msg = Twist()
        msg.linear.x = lin_velocity

        while not rospy.is_shutdown():
            if self.current_max_depth <= 0.6:
                break
            self.__cmd_vel_pub.publish(msg)
            r.sleep()

        msg.linear.x = 0.0
        self.__cmd_vel_pub.publish(msg)    
        self.say(0)

    def correct_short_angle(self, velocity=1):
        print self.current_laser_depth
        for i in xrange(0,3):
            if self.current_laser_depth[i] == -1:
                return 0

        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)

        msg = Twist()
        
        angle0 = self.__cumulative_angle
        r = rospy.Rate(100)
        while not rospy.is_shutdown():

            if self.current_laser_depth[0] - self.current_laser_depth[2] > 0:
                msg.angular.z = np.abs(-velocity)
            else:
                msg.angular.z = np.abs(velocity)

            if self.current_laser_depth[1] < self.current_laser_depth[0] and self.current_laser_depth[1] < self.current_laser_depth[2]:
                break  

            self.__cmd_vel_pub.publish(msg)
            r.sleep()

        msg.angular.z = 0.0
        self.__cmd_vel_pub.publish(msg)
        self.wait(1)

 
    def correct_long_angle(self):
        pass

    def move_maze_wall(self, lin_velocity):
        move_threshold = 0.6
        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)
        while not self.__have_odom and not rospy.is_shutdown():
            self.say("Waiting for odometry")
            r.sleep()

        while self.current_max_depth == None:
            self.say("Waiting for kinect")
            r.sleep()

        r = rospy.Rate(100)
        while not rospy.is_shutdown():
            if self.current_max_depth <= move_threshold:
                break
            self.move_maze(lin_velocity, 0.0)
            r.sleep()
        self.move(0,0)

    def apply_action(self,action,observation):
        if action==Action.move:
            if observation>0:
                self.move_maze_distance(0.8,0.2)
                return True
            else:
                return False
        elif action==Action.turn_left:
            self.turn_maze_angle(math.pi/2,0.3)
            return True
        elif action==Action.turn_right:
            self.turn_maze_angle(-math.pi/2,0.3)
            return True
        else:
            raise Exception("acton invalid")
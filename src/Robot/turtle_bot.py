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
from ..enums import Player, Action, Sign
from ..soundx import Soundx
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import pickle
import time

_turtlebot_singleton = None

from ..face_detector import loadTraining, FaceDetector
from ..signal_detector import SignalDetector


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

        self.found_players = {}
        self.found_players[Player.claudio] = 0
        self.found_players[Player.alexis] = 0
        [self.clf,self.pca]=loadTraining()

        path="/home/turtlebot/IIC_3684/robotina/sandbox/robotica_robotina/clasifier.yml"
        self.model=cv2.createEigenFaceRecognizer()
        self.model.load(path)

        self.signal_detector = SignalDetector()
        self.face_detector = FaceDetector()
        self.node_distance = None
        self.planner = None

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
        self.iterator = 0
        self.current_laser_msg = None

        self.current_cv_image = None
        self.current_cv_rgb_image = None
        self.current_mask = None
        self.current_depth_msg = None
        self.current_max_depth=None
        self.current_rgb_image = None
        self.cv_image = None
        self.last_signal = None
        self.last_player = None

        self.current_img_track = []
        self.current_depth_track = []
        self.current_target_x = None
        self.current_target_y = None
        self.current_target_depth = None
        self.current_laser_depth = [-1, -1, -1]

        self.current_maze_depth = None

        self.crop_h = 480
        self.crop_w = 480

        self.h_depth_win = 50
        self.w_depth_win = 50

        self.h_corr_win = 5
        self.w_corr_win = 30

        self.left_column = None
        self.right_column = None

        self.current_w_corr_win = self.w_corr_win

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

    def recognize(self):

        print 'RECOGNIZE !'
        #cv_image = CvBridge().imgmsg_to_cv2(self.current_rgb_image, self.current_rgb_image.encoding)
        sign_prediction = None
        cv_image = np.asarray(self.current_cv_rgb_image)

        #print "imagen"+str(int(self.iterator))+".png"
        #cv2.imwrite("wall_imgs/imagen"+str(int(self.iterator))+".png", cv_image )

        best_detection=None

        Data = []

        detections = self.face_detector.detect(cv_image)
        im_copy = cv_image

        for (x,y,w,h) in detections:
            sub_img=cv_image[y:y+h,x:x+w]
            sub_img=cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
            sub_img=cv2.resize(sub_img,(200,200))
            sub_img=np.resize(sub_img,(1,np.prod(sub_img.shape)))
            Data.append(sub_img)

        if len(Data)>0:
            mat=np.zeros((len(Data),Data[0].shape[1]))
            for index_data in xrange(0,len(Data)):
                mat[index_data,:]=Data[index_data]

            mat=self.pca.transform(mat)
            array_probs = self.clf.predict_proba(mat)

            print array_probs

            selected=[]        
            for i in xrange(0,array_probs.shape[0]):
                ind=np.argmax(array_probs[i,:])
                selected.append([array_probs[i,ind],ind])

            best_proba=0
            ind_best_proba=-1
            for i in xrange(0,len(selected)):
                if(selected[i][0]>best_proba):
                    best_proba=selected[i][0]
                    ind_best_proba=i

            p_label=selected[ind_best_proba][1]
            p_confidence=selected[i][0]

            b1=p_label==1 and p_confidence>.7
            b2=p_label==0 and p_confidence>.50

            if (b1 or b2) and (not b1 or not b2) :
                best_detection = p_label
                x=detections[ind_best_proba][0]
                y=detections[ind_best_proba][1]
                w=detections[ind_best_proba][2]
                h=detections[ind_best_proba][3]
                cv2.rectangle(cv_image,(x,y),(x+w,y+h),(255,0,0),2)
                player = self.face_detector.to_string(p_label)
                cv2.putText(cv_image,player,(x,y),cv2.FONT_HERSHEY_PLAIN, 2,(0,0,255))
                print 'Player:', Player.to_string(p_label)
                print 'Score: ', p_confidence

        else:
            print "No player found"

        #if best_detection == None:
        if best_detection == None:
            signals = self.signal_detector.circle_detect(cv_image)
            for top, bottom in signals:
                s = cv_image[top[1]:bottom[1], top[0]:bottom[0]]
                sign_prediction, score = self.signal_detector.knn_predict(s)
                cv2.rectangle(im_copy, top, bottom, (255,0,0), 2)

        self.cv_image = cv_image

        #output = open('pickle'+str(self.iterator)+'.pkl', 'wb')
        self.iterator +=1.
        #pickle.dump(cv_image, output)
        #output.close()

        #respuesta del request
        #return [p_label,p_confidence]
        if best_detection != None:
                "Playing sound"
                s = Soundx()
                s.play_player(best_detection)
                self.last_player = best_detection
        elif sign_prediction != None and score<0.3:
            print 'Signal: ', Sign.to_string(sign_prediction)
            print 'Signal Score: ', score
            self.last_signal = sign_prediction
        else:
            print 'No detections'

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

            obs_init= 0
            if self.current_max_depth != None:
                obs_init=max(int(round((self.current_max_depth-0.5)/0.8,0)),0)

            h = self.h_depth_win
            w = self.w_corr_win

            h2 = self.h_corr_win

            if obs_init > 1:
                w2 = 3 * self.w_corr_win
            else:
                w2 = self.w_corr_win

            self.current_w_corr_win = w2

            img = np.asarray(self.current_cv_image)
            max_h, max_w = img.shape

            img_aux = img[max_h*1/2-h:max_h*1/2+h, max_w/2-w:max_w/2+w]
            img_aux = img_aux[~np.isnan(img_aux)]
            if len(img_aux)>1:
                self.current_max_depth = max(img_aux) / 1000
            else:
                self.current_max_depth = -1

            #center
            self.current_laser_depth[1] = self.current_max_depth

            img_aux = img[max_h*1/2-h2:max_h*1/2+h2, max_w/2-w2:max_w/2+w2]
            left_aux = img_aux[:,0]
            right_aux = img_aux[:,2*w2-1]
            left_aux = left_aux[~np.isnan(left_aux)]
            right_aux = right_aux[~np.isnan(right_aux)]

            if len(img_aux)>1:
                #Left
                self.current_laser_depth[0] = np.average(left_aux) / 1000
                #Right
                self.current_laser_depth[2] = np.average(right_aux) / 1000
            else:
                self.current_laser_depth[0] = -1
                self.current_laser_depth[2] = -1

            img_aux = img
            left_aux = img_aux[:,0]
            right_aux = img_aux[:,639]
            left_aux = left_aux[~np.isnan(left_aux)]
            right_aux = right_aux[~np.isnan(right_aux)]
            if len(img_aux)>1:
                #Left extreme
                self.left_column = np.average(left_aux) / 1000
                #Right extreme
                self.right_column = np.average(right_aux) / 1000
            else:
                self.left_column = -1
                self.right_column = -1

        except CvBridgeError, e:
            print e

    def get_observation(self):
        while self.current_max_depth == None:
            self.wait(0.5)
        actual_depth=self.current_max_depth
        obs_init=max(int(round((actual_depth-0.5)/0.8,0)),-1)
        return obs_init

    def __rgb_handler(self,data):
        self.current_rgb_image=data
        self.current_cv_rgb_image = self.bridge.imgmsg_to_cv(data,"bgr8")

    def turn_maze_angle(self, angle, velocity=1.0, correct=True):
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
            if (angle > 0 and a_diff >= angle - 0.1 ) or (angle < 0 and a_diff <= angle + 0.1):
                break
            #print 'Get observation: ', self.get_observation()
            #print 'Final observation: ', self.node_distance[self.planner.actual_position]
            if self.node_distance[self.planner.actual_position] >= 2 and self.get_observation() == self.node_distance[self.planner.actual_position]:
                #self.turn_angle( 5*math.pi/90 * math.copysign(1,msg.angular.z))
                pass#break

            self.__cmd_vel_pub.publish(msg)
            r.sleep()

        msg.angular.z = 0.0
        self.__cmd_vel_pub.publish(msg)

        if correct:
            #self.align_wall(0.1)
            self.correct_angle()
            self.align_wall(0.1)
            self.correct_angle()

    def move_maze_distance(self, distance,lin_velocity):
        print '>> Tuttlebot::Move maze distance(distance, velocity)', distance, ' , ', lin_velocity

        self.__exit_if_movement_disabled()
        r = rospy.Rate(100)

        while self.current_max_depth == None:
            self.say("Waiting for kinect")
            r.sleep()

        #msg = Twist()
        #msg.linear.x = lin_velocity
        #msg.angular.z = 0

        # d0 = self.current_max_depth
        # while not rospy.is_shutdown():
        #     #print(self.left_column,"   ",self.right_column)
        #     delta = d0 - self.current_max_depth
        #     #
        #     #print msg.angular.z
        #     if delta >= distance:
        #         break
            
        #     self.__cmd_vel_pub.publish(msg)
        #     r.sleep()

        # msg.linear.x = 0.0
        # self.__cmd_vel_pub.publish(msg)
        
        msg = Twist()
        msg.linear.x = lin_velocity
        msg.angular.z = 0
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

        self.say(0)

        self.align_wall(lin_velocity)

        self.correct_angle()

        self.align_wall(lin_velocity)


    def align_wall(self, lin_velocity):
        self.__exit_if_movement_disabled()
        r = rospy.Rate(100)

        obs_init=self.get_observation()

        if obs_init <= 0 and self.node_distance[self.planner.actual_position] == 0:
            msg = Twist()
            
            if self.current_max_depth > (0.4):
                msg.linear.x = lin_velocity
            else:
                msg.linear.x = -lin_velocity

            threshold = 0.1

            while not rospy.is_shutdown():
                #self.play_sound(0)
                print 'Distance to wall: ',self.current_max_depth - 0.4
                obs_init=self.get_observation()
                if abs(self.current_max_depth - (0.4)) < threshold:
                    break
                self.__cmd_vel_pub.publish(msg)
                r.sleep()

            msg.linear.x = 0.0
            self.__cmd_vel_pub.publish(msg)

        elif obs_init >= 1:
            msg = Twist()
            msg.linear.x = lin_velocity

            if self.current_max_depth > (0.4+0.8*obs_init):
                msg.linear.x = lin_velocity
            else:
                msg.linear.x = -lin_velocity

            threshold = 0.1

            while not rospy.is_shutdown():
                self.play_sound(0)
                obs_init=self.get_observation()
                if abs(self.current_max_depth - (0.4+0.8*obs_init)) < threshold:
                    break
                self.__cmd_vel_pub.publish(msg)
                r.sleep()

            msg.linear.x = 0.0
            self.__cmd_vel_pub.publish(msg)

    def correct_angle(self):

        if self.get_observation() <= 0 and self.node_distance[self.planner.actual_position] == 0:
            self.correct_short_angle()
        elif self.node_distance[self.planner.actual_position] < 2:
            self.correct_short_angle()
        else:
            pass#self.correct_long_angle()

    def correct_short_angle(self):

        print 'Correcting short angle'

        for i in xrange(0,3):
            if self.current_laser_depth[i] == -1:
                print 'Obs : ',-1
                return 0

        self.__exit_if_movement_disabled()
        # No bounds checking because we trust people. Not like William.
        r = rospy.Rate(1)

        msg = Twist()

        angle0 = self.__cumulative_angle
        r = rospy.Rate(1000)
        max_iter = 2000
        i = 0
        while not rospy.is_shutdown():
            # self.play_sound(1)
            print i," : ", abs(self.current_laser_depth[0] - self.current_laser_depth[2])
            if self.current_laser_depth[0] - self.current_laser_depth[2] > 0: # Turn right
                msg.angular.z = -np.abs(0.6)
            else: # Turn left
                msg.angular.z = np.abs(0.6)

            print 'Angle: ',abs(self.current_laser_depth[0] - self.current_laser_depth[2]), ' < ', 0.008

            obs_init=max(int(round((self.current_max_depth-0.5)/0.8,0)),0)
            if (abs(self.current_laser_depth[0] - self.current_laser_depth[2])) < 0.008 or (i > max_iter):
                break

            self.__cmd_vel_pub.publish(msg)
            i+=1

            r.sleep()

        msg.angular.z = 0.0
        self.__cmd_vel_pub.publish(msg)

    def correct_long_angle(self):
        obs_init  = self.current_max_depth
        obs_final = self.node_distance[self.planner.actual_position]*.8 + .4
        while abs(obs_init - obs_final) > 0.1:
            self.turn_angle(5*math.pi/90)

    def request_open_door(self):
        print "ABREME PLX"
        s = Soundx()
        s.play_action(Action.open_door)
        init_dist = self.get_observation()
        current_dist = -10
        r = rospy.Rate(1000)
        
        while current_dist <= init_dist:
            print 'ABRAME LA PUERTA PORFAVOR'
            current_dist = self.get_observation()
            r.sleep()

        s.play_action(Action.thanks)

    def apply_action(self,action,observation):
        if action==Action.move:
            if observation>0:
                self.move_maze_distance(0.8,0.15)
            else:
                return False
        elif action==Action.turn_left:
            self.turn_maze_angle(math.pi/2,0.7)
        elif action==Action.turn_right:
            self.turn_maze_angle(-math.pi/2,0.7)
        elif action==Action.recognize:
            self.recognize()
        elif action == Action.open_door:
            self.request_open_door()
        elif action==Action.nothing:
          pass
        else:
            raise Exception("acton invalid")

        return True
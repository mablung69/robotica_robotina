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

        h2 = 5
        w2 = 30

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
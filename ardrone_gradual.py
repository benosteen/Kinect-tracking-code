#!/usr/bin/env python

import liblo, sys, getpass, telnetlib

from time import time

class DroneStatus(dict):
    mapping = {'x':0, 'y':1, 'z':2}
    rotate_mapping = {'rr':1.0, 'rl':-1.0} # direction set for rr and rl
    def __init__(self, horizontal_thresholds = [0.4, 0.4, 0.5], rotational_threshold = 0.3, update_period=150):   # every 150ms
        self.horizontal = [0.0, 0.0, 0.0]# (x,y,z) speeds
        self.rotational = 0.0 # rotate about the vertical axis
        self.horizontal_thresholds = list(horizontal_thresholds)
        self.rotational_threshold = rotational_threshold
        
        self.update_period = update_period
        self.tick = time()

        self.__initialised = True

    def __setattr__(self, item, value):
        """Allow arbitrary settings, but threshold the values to the ones preset in the init (+/-)
        """
        if not self.__dict__.has_key("_DroneStatus__initialised"):
            return dict.__setattr__(self, item, value)
        if item in ['x', 'y', 'z']:
            try:
                f_value = float(value)
                index = self.mapping[item]
                if abs(f_value) > self.horizontal_thresholds[index]:
                        f_value = self.horizontal_thresholds[index] * (f_value/abs(f_value))
                self.horizontal[index] = f_value
            except Exception:
                print "Values given must be floats or integers"
        elif item in ['rr', 'rl', 'rotational']:
            try:
                f_value = float(value)
                direction = 1.0
                if item != 'rotational':
                    direction = self.rotate_mapping(item)
                elif f_value:
                    direction = abs(f_value)/f_value

                if f_value > self.rotational_threshold:
                    f_value = self.rotational_threshold * direction
                elif f_value < 0:
                    f_value = 0.0
                self.rotational = f_value
            except Exception:
                print "Values given must be floats or integers"
        elif item == 'horizontal' and len(item) == 3:
            self.x = item[0]
            self.y = item[1]
            self.z = item[2]
        else:
            dict.__setattr__(self, item, value)

    def __getattr__(self, item):
        """Maps values to attributes."""
        if item in ['x', 'y', 'z']:
            return self.horizontal[self.mapping[item]]
        else:
            return dict.__getattr__(self, item)
    
    def update_due(self):
        if (time() - self.tick) > self.update_period:
            self.tick = time()
            return True
        else:
            return False

# create server, listening on port 1234
class CommandData(liblo.Server):
    def __init__(self, port, debug = False):
    
    HOST = "localhost"
    PORT = 54000

    self.drone = DroneStatus()

    self.tn = telnetlib.Telnet(HOST,PORT)
    print self.tn.read_very_eager()
    self.tn.write("drone.altitude();\n")
    ALT = self.tn.read_very_eager()
    print ALT
    self.tn.write("drone.trim();\n")

    self.ymulti = 1.0
    self.zmulti = 1.0
    self.rmulti = 1.0
    self.sidemulti = 1.0

    try:
        super(CommandData, self).__init__(port)
        # For takeoff and landing commands
        self.add_method("/command", 's', self.command_callback)
        # For gradual flight changes
        self.add_method("/differentials", 'fffff', self.differentials_callback)
            
        # register a fallb`ack for unhandled messages
        self.add_method(None, None, self.fallback)
        self.debug = debug
            
    except liblo.ServerError, err:
        print str(err)
        sys.exit()

    def command_callback(self, path, args):
        self.tn.write("drone.altitude();\n")
        ALT = self.tn.read_very_eager()
        print ALT
        [s] = args
        print s
        if self.debug:
            print "Recieved command: '%s'" % s
        if s == 'takeoff':
            self.tn.write("drone.takeoff();\n")
            print "Takeoff\n"
        if s == 'landing':
            self.tn.write("drone.landing();\n")
            print "Landing\n"
        """
        """
    def differentials_callback(self, path, args):
        dy, dz, dh, dr, dside = args
        # dh deadzone:
        ythreshold = 0.1
        zthreshold = 0.2
        rthreshold = 0.2
        sidethreshold = 0.2
        if not dh <= 0.3:
            # In control:
            if abs(dy) > ythreshold:
                self.drone.z = dy * self.ymulti
            if abs(dz) > zthreshold:
                self.drone.y = dz * self.zmulti
            if abs(dr) > rthreshold:
                self.drone.rotational = dr * self.rmulti
            if abs(dside) > sidethreshold:
                self.drone.x = dside * self.sidemulti
        else:
            self.drone.horizontal = (0.0, 0.0, 0.0)
            self.drone.rotational = 0.0
    
    def fallback(self, path, args, types, src):
        if self.debug:
            print "got unknown message '%s' from '%s'" % (path, src.get_url())
            for a, t in zip(args, types):
                print "argument of type '%s': %s" % (t, a)
    def update_drone(self):
        if self.drone.update_due():
            self.tn.write("drone.speedZ = %s;\n" % self.drone.z)
            self.tn.write("drone.speedY = %s;\n" % self.drone.y)
            self.tn.write("drone.speedYaw = %s;\n" % self.drone.rotational)
            self.tn.write("drone.speedX = %s;\n" % self.drone.x)
            return True
        else:
            return False
            
if __name__ == "__main__":
    # loop and dispatch messages every 100ms
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print "Usage: ardrone_gradual.py [debug]"
        sys.exit(2)
    else:
        debug = False
        if len(sys.argv) > 1:
            debug = True
        server = CommandData(7111, debug)
        while True:
            try:
                server.recv(100)
                if server.update():
                    print "Drone: Side:%s, Forward:%s, Vert:%s, Rot:%s" % (server.drone.horizontal + [server.drone.rotational])
            except KeyboardInterrupt:
                sys.exit(0)

#!/usr/bin/env python

import liblo, sys, getpass, telnetlib

# create server, listening on port 1234
class CommandData(liblo.Server):
    def __init__(self, port, debug = False):
	
	HOST = "localhost"
	PORT = 54000

	self.tn = telnetlib.Telnet(HOST,PORT)
	print self.tn.read_very_eager()
	self.tn.write("drone.altitude();\n")
	ALT = self.tn.read_very_eager()
	print ALT
	self.tn.write("drone.trim();\n")

	try:
            super(CommandData, self).__init__(port)
            self.add_method("/command", 's', self.command_callback)
            
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
	    pass
	if s == 'landing':
            self.tn.write("drone.landing();\n")
	    print "Landing\n"
	    pass
        if s == 'u':
            self.tn.write("drone.speedZ = 0.4;\n")
        elif s == 'd':
            self.tn.write("drone.speedZ = -0.4;\n")
            #mode ar drone down...
        if s == 'nu':
            self.tn.write("drone.speedZ = 0;\n")
        elif s == 'nd':
            self.tn.write("drone.speedZ = 0;\n")
            #mode ar drone down...
        elif s == 'f':
            self.tn.write("drone.speedY = -0.1;\n")
            # forward
            pass
        elif s == 'nf':
            self.tn.write("drone.speedY = 0.0;\n")
            # forward
            pass
        elif s == 'b':
            self.tn.write("drone.speedY = 0.1;\n")
            # back
            pass
        elif s == 'nb':
            self.tn.write("drone.speedY = 0.1;\n")
            # back
            pass
        elif s == 'rr':
            self.tn.write("drone.speedYaw = -0.5;\n")
            # forward
            pass
        elif s == 'nrr':
            self.tn.write("drone.speedYaw = 0.0;\n")
            # forward
            pass
        elif s == 'rl':
            self.tn.write("drone.speedYaw = 0.5;\n")
            # back
            pass
        elif s == 'nrl':
            self.tn.write("drone.speedYaw = 0.0;\n")
            # back
            pass
        elif s == 'yl':
            self.tn.write("drone.speedX = -0.5;\n")
            # forward
            pass
        elif s == 'nyl':
            self.tn.write("drone.speedX = 0.0;\n")
            # forward
            pass
        elif s == 'yr':
            self.tn.write("drone.speedX = 0.5;\n")
            # back
            pass
        elif s == 'nyr':
            self.tn.write("drone.speedX = 0.0;\n")
            # back
            pass
    
    
    def fallback(self, path, args, types, src):
        if self.debug:
            print "got unknown message '%s' from '%s'" % (path, src.get_url())
            for a, t in zip(args, types):
                print "argument of type '%s': %s" % (t, a)


if __name__ == "__main__":
    # loop and dispatch messages every 100ms
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print "Usage: ardrone.py [debug]"
        sys.exit(2)
    else:
        debug = False
        if len(sys.argv) > 1:
            debug = True
        server = CommandData(7111, debug)
        while True:
            try:
                server.recv(100)
            except KeyboardInterrupt:
                sys.exit(0)

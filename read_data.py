#!/usr/bin/env python

import liblo, sys

# create server, listening on port 1234
class OSCServer(liblo.Server):
    def __init__(self, port):
        try:
            super(OSCServer, self).__init__(port)
            self.add_method("/new_user", 'i', self.new_user_callback)
            self.add_method("/lost_user", 'i', self.lost_user_callback)
            self.add_method("/new_skel", 'i', self.new_skel_callback)
            self.add_method("/joint", 'sifff', self.joint_callback)
            
            # register a fallback for unhandled messages
            self.add_method(None, None, self.fallback)
            
            self.lh = {1:(-10.0,-10.0,-10.0)}
            self.ls = {1:(-10.0,-10.0,-10.0)}
            self.rh = {1: (-10.0,-10.0,-10.0)}
            self.rs = {1:(-10.0,-10.0,-10.0)}
            
            self.currentuser = 0
            
        except liblo.ServerError, err:
            print str(err)
            sys.exit()

    def new_user_callback(self, path, args):
        i = args
        print "New User '%s'" % (i)

    def new_skel_callback(self, path, args):
        i = args
        print "New User '%s' skeleton calibrated" % (i)
        
    def lost_user_callback(self, path, args):
        i = args.pop()
        print "Lost User '%s' - removing data" % (i)
        self.lh[i] = (-10.0,-10.0,-10.0)
        self.rh[i] = (-10.0,-10.0,-10.0)
        self.ls[i] = (-10.0,-10.0,-10.0)
        self.rs[i] = (-10.0,-10.0,-10.0)
        

    def joint_callback(self, path, args):
        s, i, x, y, z = args
        if s.startswith("r_hand"):
            self.rh[i] = (x,1.0-y,z)
#            print "User:%s - Joint '%s' (%s,%s,%s)" % (i, s, x, y, z)
        if s.startswith("l_hand"):
            self.lh[i] = (x,1.0-y,z)
#            print "User:%s - Joint '%s' (%s,%s,%s)" % (i, s, x, y, z)
        if s.startswith("r_shoulder"):
            self.rs[i] = (x,1.0-y,z)
#            print "User:%s - Joint '%s' (%s,%s,%s)" % (i, s, x, y, z)
        if s.startswith("l_shoulder"):
            self.ls[i] = (x,1.0-y,z)
#            print "User:%s - Joint '%s' (%s,%s,%s)" % (i, s, x, y, z)
    
    def fallback(self, path, args, types, src):
        pass
        #print "got unknown message '%s' from '%s'" % (path, src.get_url())
        #for a, t in zip(args, types):
        #    print "argument of type '%s': %s" % (t, a)


if __name__ == "__main__":
    # loop and dispatch messages every 100ms
    server = OSCServer(7110)
    while True:
        server.recv(100)

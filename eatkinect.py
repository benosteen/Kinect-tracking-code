#!/usr/bin/env python

import liblo, sys

# create server, listening on port 1234
class EatKinectData(liblo.Server):
    def __init__(self, port):
        try:
            super(EatKinectData, self).__init__(port)
            self.add_method("/joint", 'iffffff', self.joint_callback)
            
            # register a fallback for unhandled messages
            self.add_method(None, None, self.fallback)
            
        except liblo.ServerError, err:
            print str(err)
            sys.exit()

    def joint_callback(self, path, args):
        i, rx, ry, rz, lx, ly, lz = args
        print "User:%s - Joints (%s,%s,%s), (%s,%s,%s)" % (i, rx, ry, rz, lx, ly, lz)
    
    def fallback(self, path, args, types, src):
        print "got unknown message '%s' from '%s'" % (path, src.get_url())
        for a, t in zip(args, types):
            print "argument of type '%s': %s" % (t, a)


if __name__ == "__main__":
    # loop and dispatch messages every 100ms
    server = EatKinectData(7111)
    while True:
        server.recv(100)

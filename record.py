#!/usr/bin/env python

import liblo, sys

# create server, listening on port 1234
class RecordData(liblo.Server):
    def __init__(self, port, filename, debug = False):
        try:
            super(RecordData, self).__init__(port)
            self.add_method("/combined", 'iffffffffffff', self.joint_callback)
            
            # register a fallb`ack for unhandled messages
            self.add_method(None, None, self.fallback)
            self.o = open(filename, "w+")
            self.debug = debug
            
        except liblo.ServerError, err:
            print str(err)
            sys.exit()

    def joint_callback(self, path, args):
        i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz = args
        if self.debug:
            print "User:%s - Hands r(%s,%s,%s), l(%s,%s,%s)" % (i, rx, ry, rz, lx, ly, lz)
            print "User:%s - Shoulders r(%s,%s,%s), l(%s,%s,%s)" % (i, rx, ry, rz, lx, ly, lz)
        self.o.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz))
    
    def fallback(self, path, args, types, src):
        if self.debug:
            print "got unknown message '%s' from '%s'" % (path, src.get_url())
            for a, t in zip(args, types):
                print "argument of type '%s': %s" % (t, a)


if __name__ == "__main__":
    # loop and dispatch messages every 100ms
    if not len(sys.argv) >= 2:
        print "Usage: record.py recording_filename [debug]"
        sys.exit(2)
    else:
        filename = sys.argv[1]
        debug = False
        if len(sys.argv) > 2:
            debug = True
        print "Recording to file: '%s'" % filename
        server = RecordData(7111, filename, debug)
        while True:
            try:
                server.recv(100)
            except KeyboardInterrupt:
                server.o.close()
                sys.exit(0)

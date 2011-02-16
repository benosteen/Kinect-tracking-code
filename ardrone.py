#!/usr/bin/env python

import liblo, sys

# create server, listening on port 1234
class CommandData(liblo.Server):
    def __init__(self, port, debug = False):
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
        s = args
        print s
        if self.debug:
            print "Recieved command: '%s'" % s
        if s == 'u':
            # move ardrone up...
            pass
        elif s == 'd':
            #mode ar drone down...
            pass
        elif s == 'f':
            # forward
            pass
        elif s == 'b':
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

#!/usr/bin/env python

from read_data import OSCServer

import sys, os
import liblo

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *

import re

ip_p = re.compile(r"([^:]+):([\d]+)", re.U)

endpoints = [('localhost', 7110)]
targets = []

def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def emphasis_point(x,y,z, size=0.02, colour=(0.5,0.5,1.0)):
    glColor3f(*colour)
    glBegin(GL_QUADS)
    glVertex3f(x-size, y+size, z)
    glVertex3f(x+size, y+size, z)
    glVertex3f(x+size, y-size, z)
    glVertex3f(x-size, y-size, z)
    glEnd()


def draw(server):
    global rquad, rq_diff
    rquad = 0.0
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()	
    glTranslatef(-1.0,-1.0,-3.0)
    glRotatef(rquad,0.0,1.0,0.0)
    glBegin(GL_LINE_LOOP)

    glColor3f(1.0,1.0,1.0)
    
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(2.0,0.0,0.0)
    glVertex3f(2.0,2.0,0.0)
    glVertex3f(0.0,2.0,0.0)
    glVertex3f(0.0,0.0,0.0)
    glEnd()
    
    
    glLoadIdentity()	
    glTranslatef(-1.0,-1.0,-3.0)
    glRotatef(rquad,0.0,1.0,0.0)
    glBegin(GL_LINE_LOOP)

    glColor3f(1.0,1.0,1.0)
    
    glVertex3f(0.0,0.0,-3.0)
    glVertex3f(2.0,0.0,-3.0)
    glVertex3f(2.0,2.0,-3.0)
    glVertex3f(0.0,2.0,-3.0)
    glVertex3f(0.0,0.0,-3.0)
    glEnd()
    
    glLoadIdentity()	
    glTranslatef(-1.0,-1.0,-3.0)
    glRotatef(rquad,0.0,1.0,0.0)
    glBegin(GL_LINES)

    glColor3f(1.0,1.0,1.0)
    
    glVertex3f(0.0,0.0,-3.0) # Back bottom left to top left
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(2.0,0.0,-3.0)
    glVertex3f(2.0,0.0,0.0)
    glVertex3f(2.0,2.0,-3.0)
    glVertex3f(2.0,2.0,0.0)
    glVertex3f(0.0,2.0,-3.0)
    glVertex3f(0.0,2.0,0.0)
    glEnd()
    
    glLoadIdentity()	
    glTranslatef(0.0,0.0,-3.0)
    
    glTranslatef(-0.5,-0.5,0.0)
    for player in server.lh.keys():
        glBegin(GL_LINES)

        glColor3f(1.0,0.0,1.0)
        glVertex3f(*server.rh[player])
        glVertex3f(*server.lh[player])
        glColor3f(0.8,0.8,0.8)
        glVertex3f(*server.lh[player])
        glVertex3f(*server.ls[player])
        glVertex3f(*server.rh[player])
        glVertex3f(*server.rs[player])
        glEnd()
        emphasis_point(*server.rh[player], colour=(1.0,0.3,0.4))
        emphasis_point(*server.lh[player])
        # And now, shoulder joints
        emphasis_point(*server.ls[player], colour=(0.3, 0.3, 0.7))
        emphasis_point(*server.rs[player], colour=(0.7, 0.2, 0.2))
        

class UserState(object):
    def __init__(self):
        self.lh = {}
        self.rh = {}
        self.ls = {}
        self.rs = {}
    def update(self, i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz):
        i = int(i)
        self.rh[i] = (float(rx),float(ry),float(rz))
        self.lh[i] = (float(lx),float(ly),float(lz))
        self.ls[i] = (float(lsx),float(lsy),float(lsz))
        self.rh[i] = (float(rsx),float(rsy),float(rsz))


def main():
    if not len(sys.argv) >= 2:
        print "Usage: rebroadcast_recording.py [ip:port [ip:port ...]] recording_filename"
        sys.exit(2)
    else:
        video_flags = OPENGL|DOUBLEBUF
    
        pygame.init()
        pygame.display.set_caption("Kinect handtracker demo (#pmrhack)")
        # setup targets
        pygame.display.set_mode((640,480), video_flags)

        resize((640,480))
        init()

        frames = 0
        ticks = pygame.time.get_ticks()

        l = list(sys.argv)
        prog = l.pop(0)
        state = UserState()
        filename = l.pop()
        for entry in l:
            m = ip_p.match(entry)
            if m != None:
                d = m.groups()
                endpoints.append((d[0], d[1]))
        print "Rebroadcasting '%s' to the following endpoints:" % filename
        for ep in endpoints:
            print "-- %s, port %s" % (ep[0], ep[1])
            targets.append(liblo.Address(ep[0], ep[1]))
        with open(filename, "r") as inp:
            line = inp.readline()
            while (line):
                event = pygame.event.poll()
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    break
        
                draw(state)
                pygame.display.flip()
        
                frames = frames+1

                i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz = line.split(",")
                state.update(i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz)
                for target in targets:
                    liblo.send(target, "/combined", i, rx, ry, rz, lx, ly, lz, rsx, rsy, rsz, lsx, lsy, lsz)
                    print "User:%s - Hands r(%s,%s,%s), l(%s,%s,%s)" % (i, rx, ry, rz, lx, ly, lz)
                    print "User:%s - Shoulders r(%s,%s,%s), l(%s,%s,%s)" % (i, rx, ry, rz, lx, ly, lz)
                line = inp.readline()
        print "End of recording"

        print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))


if __name__ == '__main__': main()

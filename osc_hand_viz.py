#!/usr/bin/env python

from read_data import OSCServer

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *

import liblo

endpoints = [('localhost', 7111)]

server = OSCServer(7110)
rquad = 0.0
rq_diff = 0.15

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
        

def main():
    video_flags = OPENGL|DOUBLEBUF
    #target = liblo.Address(7111)
    
    pygame.init()
    pygame.display.set_caption("Kinect handtracker demo (#pmrhack)")
    # setup targets
    targets = []
    for ep in endpoints:
        targets.append(liblo.Address(ep[0], ep[1]))
    pygame.display.set_mode((640,480), video_flags)

    resize((640,480))
    init()

    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        
        draw(server)
        pygame.display.flip()
        server.recv(100)
        for player in (x for x in server.lh.keys() if server.lh[x][0] > -10.0):
            # Only send real data
            for target in targets:
                liblo.send(target, "/hands", player, *(server.rh[player] + server.lh[player]))
                liblo.send(target, "/shoulders", player, *(server.rs[player] + server.ls[player]))
                liblo.send(target, "/combined", player, *(server.rh[player] + server.lh[player]+server.rs[player] + server.ls[player]))
        
        frames = frames+1

    print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))


if __name__ == '__main__': main()

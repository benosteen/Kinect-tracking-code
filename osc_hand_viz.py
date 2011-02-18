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

class CommandState(object):
    def __init__(self):
        self.state = {}

    def update(self, i, command, state):
        if not self.state.has_key(i):
            self.state[i] = {}
        if not self.state[i].has_key(command):
            self.state[i][command] = False
        if self.state[i][command] != state:
            self.state[i][command] = state
            return True
        else:
            return False

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


def draw(server, c):
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
        if c.state.has_key(player) and True in c.state[player].values():
            emphasis_point(*server.rh[player], colour=(1.0,0.0,0.0), size=0.05)
            emphasis_point(*server.lh[player], colour=(0.0,0.0,1.0), size=0.05)
        else:
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

    c = CommandState()
    ythreshold = 0.2
    zthreshold = 0.4
    rotate_threshold = 0.5
    side_threshold = 0.5

    arms_out_threshold = 0.3

    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        commands = []
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if event.type == KEYDOWN and event.key == K_t:
            commands.append('takeoff')
        if event.type == KEYDOWN and event.key == K_l:
            commands.append('landing')
        for target in targets:
            for command in commands: 
                print commands
                liblo.send(target, "/command", command)
        
        draw(server, c)
        pygame.display.flip()
        server.recv(100)
        for player in (x for x in server.lh.keys() if server.lh[x][0] > -10.0):
            # Only send real data
            rh = server.rh[player]
            lh = server.lh[player]
            ls = server.ls[player]
            rs = server.rs[player]
            dx = (rs[0]+ls[0]) - (rh[0]+lh[0])
            dy = (rs[1]+ls[1]) - (rh[1]+lh[1])
            dz = (rs[2]+ls[2]) - (rh[2]+lh[2]) - 0.1 # fudge
            dh = abs(rh[0]-lh[0]) + abs(rh[1]-lh[1]) + abs(rh[2]-lh[2])
            dr = rh[2]-lh[2]
            dside = rh[1]-lh[1]

            if abs(dy) > ythreshold and dh > arms_out_threshold:
                if dy<0:
                    if c.update(player, 'u', True):
                        commands.append('u')
                else:
                    if c.update(player, 'd', True):
                        commands.append('d')
            else:
                if c.update(player, 'u', False):
                    commands.append('nu')
                if c.update(player, 'd', False):
                    commands.append('nd')
            
           
            if abs(dr) > rotate_threshold and dh > arms_out_threshold:
                if dr<0:
                    if c.update(player, 'rl', True):
                        commands.append('rl')
                else:
                    if c.update(player, 'rr', True):
                        commands.append('rr')
            else:
                if c.update(player, 'rl', False):
                    commands.append('nrl')
                if c.update(player, 'rr', False):
                    commands.append('nrr')

            if abs(dside) > side_threshold and dh > arms_out_threshold:
                if dside<0:
                    if c.update(player, 'yl', True):
                        commands.append('yl')
                else:
                    if c.update(player, 'yr', True):
                        commands.append('yr')
            else:
                if c.update(player, 'yl', False):
                    commands.append('nyl')
                if c.update(player, 'yr', False):
                    commands.append('nyr')
            
            
            if abs(dz) > zthreshold and dh > arms_out_threshold:
                if dz<0:
                    if c.update(player, 'b', True):
                        commands.append('b')
                else:
                    if c.update(player, 'f', True):
                        commands.append('f')
            else:
                if c.update(player, 'f', False):
                    commands.append('nf')
                if c.update(player, 'b', False):
                    commands.append('nb')
            

            if commands:
                print "Commands to be sent: %s" % commands
            for target in targets:
                liblo.send(target, "/hands", player, *(server.rh[player] + server.lh[player]))
                liblo.send(target, "/shoulders", player, *(server.rs[player] + server.ls[player]))
                liblo.send(target, "/combined", player, *(server.rh[player] + server.lh[player]+server.rs[player] + server.ls[player]))
                liblo.send(target, "/differentials", dy, dz, dh, dr, dside)
                for command in commands: 
                    print commands
                    liblo.send(target, "/command", command)
                commands = []

        frames = frames+1

    print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))


if __name__ == '__main__': main()

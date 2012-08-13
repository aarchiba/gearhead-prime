#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2012 Anne Archibald <peridot.faceted@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
# 

import os

import pygame
from pygame import Rect
from pygame.locals import *  #<- is this a good idea?

import util
import ui
import game
import gamemap
import sdlmap
import command
import action
import image

import random

class Layer(object):
    def handle(self, event):
        return False

def render_text(font, text, width):
    imgs = [ font.render(l, True, (255,255,255)) for l in text.split("\n")]
    h = sum(i.get_height() for i in imgs)
    s = pygame.surface.Surface((width,h))
    o = 0
    for i in imgs:
        s.blit(i,(0,o))
        o += i.get_height()        
    return s

class HUDLayer(Layer):
    def __init__(self, gameboard, ui):
        self.gameboard = gameboard
        self.ui = ui
        self.w = 600
        self.h = 100
        self.font =  pygame.font.Font(None, 24)

    def draw(self, screen):
        w, h = screen.get_size()
        r = Rect((w-self.w)//2, h-self.h, self.w, self.h)
        screen.fill((0,0,0), r)
        o = 0
        for m in reversed(self.gameboard.messages):
            s = render_text(self.font, m, self.w)
            o += s.get_height()
            screen.blit(s, ((w-self.w)//2,h-o))
            if o>self.h:
                break
                
        
class MapLayer(Layer):
    def __init__(self, remembered_map, gamemap, ui):
        self.ui = ui
        self.remembered_map = remembered_map
        self.gamemap = gamemap
        self.sdlmap = sdlmap.SDLMap(remembered_map)
        self.screen = None
    def draw(self, screen):
        self.screen = screen
        self.sdlmap.see(self.gamemap.look(self.ui.gameboard.PC))
        i, j = self.ui.gameboard.PC.coords
        self.sdlmap.view_x = 32*i-32*j
        self.sdlmap.view_y = 16*i+16*j
        self.sdlmap.draw(screen)
    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode == u'[':
                self.ui.command_processor.issue(action.Turn(self.ui.gameboard.PC,False))
                return True
            elif event.unicode == u']':
                self.ui.command_processor.issue(action.Turn(self.ui.gameboard.PC,True))
                return True
            elif event.unicode == u'=':
                self.ui.command_processor.issue(action.Advance(self.ui.gameboard.PC))
                return True
            elif event.key == pygame.K_UP:
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, 7))
                return True
            elif event.key == pygame.K_DOWN:
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, 3))
                return True
            elif event.key == pygame.K_RIGHT:
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, 1))
                return True
            elif event.key == pygame.K_LEFT:
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, 5))
                return True

            #numpad keys:
            kptodelta = {K_KP1:(0,1), K_KP2:(1,1), K_KP3:(1,0), K_KP4:(-1,1),
                    K_KP6:(1,-1), K_KP7:(-1,0), K_KP8:(-1,-1), K_KP9:(0,-1)}
            #(and vi-like keys, just because)
            kptovi = {K_KP1:u'b', K_KP2:u'j', K_KP3:u'n', K_KP4:u'h',
                K_KP6:u'l', K_KP7:u'y', K_KP8:u'k', K_KP9:u'u'}
            vitodelta = dict([ (kptovi[i[0]], i[1]) for i in kptodelta.items() ])
            #FIXME gotta move dis stuff ^ somewhere else
            if event.key in kptodelta.keys():
                direction = gamemap.delta_to_orientation[kptodelta[event.key]]
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, direction))
            elif event.unicode in vitodelta:
                direction = gamemap.delta_to_orientation[vitodelta[event.unicode]]
                self.ui.command_processor.issue(command.TurnAndGo(self.ui.gameboard.PC, direction))

            elif event.unicode in [u'O', u'C']:
                for c in gamemap.neighbors(self.ui.gameboard.PC.coords):
                    for o in self.gamemap.objects[c]:
                        if isinstance(o, gamemap.Door):
                            if o.closed and event.unicode==u'O':
                                self.ui.command_processor.issue(
                                    action.OpenDoor(self.ui.gameboard.PC, o, c))  #FIXME getting hold of the PC and such is getting very verbose...
                                return True
                            elif not o.closed and event.unicode==u'C':
                                self.ui.command_processor.issue(
                                    action.CloseDoor(self.ui.gameboard.PC, o, c))
                                return True
                #FIXME: this will interact with a random appropriate if there is more than one. choice should be given
                self.ui.gameboard.post_message("No suitable doors found")

                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = self.sdlmap.map_coords(event.pos, self.screen)
            self.ui.gameboard.post_message("Going to (%d,%d)" % click_pos)
            self.ui.click(click_pos)
        
        return False


class SDLUI(ui.UI):
    def __init__(self):
        ui.UI.__init__(self)

        pygame.init()
        self.screen = None
        self.set_size((800,600))
        self.frame_clock = pygame.time.Clock()
        self.layers = []
    
    def new_game(self):
        gb = game.Gameboard()
        gb.gamemap = gamemap.load_ascii_map(util.data_dir("testmap2.txt"))
        gb.PC = game.PC()
        gb.PC.coords = (10,5)
        gb.PC.map = gb.gamemap
        gb.gamemap.objects[gb.PC.coords].append(gb.PC)
        m = game.Monster("rat", image.character_sprites("monster_rat.png"), 
            map=gb.gamemap, coords=(1,1))
        gb.gamemap.objects[m.coords].append(m)
        gb.active_NPCs.append(m)
        ui.UI.new_game(self, gb)
        
        self.layers = [MapLayer(gamemap.Map(gb.gamemap.size), gb.gamemap, self), HUDLayer(gb,self)]
        
    def event_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self.set_size(event.size)
                else:
                    for l in reversed(self.layers):
                        if l.handle(event):
                            break
            self.act()
            self.draw()
            pygame.display.flip()
            self.frame_clock.tick(30)
    def set_size(self, size):
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)        
    def draw(self):
        self.screen.fill((64,64,64))
        for l in self.layers:
            l.draw(self.screen)



if __name__=='__main__':
    S = SDLUI()
    S.new_game()
    S.event_loop()

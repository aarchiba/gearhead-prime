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

import ui
import game
import gamemap
import sdlmap
import command
import action

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
                self.ui.command_processor.issue(command.ActionSequence([action.Turn(False)]))
                return True
            elif event.unicode == u']':
                self.ui.command_processor.issue(command.ActionSequence([action.Turn(True)]))
                return True
            elif event.unicode == u'=':
                self.ui.command_processor.issue(command.ActionSequence([action.Advance()]))
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
        gb.gamemap = gamemap.load_ascii_map(os.path.join(os.path.dirname(__file__),"data/testmap2.txt"))
        gb.PC = game.PC()
        gb.PC.coords = (10,5)
        gb.gamemap.movable_objects.append(gb.PC)
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

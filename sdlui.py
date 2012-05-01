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

import pygame

import ui
import game
import map
import sdlmap
import command

class Layer(object):
    def handle(self, event):
        return False
    
class MapLayer(Layer):
    def __init__(self, map, ui):
        self.ui = ui
        self.map = map
        self.sdlmap = sdlmap.SDLMap(map)
    def draw(self, screen):
        self.sdlmap.draw(screen)
    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode == u'[':
                self.ui.command_processor.issue(command.ActionSequence([command.Turn(False)]))
                return True
            if event.unicode == u']':
                self.ui.command_processor.issue(command.ActionSequence([command.Turn(True)]))
                return True
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
        gb.map = map.load_ascii_map("data/testmap1.txt")
        gb.PC = game.PC()
        gb.PC.coords = (10,5)
        gb.map.movable_objects.append(gb.PC)
        ui.UI.new_game(self, gb)
        
        self.layers = [MapLayer(gb.map, self)]
        
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

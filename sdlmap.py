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

import collections

import pygame
from pygame import Rect

import gamemap
import image
import terrain


class SDLMap(object):
    """Graphical representation of a particular map
    
    This takes care of drawing the map to the screen.
    
    The coordinate system puts the center of the (0,0) tile at
    position (0,0) in the map viewer's space. The center of the
    (1,0) tile is at (32,16), while the center of the (0,1) tile
    is at (-32,16). This means that the x axis runs down and to
    the right, while the y axis runs down and to the left.
    
    The image displayed on screen is centered on the point
    (self.view_x, self.view_y) in viewer space.

    """
    def __init__(self, map_to_draw):
        self.view_x = 0
        self.view_y = 0
        self.map_to_draw = map_to_draw
        self.mouse_cursor = image.get("target64.png", None, (0,0,64,64))
    
    def draw(self, screen, work_rects=None):
        """Draw the map to the screen"""
        if work_rects is None:
            work_rects = [Rect(0,0,screen.get_width(),screen.get_height())]
        extra_things = collections.defaultdict(list)
        for (k,v) in self.map_to_draw.objects.items():
            extra_things[k].extend(v)
        extra_things[self.map_coords(pygame.mouse.get_pos(), screen)].append(self.mouse_cursor)
        for i in range(self.map_to_draw.w):
            for j in range(self.map_to_draw.h):
                view_x =  32*i-32*j
                view_y =  16*i+16*j
                x, y = view_x - self.view_x + screen.get_width()//2, view_y-self.view_y + screen.get_height()//2
                t = self.map_to_draw.terrain((i,j))
                s = t.sprite()
                s_pos = Rect(x-32,y+16-s.get_height(),s.get_width(),s.get_height())
                if s_pos.collidelist(work_rects)>=0:
                    screen.blit(s, s_pos)
                    if (i,j) in extra_things:
                        for t in extra_things[(i,j)]:
                            if isinstance(t, pygame.Surface):
                                s = t
                            else:
                                s = t.sprite()
                            screen.blit(s,(x-32,y+16-s.get_height()))
    def map_coords(self, xy, screen):
        x, y = xy
        x, y = x + self.view_x-screen.get_width()//2, y + self.view_y-screen.get_height()//2
        i = (x+2*y+32)//64
        j = (2*y-x+32)//64
        return (i,j)
    def see(self, things):
        for coords, obj in things:
            if isinstance(obj, terrain.Terrain):
                self.map_to_draw.set_terrain(coords, obj)
                del self.map_to_draw.objects[coords][:]
        for coords, obj in things:
            if not isinstance(obj, terrain.Terrain):
                self.map_to_draw.objects[coords].append(obj)

if __name__ == '__main__':
    import sys
    
    pygame.init()
    size = width, height = 800,  600
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    M = gamemap.load_ascii_map("data/testmap2.txt")
    S = SDLMap(M,M)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    S.view_y -= 16
                elif event.key == pygame.K_DOWN:
                    S.view_y += 16
                elif event.key == pygame.K_LEFT:
                    S.view_x -= 16
                elif event.key == pygame.K_RIGHT:
                    S.view_x += 16
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
        screen.fill((64,64,64))
        S.draw(screen)
        pygame.display.flip()
        clock.tick(30)


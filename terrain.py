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

import yaml

import image

class Terrain(yaml.YAMLObject):
    yaml_tag = "!Terrain"
    
    def __init__(self, name, roguechar, sprite, 
                 passable=True, opaque=False, description=None):
        self.name = name
        self.roguechar = roguechar
        self.sprite = sprite
        self.passable = passable
        self.opaque = opaque
        self.description = description
        
void = Terrain("void", " ", image.Image("big_terrain.png", None, (576,0,64,96)), passable=False)
floor = Terrain("floor", ".", image.Image("big_terrain.png", None, (576,96,64,96)))
wall = Terrain("wall", "#", image.Image("big_terrain.png", None, (448,288,64,96)), passable=False, opaque=True)

if __name__=='__main__':
    pass

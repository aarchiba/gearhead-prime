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

import random

import yaml
import image
import action

class Character(yaml.YAMLObject):
    yaml_tag = "!Character"    
    def __init__(self, name, sprites, map=None, orientation=0, coords=(0,0)):
        self.name = name
        self.sprites = sprites
        self.orientation = orientation
        self.map = map
        self.coords = coords
        self.opaque = False
        self.passable = False
    @property
    def sprite(self):
        return self.sprites[self.orientation]

class PC(Character):
    def __init__(self):
        self.colors = image.random_color_scheme("personal")
        Character.__init__(self, "you", image.character_sprites("cha_f_mechanic.png",self.colors))

class Monster(Character):
    def __init__(self, name, sprites, map=None, orientation=0, coords=(0,0), description=None):
        Character.__init__(self, name, sprites, map=map, orientation=orientation, coords=coords)
        self.description = description
    def act(self):
        return random.choice([action.Advance(self), action.Turn(self,1), action.Turn(self,0)])
    
class Gameboard(yaml.YAMLObject):
    yaml_tag = "!Gameboard"
    
    def __init__(self):
        self.gamemap = None
        self.PC = None
        self.messages = ["New game"]
        self.ui = None
        self.active_NPCs = []
    
    def post_message(self, message):
        self.messages.append(message)
        self.ui.post_message(message)

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['ui']
        return d
    def __setstate__(self,d):
        self.__dict__ = d
        self.ui = None

if __name__=='__main__':
    pass

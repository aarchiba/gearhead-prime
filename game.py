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

class Character(yaml.YAMLObject):
    yaml_tag = "!Character"    
    def __init__(self, sprites, orientation=0):
        self.sprites = sprites
        self.orientation = orientation
    @property
    def sprite(self):
        return self.sprites[self.orientation]

class PC(Character):
    def __init__(self):
        self.colors = image.random_color_scheme("personal")
        Character.__init__(self, 
            [image.Image("cha_f_mechanic.png", self.colors, (64*(i%4), 64*(i//4), 64, 64)) for i in range(8)])
        self.map = None
        self.coords = (0,0)


class Gameboard(yaml.YAMLObject):
    yaml_tag = "!Gameboard"
    
    def __init__(self):
        self.gamemap = None
        self.PC = None
        self.messages = ["New game"]
        self.ui = None
    
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

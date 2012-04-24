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

import numpy as np

class Map(object):
    def __init__(self, size):
        self.size = size
        self.w, self.h = self.size
        self.map = np.zeros(self.size, np.uint8)
        self.seen = np.zeros(self.size, np.uint8)
        self.terrain_types = [" "]
        self.terrain_types_reverse = { self.terrain_types[0]: 0 }

    def add_terrain_type(self, t):
        self.terrain_types.append(t)
        self.terrain_types_reverse[t] = len(self.terrain_types)-1
        if len(self.terrain_types) == 256:
            self.map = self.map.astype(np.uint16)
        elif len(self.terrain_types) == 65536:
            self.map = self.map.astype(np.uint32)
                
    def terrain(self, xy):
        return self.terrain_types[self.map[xy]]
        
    def set_terrain(self, xy, t):
        if t not in self.terrain_types_reverse:
            self.add_terrain_type(t)
        self.map[xy] = self.terrain_types_reverse[t]
    
    def __str__(self):
        return ("Map {0} by {1}:\n".format(self.w, self.h) + 
            "\n".join("".join(self.terrain_types[v] for v in l) 
                        for l in self.map.T))

def load_ascii_map(f):
    a = open(f,"rt").readlines()
    for i, l in enumerate(a):
        if l[-1] == "\n":
            a[i] = l[:-1]
    if not a[-1]:
        a = a[:-1]
    w = max(len(l) for l in a)
    a = [l+" "*(w-len(l)) for l in a]
    M = Map((w,len(a)))
    for j, l in enumerate(a):
        for i, c in enumerate(l):
            M.set_terrain((i,j),c)
    return M

if __name__ == '__main__':
    print load_ascii_map("data/testmap1.txt")

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

import unicodedata
import collections
import heapq

import numpy as np
import random

import util
import yaml
import fov
import terrain
import image

def unicode_usable(c):
    if c in '\\ \t':
        return False
    if not unicodedata.category(c) in [
            'Ll', 'Lt', 'Lu', 'Me', 'Nd', 'Nl', 'No', 
            'Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps',
            'Sc', 'Sm']:
        return False
    return True
usable_unicode_chars = [unichr(i) for i in range(65536) if unicode_usable(unichr(i))]


class Map(yaml.YAMLObject):
    yaml_tag = "!Map"
    
    def __init__(self, size):
        self.size = size
        self.w, self.h = self.size
        self.terrain_array = np.zeros(self.size, np.uint8)
        self.seen = np.zeros(self.size, np.uint8)
        self.terrain_types = [terrain.void]
        self.terrain_types_reverse = { self.terrain_types[0]: 0 }
        self.objects = collections.defaultdict(list)

    def add_terrain_type(self, t):
        self.terrain_types.append(t)
        self.terrain_types_reverse[t] = len(self.terrain_types)-1
        if len(self.terrain_types) == 256:
            self.terrain_array = self.terrain_array.astype(np.uint16)
        elif len(self.terrain_types) == 65536:
            self.terrain_array = self.terrain_array.astype(np.uint32)
                
    def terrain(self, xy):
        return self.terrain_types[self.terrain_array[xy]]
        
    def set_terrain(self, xy, t):
        if t not in self.terrain_types_reverse:
            self.add_terrain_type(t)
        self.terrain_array[xy] = self.terrain_types_reverse[t]
    
    def __str__(self):
        return ("Map {0} by {1}:\n".format(self.w, self.h) + 
            "\n".join("".join(self.terrain_types[v].roguechar for v in l) 
                        for l in self.terrain_array.T))
    def __getstate__(self):
        d = self.__dict__.copy()
        del d['terrain_array']
        del d['terrain_types_reverse']
        del d['terrain_types']
        del d['size']
        del d['w']
        del d['h']
        del d['objects']
        cells = np.zeros_like(self.terrain_array)
        cell_types = { (self.terrain_types[0], ()): 0 }
        cell_chars = [' ']
        n_cell_types = 1
        unicode_used = 0
        for i in range(self.w):
            for j in range(self.h):
                terrain_ = self.terrain_types[self.terrain_array[i,j]]
                contents = tuple(self.objects[i,j])
                if (terrain_,contents) not in cell_types:
                    cell_types[terrain_,contents] = n_cell_types
                    n_cell_types += 1
                    # choose a Unicode character
                    # FIXME: try all contents then the terrain hoping
                    # for an unused character
                    if contents:
                        ch = contents[-1].roguechar
                    else:
                        ch = terrain_.roguechar
                    while ch in cell_chars:
                        ch = unicode_usable[unicode_used]
                        unicode_used += 1
                    cell_chars.append(ch)
                cells[i,j] = cell_types[terrain_,contents]

        d['map'] = '\n'.join("".join(cell_chars[cells[i,j]] for i in range(self.w)) for j in range(self.h))+"\n"
        if np.any(self.seen):
            d['seen'] = '\n'.join("".join('*' if self.seen[i,j] else '.' for i in range(self.w)) for j in range(self.h))+"\n"
        else:
            del d['seen']
        d['cell_types'] = {}
        for (k,v) in cell_types.items():
            terrain_, contents = k
            d['cell_types'][cell_chars[v]] = [terrain_]+list(contents)
        return d
    def __setstate__(self, d):
        cell_types = d.pop('cell_types')
        cell_map = d.pop('map')
        seen = d.pop('seen',None)

        self.__dict__ = d
        
        self.h = len(cell_map.split("\n"))
        self.w = 0
        for l in cell_map.split("\n"):
            self.w = max(len(l),self.w)
 
        self.size = (self.w, self.h)
        self.terrain_array = np.zeros(self.size, np.uint8)
        self.seen = np.zeros(self.size, np.uint8)
        if seen is not None:
            for j,l in enumerate(seen.split("\n")):
                for i,c in enumerate(l):
                    if c!='.':
                        self.seen[i,j] = 1
        self.terrain_types = [terrain.void]
        self.terrain_types_reverse = { self.terrain_types[0]: 0 }
        self.objects = collections.defaultdict(list)
        for j,l in enumerate(cell_map.split("\n")):
            for i,c in enumerate(l):
                tc = cell_types[c]
                terrain_ = tc[0]
                contents = tc[1:]
                self.set_terrain((i,j),terrain_)
                self.objects[i,j].extend(contents)

    def is_opaque(self, ij):
        i,j = ij
        if self.terrain((i,j)).opaque:
            return True
        else:
            for o in self.objects[i,j]:
                if o.opaque:
                    return True
        return False
    def is_passable(self, ij):
        i,j = ij
        if not self.terrain((i,j)).passable:
            return False
        else:
            for o in self.objects[i,j]:
                if hasattr(o,'passable') and not o.passable:
                    return False
        return True
    def look(self, char):
        """List everything the character can see from its current position"""
        r = []
        def see(x,y):
            r.append(((x,y), self.terrain((x,y))))
            for m in self.objects[(x,y)]:
                r.append(((x,y),m))
        fov.fieldOfView(char.coords[0], char.coords[1], self.w, self.h, self.w+self.h,
            see, lambda x,y: self.is_opaque((x,y)))
        return r
    def lsobjects(self, filterfunc=None):
        """Return a set of all objects on the map, optionally filtered."""
        #TODO? optionally only return objects inside a certain rect of coords
        ls = set()
        #[[ls.update(set(matches)) for matches in filter(filterfunc, tile_contents)]
         #   for tile_contents in self.objects.values()]
        for tile_contents in self.objects.values():
            for obj in tile_contents:
                if not filterfunc:
                    ls.add(obj)
                elif filterfunc(obj):
                    ls.add(obj)
        return ls

class Feature(yaml.YAMLObject):
    yaml_tag = "!Feature"
    
    def __init__(self, name, roguechar, sdl_image_spec, 
                 passable=True, opaque=False, description=None):
        self.name = name
        self.roguechar = roguechar
        self.sdl_image_spec = sdl_image_spec
        self.description = description
        self._passable = passable
        self._opaque = opaque
        self._sprite = None

    @property
    def sprite(self):
        if self._sprite is None:
            self._sprite = image.get(*self.sdl_image_spec)
        return self._sprite

    @property
    def passable(self):
        return self._passable
    @property
    def opaque(self):
        return self._opaque
        
    def __getstate__(self):
        d = self.__dict__.copy()
        del d['_sprite']
        return d
    def __setstate__(self,d):
        self.__dict__ = d
        self._sprite = None

#some default thinwalls
twfile = "SharkD_Wall_FlatTechy_b_sheet_a.png"
twls = {}
colors = image.random_color_scheme('mecha')
#ThinWall, Corner: Right and Down
twls[u'┌'] = Feature("tw-crd", u"┌", (twfile, colors, (0,288,64,96)), False, True)
twls[u'┐'] = Feature("tw-cld", u"┐", (twfile, colors, (64,192,64,96)), False, True)
twls[u'└'] = Feature("tw-cru", u"└", (twfile, colors, (64*2,96,64,96)), False, True)
twls[u'┘'] = Feature("tw-clu", u"┘", (twfile, colors, (64*3,0,64,96)), False, True)
twls[u'─'] = Feature("tw-h",   u"─", (twfile, colors, (64,96,64,96)), False, True)
twls[u'│'] = Feature("tw-v",   u"│", (twfile, colors, (64*2,96*2,64,96)), False, True)
twls[u'┬'] = Feature("tw-jd",  u"┬", (twfile, colors, (64, 96*3, 64,96)), False, True)
twls[u'┴'] = Feature("tw-ju",  u"┴", (twfile, colors, (64*3, 96, 64,96)), False, True)
twls[u'├'] = Feature("tw-jr",  u"├", (twfile, colors, (64*2, 96*3, 64,96)), False, True)
twls[u'┤'] = Feature("tw-jl",  u"┤", (twfile, colors, (64*3, 96*2, 64,96)), False, True)
twls[u'┼'] = Feature("tw-jx",  u"┼", (twfile, colors, (64*3, 96*3, 64,96)), False, True)


def load_ascii_map(f):
    a = [line.decode('UTF-8') for line in open(f,"rt").readlines()]
    #FIXME? detect file encoding automatically
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
            obj = []
            if c=="#":
                c = terrain.wall
            elif c==".":
                c = terrain.floor

            elif c in twls:
                obj = [twls[c]]
                c = terrain.floor

            elif c=='+':
                c = terrain.floor
                obj = [Door( (i,j), closed = bool(random.getrandbits(1)) )]

            else:
                c = terrain.void
            M.set_terrain((i,j),c)
            M.objects[i,j].extend(obj)
    return M



orientation_to_delta = [(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1)]
delta_to_orientation = dict([(o, i) for (i,o) in enumerate(orientation_to_delta)])

# FIXME: wrong if more than one step away
# possible solution: normalize the vector and then round
# its coordinates to the closest integer
def find_orientation(from_, to):
    x1, y1 = from_
    x2, y2 = to
    return delta_to_orientation[x2-x1,y2-y1]


def adjacent(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (not pos1==pos2) and abs(x1-x2)<=1 and abs(y1-y2)<=1


#another attempt at doors:
class Door(Feature):
    def __init__(self, coords, colors=None, closed=True):
        Feature.__init__(self, 'door', '+', None, description="Door")
        del self._passable, self._opaque, self._sprite

        self.coords = (coords[0], coords[1])
        if colors is None:
            colors = image.random_color_scheme('mecha')
        self.colors = colors
        self.closed = closed
        
    @property
    def sprite(self):
        x = 0 #TODO: door orientation
        y = 0
        if not self.closed: y = 96
        return image.get("door_a.png", self.colors, (x,y,64,96))

    @property
    def passable(self):
        return not self.closed
    @property
    def opaque(self):
        return self.closed

    def __getstate__(self):
        d = self.__dict__.copy()
        return d
    def __setstate__(self, d):
        self.__dict__ = d






class NoPathException(ValueError):
    def __init__(self, best_effort=None):
        ValueError.__init__(self, "Path not found")
        self.best_effort=best_effort

root2 = np.sqrt(2)
def find_path(x1y1,x2y2,passable):

    def dist(x1y1, x2y2):
        x1,y1 = x1y1
        x2,y2 = x2y2
        return np.hypot(x1-x2,y1-y2)

    path_to = {x1y1: ((x1y1,),0)}
    costs = [(dist(x1y1,x2y2), x1y1)]

    closest = np.inf, None

    while costs:
        d, node = heapq.heappop(costs)
        if node == x2y2:
            return path_to[x2y2]

        dd = dist(node,x2y2)
        if dd < closest[0]:
            closest = dd, node

        path_so_far, l_so_far = path_to[node]

        nx, ny = node
        #FIXME: random.sample here doesn't seem to make pathfinding moar random
        for i in random.sample((-1,0,1), 3):
            for j in random.sample((-1,0,1), 3):
                nbx, nby = nx+i, ny+j
                if not passable(nbx,nby):
                    continue
                l = l_so_far + np.hypot(i,j)
                if (nbx,nby) in path_to:
                    pp, ll = path_to[nbx,nby]
                    if ll<=l:
                        continue
                    # new shortest path to this node
                    # so remove it from the queue (if it's there)
                    # and fall through to the "new node" code
                    costs = [(d,n) for (d,n) in costs if n!=(nbx,nby)]
                # this is the shortest known path to (nbx,nby)
                path_to[nbx,nby] = path_so_far + ((nbx,nby),), l

                # How promising is it?
                cost = l+dist((nbx,nby),x1y1)

                heapq.heappush(costs, (cost,(nbx,nby)))

    raise NoPathException(path_to[closest[1]])



if __name__ == '__main__':
    M = load_ascii_map(util.data_dir("testmap2.txt"))
    f = open(util.data_dir("testmap2.yaml"),"w")
    yaml.dump(M,f, encoding="UTF8", allow_unicode=True)
    f.close()
    f = open(util.data_dir("testmap2.yaml,roundtrip"),"w")
    yaml.dump(yaml.load(yaml.dump(M)),f, encoding="UTF8", allow_unicode=True)
    f.close()

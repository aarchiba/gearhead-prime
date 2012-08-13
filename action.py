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

import gamemap

class ActionFailure(Exception):
	"""Action.__call__ can raise this whenever the action fails for
	any reason."""
	pass

class Action(object):
    """An action is a request for the game to do something atomic.
    
    This may be "turn left", "swing my sword at this monster", or
    "try picking this lock". It takes a certain amount of time and/or
    resources, and it cannot be interrupted.
    
    Often actions are too fine-grained for convenient use by the player,
    who instead issues higher-level commands, which yield a sequence
    of actions. That said, every change the user makes in the game
    world passes through actions; they handle making sure that (for
    example) things that are supposed to take time, do take time.
    """
    def __init__(self, char):
        self.char = char
    def __call__(self, gameboard):
        raise NotImplemented

class Turn(Action):
    def __init__(self, char, right): #FIXME: does 'right' mean clockwise?
        Action.__init__(self, char)
        self.right = right
    def __call__(self, gameboard):
        if self.right:
            self.char.orientation += 1
        else:
            self.char.orientation -= 1
        self.char.orientation %= 8

class Advance(Action):
    def __call__(self, gameboard):
        x, y = self.char.coords
        delta_x, delta_y = gamemap.orientation_to_delta[self.char.orientation]
        to_x, to_y = x+delta_x, y+delta_y
        if self.char.map.is_passable((to_x,to_y)):
            self.char.map.objects[self.char.coords].remove(self.char)
            self.char.coords = to_x, to_y
            self.char.map.objects[self.char.coords].append(self.char)
        else:
            blocker = "unknown object"
            if not self.char.map.terrain((to_x,to_y)).passable:
                blocker = self.char.map.terrain((to_x,to_y)).name
            else:
                for o in self.char.map.objects[to_x,to_y]:
                    if not o.passable:
                        blocker = o.name
                        break
            raise ActionFailure("Cannot advance into (%i,%i): blocked by %s"
                % (to_x, to_y, blocker))

class OpenDoor(Action):
    def __init__(self, char, door, coords):
        Action.__init__(self, char)
        self.door = door
        self.coords = coords
        # FIXME: check door is actually at coords
    def __call__(self, gameboard):
        if not gamemap.adjacent(self.char.coords, self.coords):
            raise ActionFailure("Not adjacent to door")
        if self.door.locked:
            raise ActionFailure("Door is locked")
        if self.door.closed:
            self.door.closed = False
        else:
            raise ActionFailure("Door is already open")

class CloseDoor(Action):
    def __init__(self, char, door, coords):
        Action.__init__(self, char)
        self.door = door
        self.coords = coords
        # FIXME: check door is actually at coords
    def __call__(self, gameboard):
        if not gamemap.adjacent(self.char.coords, self.coords):
            raise ActionFailure("Not adjacent to door")
        if not self.door.closed:
            self.door.closed = True
        else:
            raise ActionFailure("Door is already closed")


if __name__=='__main__':
    pass

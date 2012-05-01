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

class Action(object):
    """An action is a request for the game to do something atomic.
    
    This may be "turn left", "swing my sword at this monster", or
    "try picking this lock". It takes a certain amount of time and/or
    resources, and it cannot be interrupted.
    
    Often actions are too fine-grained for convenient use by the player,
    who instead issues higher-level commands, which yield a sequence
    of actions. 
    """
    def __call__(self, gameboard):
        raise NotImplemented

class Turn(Action):
    def __init__(self, right):
        self.right = right
    def __call__(self, gameboard):
        if self.right:
            gameboard.PC.orientation += 1
        else:
            gameboard.PC.orientation -= 1
        gameboard.PC.orientation %= 8
        
class Command(object):
    """A command is something the player asks the game to do.
    
    This may be "go to (x,y)", "repair this object" or simply "walk
    forward". This may involve multiple actions, and may need to be
    interrupted (say if the player rounds a corner and notices 
    a monster).
    """
    pass
    
def command_wrapper(gen):
    class Generator(Command):
        def __init__(self, *args, **kwargs):
            self.gen = gen(*args, **kwargs)
        
        def next(self):
            return self.gen.next()
    return Generator
    
@command_wrapper
def ActionSequence(al):
    for a in al:
        yield a
                

class CommandProcessor(object):
    def __init__(self):
        self.command_queue = collections.deque()
        
    def issue(self, command):
        self.command_queue.append(command)
        
    def next(self):
        while self.command_queue:
            try:
                return self.command_queue[0].next()
            except StopIteration:
                self.command_queue.popleft()
        raise StopIteration
    
    def interrupt(self):
        self.command_queue = collections.deque()


if __name__=='__main__':
    pass

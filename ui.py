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
import heapq

import yaml
import command
from action import ActionFailure

class UI(object):
    def __init__(self):
        self.logfile = open('messages.txt','wt')
        self.command_processor = command.CommandProcessor()
        self.gameboard = None
        self.save_name = "ghsave.yaml"
        
    def new_game(self, gameboard):
        self.gameboard = gameboard
        gameboard.ui = self
        heapq.heappush(self.gameboard.next_actor,(0,self.gameboard.PC))
        for n in self.gameboard.active_NPCs:
            heapq.heappush(self.gameboard.next_actor, (0,n))
                
    def load_game(self):
        self.gameboard = yaml.load(open(self.save_name, 'rt'))
        gameboard.ui = self        
    def save_game(self):
        yaml.dump(self.gameboard, open(self.save_name, 'wt'))
    
    def act(self):
        """Make one action happen
        
        Whoever's turn it is to move next gets to execute one action.
        This action takes time (in an amount returned by the action)
        so they don't get scheduled again until it finishes. If the
        next action is up to the user and they haven't chosen one yet,
        return and don't advance the clock.
        """
        self.gameboard.time, char = heapq.heappop(self.gameboard.next_actor)
        if char is self.gameboard.PC:
            try:
                dt = (self.command_processor.next())(self.gameboard)
                heapq.heappush(self.gameboard.next_actor, (self.gameboard.time+dt, self.gameboard.PC))
            except StopIteration:
                heapq.heappush(self.gameboard.next_actor, (self.gameboard.time, self.gameboard.PC))
                return
            except ActionFailure, e:
                #FIXME: ActionFailure should somehow be communicated back
                #to the command processor
                self.gameboard.post_message("ActionFailure: %s" % str(e))
                #FIXME: failed actions should take time too (specify it in the exception?)
                heapq.heappush(self.gameboard.next_actor, (self.gameboard.time, self.gameboard.PC))
        else:
            a = char.act()
            try:
                dt = a(self.gameboard)
                heapq.heappush(self.gameboard.next_actor, (self.gameboard.time+dt, char))
            except ActionFailure, e:
                self.gameboard.post_message("ActionFailure for %s: %s" % (char.name, str(e)))
                heapq.heappush(self.gameboard.next_actor, (self.gameboard.time, char))
			
        return self.command_processor.command_queue
        
    def post_message(self, message):
        self.logfile.write(message)
        print message
        
    def click(self, coords):
        self.command_processor.issue(command.GoTo(self.gameboard.PC, self.gameboard.gamemap, coords))

    def display_messages(self):
        raise NotImplemented
    def browse_characters(self):
        raise NotImplemented
    def examine(self, item):
        raise NotImplemented

if __name__=='__main__':
    pass

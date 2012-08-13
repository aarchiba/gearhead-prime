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

import action

class MonsterBrain(object):
    def next(self):
        return random.choice([action.Advance(), action.Turn(1), action.Turn(0)])


if __name__=='__main__':
    pass

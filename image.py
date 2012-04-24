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

import os, re, random
import weakref

import pygame
import pygame.surfarray as surfarray # FIXME: fall back gracefully
surfarray.use_arraytype('numpy')
import numpy as np

import lru

# Cache of recolored images: keep them around as long as they're in use
_images = weakref.WeakValueDictionary()
_image_dir = "images"
# Use LRU to make sure the weakref deletion isn't too aggressive
@lru.cache()
def get(name, recoloring = None):
    if (name, recoloring) not in _images:
        if recoloring is None:
            i = pygame.image.load(os.path.join(_image_dir,name))
            # Colorkey has no effect if the image already has alpha
            i.set_colorkey((0,0,255))
            i = i.convert_alpha(pygame.Surface((1,1), pygame.SRCALPHA, 32))
        else:
            i = recolor(get(name),recoloring)
        _images[(name,recoloring)] = i

    return _images[(name,recoloring)]

def recolor(image, mode):
    if mode is None:
        return image
    elif mode[0]=="RYG":
        return recolor_ryg(image, mode[1:])
    else: 
        raise ValueError("Unrecognized recoloring spec {}".format(mode))
        
def recolor_ryg(image, ryg):
    red, yellow, green = (np.asarray(c,np.uint8) for c in ryg)
    # We need to make a copy in this specific format
    image = image.convert_alpha(pygame.Surface((1,1), pygame.SRCALPHA, 32))
    # We can't make a new image from an array, so we're going to
    # jigger this one in place.
    a = surfarray.pixels3d(image)

    yellow_red = (a[...,0] > a[...,1]) & (a[...,2]<=a[...,1])
    yr = a[yellow_red,:]
    c1 = yr[:,2]
    c2 = yr[:,1]-yr[:,2]
    c3 = yr[:,0]-yr[:,1]
    a[yellow_red,:3] = np.minimum(c1[:,None] + 
                                    (c2[:,None]/255.)*yellow[None,:] + 
                                    (c3[:,None]/255.)*red[None,:],
                                   255).astype(np.uint8)
    green_yellow = (a[...,0] <= a[...,1]) & (a[...,2]<=a[...,0])
    gy = a[green_yellow,:]
    c1 = gy[:,2]
    c2 = gy[:,0]-gy[:,2]
    c3 = gy[:,1]-gy[:,0]
    a[green_yellow,:3] = np.minimum(c1[:,None] + 
                                      (c2[:,None]/255.)*yellow[None,:] + 
                                      (c3[:,None]/255.)*green[None,:],
                                     255).astype(np.uint8)

    return image

colors = None
def load_sdl_colors_txt(filename="data/sdl_colors.txt"):
    global colors, personal, mecha

    if colors is not None:
        return
    colors = {}
    personal = [], [], []
    mecha = [], [], []
    color_re = re.compile(r"^([-+]+):([A-Za-z0-9 ]*[A-Za-z0-9]) *< *([0-9]+) +([0-9]+) +([0-9]+) *>")
    f = open(filename,"rt")
    l = f.readline()
    if not l.startswith("% Standard Color List"):
        raise ValueError("%s does not appear to be in the correct format" % filename)

    for c in f.readlines():
        if not c:
            continue
        m = color_re.search(c)
        if not m:
            raise ValueError("Line from %s does not appear to specify a color: %s" % (filename, c))
        name = m.group(2)
        r, g, b = int(m.group(3)), int(m.group(4)), int(m.group(5))
        colors[name] = r, g, b
        flags = m.group(1)
        for i in range(3):
            if flags[i]=="+":
                personal[i].append(name)
            else:
                assert flags[i]=="-"
            if flags[i+3]=="+":
                mecha[i].append(name)
            else:
                assert flags[i+3]=="-"
                
def random_color_scheme(kind=None):
    if colors is None:
        load_sdl_colors_txt()
    if kind is None:
        rs, gs, bs = colors, colors, colors
    elif kind == "mecha":
        rs, gs, bs = mecha
    elif kind == "personal":
        rs, gs, bs = personal
    else:
        r, g, b = kind # pass through
        return r, g, b
    return (colors[random.choice(rs)],
            colors[random.choice(gs)],
            colors[random.choice(bs)])


if __name__ == '__main__':
    import sys

    pygame.init()
    size = width, height = 900, 700
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    
    img1 = get("por_f_ladi_mischa(AC-).png")
    r, y, g = random_color_scheme(kind="personal")
    img2 = get("por_f_ladi_mischa(AC-).png",("RYG",r,y,g))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                r, y, g = random_color_scheme(kind="personal")
                img2 = get("por_f_ladi_mischa(AC-).png",("RYG",r,y,g))
        
        screen.fill((64,64,64))
        screen.blit(img1,(0,0))
        screen.blit(img2,(img1.get_width(),0))
        pygame.display.flip()
        clock.tick(30)


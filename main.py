import numpy as np
import time
import curses
import random

size = (64,32)
clamp = np.ones(size,dtype="uint8")
world = np.zeros(size,dtype="uint8")

# density sorted
# 0: air
# 1-2: water
# 3-4: sand

# ===== Render ======

col_map = [(curses.COLOR_BLACK,curses.COLOR_BLACK),(curses.COLOR_BLUE,curses.COLOR_BLUE)]

def render(scr):
    for y in range(size[1]):
        for x in range(size[0]):
            c = (world[x,size[1]-y-1]+1)//2
            # erase makes this unnecesary
            #if c == 0:
            #    # air hax to get less flickers
            #    scr.addstr("  ",curses.color_pair(1+c))
            #else:
            scr.addstr("██",curses.color_pair(1+c))
        scr.addstr("\n")

def colour_init():
    for k,pair in enumerate(col_map):
        curses.init_pair(k+1,pair[0],pair[1])

# ===== Sim =====

def tick():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            func_map[(world[x,y]-1)//2](x,y)

def tick_water(x,y): 
    # unticked pixel
    if world[x,y] == 1:
        if y == 0:
            # bottom of world
            return
        if world[x,y-1] == 0:
            # empty space
            world[x,y-1] = 2
            world[x,y] = 0
        else:
            # filled space
            direction = random.choice([-1,1])
            nx = x + direction
            if nx >= 0 and nx < size[0]:
                if world[nx,y] == 0:
                    # empty space next to
                    world[nx,y] = 2
                    world[x,y] = 0

def tick_sand(x,y):
    pass


func_map = [tick_water,tick_sand]

def clean():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            if world[x,y] == 0:
                continue
            world[x,y] = ((world[x,y] + 1 ) // 2) * 2 - 1

def world_init():
    for y in range(size[1]):
        for x in range(size[0]):
            world[x,y] = 1 if random.random() < 0.1 else 0

# ===== Control =====

def init():
    colour_init()
    world_init()

def main(scr):
    scr.nodelay(True)
    init()
    while True:
        #scr.clear()
        scr.erase() # magically fixes all the flickering
        tick()
        clean()
        render(scr)
        scr.refresh()
        try:
            key = scr.getkey()
            scr.addstr(key)
        except:
            pass

curses.wrapper(main)

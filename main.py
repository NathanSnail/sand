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
# 5-6: rock
# ===== Render ======

col_map = [
        (600, 600, 1000),
        (0, 200, 1000),
        (1000, 1000, 100),
        (20, 40, 60),
]

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
    do_fps(scr)

magic_cols = {254:(1000,1000,1000)}
magic_pairs = {255:(254,254)}

def colour_init():
    for k,col in enumerate(col_map):
        curses.init_color(k+1,col[0],col[1],col[2])
        curses.init_pair(k+1,k+1,k+1)
    for key in magic_cols.keys():
        value = magic_cols[key]
        curses.init_color(key,value[0],value[1],value[2])
    for key in magic_pairs.keys():
        value = magic_pairs[key]
        curses.init_pair(key, value[0], value[1])

frame_times = [1 for _ in range(15)]
current_frame = 0
last_time = time.time()
def do_fps(scr):
    global last_time, current_frame, frame_times
    current_time = time.time()
    frame_times[current_frame] = current_time - last_time
    last_time = current_time
    current_frame += 1
    current_frame %= 15
    fps = 15 / sum(frame_times)
    scr.addstr(size[1],0,f"FPS: {fps:.0f}",255)

# ===== Sim =====

def tick():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            material = world[x,y]
            if material % 2 == 0:
                continue
            func_map[world[x,y]//2](x,y)

def tick_water(x,y): 
    # unticked pixel
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
        if nx < 0 or nx >= size[0]:
            return
        if world[nx,y] == 0:
            # empty space next to
            world[nx,y] = 2
            world[x,y] = 0

def tick_sand(x,y):
    if y == 0:
        # bottom of world
        return
    below = world[x,y-1]
    if below < 3 and random.random() < 0.8: # chance to move with water
        pass
        # empty space
        world[x,y-1] = 4
        world[x,y] = below
    else:
        # filled space
        direction = random.choice([-1,1])
        nx = x + direction
        if nx < 0 or nx >= size[0]:
            return
        below_side = world[nx,y-1]
        if below_side < 3:
            # empty space next to
            world[nx,y] = 4
            world[x,y] = below_side

def tick_rock(x,y):
    pass # rocks dont do much

func_map = [tick_water, tick_sand, tick_rock]

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
            ty = 0
            if random.random() < 0.1:
                ty = 1
            elif random.random() < 0.1:
                ty = 3
            elif y * 0.1 < random.random():
                ty = 5
            world[x,y] = ty

# ===== Control =====

def init():
    colour_init()
    world_init()

def main(scr):
    if not curses.can_change_color():
        raise Exception("Doesn't support fancy colours")
    scr.nodelay(True)
    init()
    while True:
        #scr.clear()
        scr.erase() # magically fixes all the flickering
        #time.sleep(0.5)
        scr.addstr(str())
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

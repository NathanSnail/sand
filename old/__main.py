import numpy as np
import time
import curses
import random

size = (32,32)
clamp = np.ones(size,dtype="uint8")
world = np.zeros(size,dtype="uint8")

# density sorted
# air
# fire
# water
# sand
# wood
# rock
# ===== Render ======

col_map = [
        (600, 600, 1000),
        (1000, 200, 0),
        (0, 200, 1000),
        (1000, 1000, 100),
        (400,400,200),
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

def colour_init():
    for k,col in enumerate(col_map):
        curses.init_color(k+1,col[0],col[1],col[2])
        curses.init_pair(k+1,k+1,k+1)

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

# hashing is prob slower
mat_list = ["fire","water","sand","wood","rock"]

def get_mat(name):
    return mat_list.index(name)

def tick():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            material = world[x,y]
            if material % 2 == 0:
                continue
            mid = world[x,y]//2
            func_map[mid](x,y,mid*2+1)

def tick_fire(x,y,mid):
    wood = False
    for nx in range(x-1, x+2):
        for ny in range(y-1, y+2):
            if (world[nx,ny] - 1) // 2 == get_mat("wood"):
                wood = True
    if not wood:
        if random.random() < 0.15: # 15% of burning out
            world[x,y] = 0
            return
        swap = world[x,y-1]
        if swap < mid:
            world[x,y-1] = mid + 1
            world[x,y] = swap
            
def tick_water(x,y,mid): 
    # unticked pixel
    if y == 0:
        # bottom of world
        return
    if world[x,y-1] < mid:
        # empty space
        swap = world[x,y-1]
        world[x,y-1] = mid + 1
        world[x,y] = swap
    else:
        # filled space
        direction = random.choice([-1,1])
        nx = x + direction
        if nx < 0 or nx >= size[0]:
            return
        if world[nx,y] < mid:
            # empty space next to
            swap = world[nx,y]
            world[nx,y] = mid + 1
            world[x,y] = swap

def tick_sand(x,y,mid):
    if y == 0:
        # bottom of world
        return
    below = world[x,y-1]
    if below < mid:
        pass
        # empty space
        world[x,y-1] = mid + 1
        world[x,y] = below
    else:
        # filled space
        direction = random.choice([-1,1])
        nx = x + direction
        if nx < 0 or nx >= size[0]:
            return
        below_side = world[nx,y-1]
        if below_side < mid:
            # empty space next to
            world[nx,y] = mid + 1
            world[x,y] = below_side

def tick_wood(x,y,mid):
    pass # wood also is boring

def tick_rock(x,y,mid):
    pass # rocks dont do much

func_map = [tick_fire, tick_water, tick_sand, tick_wood, tick_rock]

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

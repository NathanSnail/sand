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
# spark
# water
# sand
# wood
# rock
# ===== Render ======

col_map = [
        (600, 600, 1000),
        (1000, 200, 0),
        (900, 400, 100),
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

# gas
# liquid
# sand
# solid
# %2 => ticked

# hashing is prob slower
mat_list = [("fire",0),("spark",1),("water",1),("sand",2),("wood",3),("rock",3)]

def get_mat(name):
    if name == "air":
        return 0
    for k,v in enumerate(mat_list):
        if v[0] == name:
            return (k+1)*2+1

def get_type(mid):
    return mat_list[mid-1][1]

def get_name(mid):
    if mid == 0:
        return "air"
    return mat_list[mid-1][0]

def tick():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            material = world[x,y]
            if material % 2 == 1 or material == 0:
                continue
            mid = world[x,y]//2
            if do_reaction(x,y,mid):
                continue
            func_map[get_type(mid)](x,y,mid*2)

def tick_gas(x,y,mid):
    # unticked pixel
    if y == size[1]:
        # top of world
        return
    if y < size[1] - 1 and world[x,y+1] < mid:
        # empty space
        swap = world[x,y+1]
        world[x,y+1] = mid + 1
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
 
def tick_liquid(x,y,mid): 
    # unticked pixel
    if world[x,y-1] < mid and y != 0:
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

def tick_solid(x,y,mid):
    pass # solids don't do anything

def tick_rock(x,y,mid):
    pass # rocks dont do much

func_map = [tick_gas, tick_liquid, tick_sand, tick_solid]

reactions = {
        "fire+air":("air+air",0.15),
        "fire+wood":("spark+fire",0.95),
        "spark+wood":("fire+fire",0.8),
        "spark+air":("air+fire",0.3)
}

def do_reaction(x,y,mid):
    nx = x + random.choice([-1,0,1])
    ny = y + random.choice([-1,0,1])
    if x != nx or y != ny:
        if nx >= 0 and nx < size[0] and ny >= 0 and ny < size[1]:
            new = get_reaction(get_name(world[x,y]//2),get_name(world[nx,ny]//2))
            world[x,y] = get_mat(new[0][0])
            world[nx,ny] = get_mat(new[0][1])
            return new[1]
    return False

def get_reaction(a,b):
    try:
        if random.random() < reactions[a+"+"+b][1]:
            return (reactions[a+"+"+b][0].split("+"),True)
        else:
            return ([a,b],False)
    except:
        return ([a,b],False)

def clean():
    global world
    for y in range(size[1]):
        for x in range(size[0]):
            if world[x,y] == 0:
                continue
            world[x,y] = ((world[x,y]) // 2) * 2

def world_init():
    for y in range(size[1]):
        for x in range(size[0]):
            ty = get_mat("air")
            if random.random() < 0.1:
                ty = get_mat("fire")
            elif random.random() < 0.1:
                ty = get_mat("sand")
            elif y * 0.1 < random.random():
                ty = get_mat("water")
            elif random.random() < 0.1:
                ty = get_mat("wood")
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

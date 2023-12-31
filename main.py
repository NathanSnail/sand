import glfw
import compushady
from compushady import HEAP_UPLOAD, Buffer, Swapchain, Texture2D, HEAP_READBACK
from compushady.formats import R32G32B32A32_FLOAT, R8_UINT, R32_FLOAT, B8G8R8A8_UNORM, R32_UINT, R8G8B8A8_UNORM
from compushady.shaders import hlsl
import platform
import random
import struct
import math
import numpy as np
import time

glfw.init()
# we do not want implicit OpenGL!
glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)

# use 16 to make d3d11 happy...
config = compushady.Buffer(16, compushady.HEAP_UPLOAD)
config_fast = compushady.Buffer(config.size)

# srv is read only, uav is read & write
# 0 is air
# 1 is gas
# 2 is sand
# 3 is liquid
# 4 is solid

mats = [
    (0.0, [200, 200, 255, 255], 0, "air"),
    (1.0, [255, 255, 0, 255], 2, "sand"),
    (0.5, [0, 0, 255, 255], 3, "water"),
    (-0.2, [255, 150, 0, 255], 1, "fire"),
    (2.0, [255, 255, 255, 255], 4, "glass"),
]

density = [mat[0] for mat in mats]
colour = [mat[1] for mat in mats]
types = [mat[2] for mat in mats]
names = [mat[3] for mat in mats]

WIDTH = 1920//40
HEIGHT = 1080//40
SCALE = 10
NUM_MATS = len(mats)


def get_mat(name):
    return names.index(name)


reactions = [("fire+sand", "fire+glass", 1.0)]
reaction_array_reactant = np.array([[0 for y in range(NUM_MATS)]
                                    for x in range(NUM_MATS)], dtype=np.uint32)
reaction_array_catalyst = np.array([[0 for y in range(NUM_MATS)]
                                    for x in range(NUM_MATS)], dtype=np.uint32)

reaction_array_probability = np.array([[0.0 for y in range(NUM_MATS)]
                                       for x in range(NUM_MATS)], dtype=np.float32)

for reaction in reactions:
    reactants = [get_mat(v) for v in reaction[0].split("+")]
    products = [get_mat(v) for v in reaction[1].split("+")]
    probability = reaction[2]
    reaction_array_reactant[reactants[0], reactants[1]] = products[0]
    reaction_array_catalyst[reactants[0], reactants[1]] = products[1]
    reaction_array_probability[reactants[0], reactants[1]] = probability

target = Texture2D(WIDTH*SCALE, HEIGHT*SCALE, B8G8R8A8_UNORM)

# least dry code of all time - like 20 lines of garbage

density_buf = compushady.Texture1D(NUM_MATS, R32_FLOAT)
colour_buf = compushady.Texture1D(NUM_MATS, R8G8B8A8_UNORM)
types_buf = compushady.Texture1D(NUM_MATS, R8_UINT)
# memory go bye bye
react_reactant_buf = compushady.Texture2D(NUM_MATS, NUM_MATS, R32_UINT)
react_catalyst_buf = compushady.Texture2D(NUM_MATS, NUM_MATS, R32_UINT)
react_probability_buf = compushady.Texture2D(NUM_MATS, NUM_MATS, R32_FLOAT)

silly_buf = compushady.Texture2D(2,2,R32_UINT)
print(silly_buf.size) 
silly_buf = compushady.Texture2D(1000,4,R32_UINT)
print(silly_buf.size)
# silly_buf = compushady.Texture2D(1920,1080,R32_UINT)
# print(silly_buf.size)

staging_buffer_density = Buffer(density_buf.size, HEAP_UPLOAD)
staging_buffer_colour = Buffer(colour_buf.size, HEAP_UPLOAD)
staging_buffer_types = Buffer(types_buf.size, HEAP_UPLOAD)
staging_buffer_react_reactant = Buffer(react_reactant_buf.size, HEAP_UPLOAD)
staging_buffer_react_catalyst = Buffer(react_catalyst_buf.size, HEAP_UPLOAD)
staging_buffer_react_probability = Buffer(
    react_probability_buf.size, HEAP_UPLOAD)

world = [[random.choice([0, 1]) for y in range(HEIGHT)]
         for x in range(WIDTH)]
world = np.array(world)
world[:,:] = 0
world[:,1:4] = 1
world[5:20,7:9] = 1
world[1:3,:] = 2
world = world.tolist()
world_buf = compushady.Texture2D(WIDTH, HEIGHT, R32_UINT)

print(world_buf.size)

print(reaction_array_probability)
print(reaction_array_probability.tobytes().hex())
print(reaction_array_probability.dtype)

def copy_bufs():
    staging_buffer_density.upload(np.array(density, dtype=np.float32))
    staging_buffer_density.copy_to(density_buf)
    staging_buffer_colour.upload(np.array(colour, dtype=np.uint8))
    staging_buffer_colour.copy_to(colour_buf)
    print(types)
    staging_buffer_types.upload(np.array(types, dtype=np.uint8))
    staging_buffer_types.copy_to(types_buf)

    staging_buffer_react_reactant.upload(
        np.array(reaction_array_reactant, dtype=np.uint32))
    staging_buffer_react_reactant.copy_to(react_reactant_buf)
    staging_buffer_react_catalyst.upload(
        np.array(reaction_array_catalyst, dtype=np.uint32))
    staging_buffer_react_catalyst.copy_to(react_catalyst_buf)
    staging_buffer_react_probability.upload(reaction_array_probability)
    staging_buffer_react_probability.copy_to(react_probability_buf)

    staging_buffer_world = Buffer(world_buf.size, HEAP_UPLOAD)
    staging_buffer_world.upload(np.array(world, dtype=np.uint32))
    staging_buffer_world.copy_to(world_buf)

    buffer = Buffer(react_catalyst_buf.size, HEAP_READBACK)
    react_catalyst_buf.copy_to(buffer)
    read = buffer.readback()
    stringy = read.hex()
    print(stringy)
    # buffer = Buffer(world_buf.size, HEAP_READBACK)
    # world_buf.copy_to(buffer)
    # read = buffer.readback()
    # stringy = read.hex()
    # print(stringy)


copy_bufs()

with open("compute.hlsl") as f:
    shader_compute = hlsl.compile(
        f
        .read()
        .replace("1/*$WIDTH*/", str(WIDTH))
        .replace("1/*$HEIGHT*/", str(HEIGHT))
        .replace("1/*$NUM_MATS*/", str(NUM_MATS))
    )
compute = compushady.Compute(shader_compute, cbv=[config_fast], srv=[
                             types_buf, density_buf, react_reactant_buf, react_catalyst_buf, react_probability_buf], uav=[world_buf])

with open("render.hlsl") as f:
    shader_render = hlsl.compile(
        f
        .read()
        .replace("1/*$WIDTH*/", str(WIDTH))
        .replace("1/*$HEIGHT*/", str(HEIGHT))
        .replace("1/*$NUM_MATS*/", str(NUM_MATS))
    )
# , srv=[world_buf, colour_buf]
render = compushady.Compute(
    shader_render, srv=[world_buf, colour_buf], uav=[target])

window = glfw.create_window(
    target.width, target.height, "Sand Sim", None, None)

if platform.system() == "Windows":
    swapchain = compushady.Swapchain(glfw.get_win32_window(
        window), compushady.formats.B8G8R8A8_UNORM, 2)
elif platform.system() == "Darwin":
    # macos
    from compushady.backends.metal import create_metal_layer
    ca_metal_layer = create_metal_layer(glfw.get_cocoa_window(
        window), compushady.formats.B8G8R8A8_UNORM)
    swapchain = compushady.Swapchain(
        ca_metal_layer, compushady.formats.B8G8R8A8_UNORM, 2)
else:
    swapchain = compushady.Swapchain((glfw.get_x11_display(), glfw.get_x11_window(
        window)), compushady.formats.B8G8R8A8_UNORM, 2)

count = 0
start = None
multiplier = 0


def do_offset(x, y):
    config.upload(np.array([x, y, random.random()*16], dtype=np.uint32))
    config.copy_to(config_fast)
    # print(compute)
    # print(shader_compute)
    compute.dispatch(target.width // 8, target.height // 8, 1)


while not glfw.window_should_close(window):
    glfw.poll_events()

    # update "push constants*/" or whatever compushady calls them
    # config.upload(struct.pack('f', abs(math.sin(multiplier))))
    # config.copy_to(config_fast)
    render.dispatch(target.width // 8, target.height // 8, 1)
    # prevents races
    for y in range(2, -1, -1):  # makes less holes
        if count % 2:
            for x in range(3):  # favours 1 side
                do_offset(x, y)
        else:
            for x in range(2, -1, -1):  # favours other
                do_offset(x, y)
    swapchain.present(target)
    # time.sleep(0.5)
    if start is None:
        start = time.time()
    # multiplier += 0.02
    count += 1
print(count/(time.time()-start))

swapchain = None  # this ensures the swapchain is destroyed before the window

glfw.terminate()

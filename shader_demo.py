import glfw
import compushady
from compushady import HEAP_UPLOAD, Buffer, Swapchain, Texture2D
from compushady.formats import B8G8R8A8_UNORM
from compushady.shaders import hlsl
import platform
import random
import struct
import math
import time

glfw.init()
# we do not want implicit OpenGL!
glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)

target = Texture2D(1920//5, 1080//5, B8G8R8A8_UNORM)
config = compushady.Buffer(16, compushady.HEAP_UPLOAD) # use 16 to make d3d11 happy...
config_fast = compushady.Buffer(config.size)

with open("compute.hlsl") as f:
    shader = hlsl.compile(f.read())
compute = compushady.Compute(shader, cbv=[config_fast], uav=[target])

window = glfw.create_window(
    target.width, target.height, 'Random', None, None)

if platform.system() == 'Windows':
    swapchain = compushady.Swapchain(glfw.get_win32_window(
        window), compushady.formats.B8G8R8A8_UNORM, 2)
elif platform.system() == 'Darwin':
    # macos
    from compushady.backends.metal import create_metal_layer
    ca_metal_layer = create_metal_layer(glfw.get_cocoa_window(window), compushady.formats.B8G8R8A8_UNORM)
    swapchain = compushady.Swapchain(ca_metal_layer, compushady.formats.B8G8R8A8_UNORM, 2)
else:
    swapchain = compushady.Swapchain((glfw.get_x11_display(), glfw.get_x11_window(
        window)), compushady.formats.B8G8R8A8_UNORM, 2)

count = 0
start = None
multiplier = 0
while not glfw.window_should_close(window):
    glfw.poll_events()

    # update "push constants" or whatever compushady calls them
    config.upload(struct.pack('f', abs(math.sin(multiplier))))
    config.copy_to(config_fast)
    compute.dispatch(target.width // 8, target.height // 8, 1)

    swapchain.present(target)
    if start is None:
        start = time.time()
    multiplier += 0.02
    count += 1
print(count/(time.time()-start))

swapchain = None  # this ensures the swapchain is destroyed before the window

glfw.terminate()
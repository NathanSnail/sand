import glfw
import compushady
from compushady import HEAP_UPLOAD, Buffer, Swapchain, Texture2D
from compushady.formats import B8G8R8A8_UNORM
import platform
import random
import time

print(dir(glfw))
print(glfw.__file__)
glfw.init()
# we do not want implicit OpenGL!
glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)

target = Texture2D(1920//5, 1080//5, B8G8R8A8_UNORM)
random_buffer = Buffer(target.size, HEAP_UPLOAD)

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
start = 2**50
while not glfw.window_should_close(window):
    glfw.poll_events()
    random_buffer.upload(bytes([random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255), 255]) * (target.size // 4))
    random_buffer.copy_to(target)
    swapchain.present(target)
    start = min(time.time(), start)
    count += 1
print(count/(time.time()-start))

swapchain = None  # this ensures the swapchain is destroyed before the window

glfw.terminate()
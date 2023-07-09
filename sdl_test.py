import sys
import sdl2
import sdl2.ext
import sdl2.sdlgfx

def run():
    sdl2.ext.init()

    window = sdl2.ext.Window("Test", size = (320,320))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        for x in range(320):
            for y in range(320):
                sdl2.sdlgfx.pixelRGBA(renderer,x,y,round(x/320*255), round(y/320*255), 255, 255)
        renderer.present()
        #window.refresh()
    sdl2.ext.quit()

if __name__ == "__main__":
    sys.exit(run())

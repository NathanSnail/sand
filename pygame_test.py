import pygame
import random
import time
WIDTH, HEIGHT = (1920,1080)

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))


running = True
frame_count = 1
start = time.time()
running_time = 0.01
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            print("quit")
    screen.fill((0,0,0))
    for i in range(int(WIDTH/5*HEIGHT/5)):
        x = round(random.random() * WIDTH)
        y = round(random.random() * HEIGHT)
        start_2 = time.time()
        #screen.fill((random.random()*255,random.random()*255,random.random()*255),rect=(x,y,1,1))
        screen.set_at((x,y),pygame.Color(200,200,200))
        running_time += time.time() - start_2
    pygame.display.flip()
    frame_count+=1
    print(frame_count)
pygame.quit()
print(frame_count/(time.time()-start))
print(frame_count/running_time)

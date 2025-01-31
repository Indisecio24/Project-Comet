import pygame, time

screen = pygame.display.set_mode((256, 256))
clock = pygame.time.Clock()
test = pygame.Surface((16, 24))
image = pygame.image.load("smw_mario_small - Copy.png")
frame = 0

def set_image(raw_image, index):
    global test
    raw_surface = pygame.surface.Surface((test.get_width(), test.get_height()))
    sheetwidth = raw_image.get_width()
    raw_surface.blit(raw_image, ( 0 - test.get_width() * (index % (sheetwidth / test.get_width())), 0 - test.get_height() * (index // (sheetwidth / test.get_width())) ))
    test = pygame.transform.flip(raw_surface, False, False)

def animate(image, indexmap, seconds_advance = 1):
    global frame
    #print(indexmap[int(frame // 1)])
    set_image(image, indexmap[int(frame // 1)])
    frame += (1 / seconds_advance) * (clock.tick(1) / 1000)
    frame %= len(indexmap)

for i in range(500):
    animate(image, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    screen.blit(test, (16, 16))
    pygame.display.update()
    screen.fill("white")

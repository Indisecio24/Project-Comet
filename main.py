import pygame, pathlib, json
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_p, K_UP, K_DOWN, K_LEFT, K_RIGHT

pygame.init()

# CONSTANTS
SIZE = 1
DISPLAYMULTS = [1, 1]
TILESIZE = [32, 24]
PATH = pathlib.Path()

screen = pygame.display.set_mode((TILESIZE[0] * 16 * SIZE * DISPLAYMULTS[0], TILESIZE[1] * 16 * SIZE * DISPLAYMULTS[1]), pygame.RESIZABLE)
pygame.display.set_caption('Project Comet')
clock = pygame.time.Clock()
deltatime = 0

tile = ""
tiles = pygame.sprite.Group()
tilearray = [[20, 68, 92, 112, 28, 124, 116, 80],
             [21, 84, 87, 221, 127, -1, 241, 17],
             [29, 117, 85, 95, 247, 215, 209, 1],
             [23, 213, 81, 31, 253, 125, 113, 16],
             [5, 69, 93, 119, 223, 255, 245, 65],
             [0, 4, 71, 193, 7, 199, 197, 64]]


# CLASSES
class Sprite(pygame.sprite.Sprite):

    def __init__(self, id, x, y, width, height, up, down, left, right, movemult):
        super().__init__()
        self.id = str(id).lower()
        self.keys, self.movemult = [up, down, left, right], movemult
        self.width, self.height = width, height
        self.vectx, self.vecty, self.dir = 0, 0, "right"
        self.anim, self.old_anim, self.frame, self.anim_speed = "", "", 0, 1
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.image.fill(pygame.Color("blue"))
        self.rect.x, self.rect.y = x, y

    def set_image(self, image):
        raw_image = pygame.image.load(image)
        self.image = pygame.transform.flip(raw_image, self.dir == "left", False)

    def animate(self, folder, seconds_advance=1):
        directory, max = PATH.joinpath(folder, self.id), 0
        while directory.joinpath(f"{self.anim}_{max}.png").exists():
            max += 1
        self.set_image(directory.joinpath(f"{self.anim}_{self.frame}.png"))
        self.frame += seconds_advance * deltatime  # how much it advances every second
        self.frame %= max

    def render(self):
        visual = pygame.transform.scale(self.image, (self.width * SIZE, self.height * SIZE))
        screen.blit(visual, ((self.rect.x - camera.rect.x - 16) * SIZE, (self.rect.y - camera.rect.y - 16) * SIZE))

    def move(self):
        self.rect.x += self.vectx
        self.rect.y += self.vecty

    def control(self, up, down, left, right):
        pressed = pygame.key.get_pressed()
        if pressed[up]:
            self.vecty += -1 * self.movemult
        if pressed[down]:
            self.vecty += 1 * self.movemult
        if pressed[left]:
            self.vectx += -1 * self.movemult
        if pressed[right]:
            self.vectx += 1 * self.movemult
        self.vectx *= 0.7
        self.vecty *= 0.7

    def tick(self):
        self.render()
        self.control(self.keys[0], self.keys[1], self.keys[2], self.keys[3])
        self.move()


class Tile(Sprite):

    def __init__(self, id, index, x, y):
        super().__init__(id, x, y, 16, 16, False, False, False, False, 0)
        self.index = index
        self.directory, self.max, self.frames = PATH.joinpath("assets/tiles"), 0, []
        while self.directory.joinpath(f"{self.id}_{self.max}.png").exists():
            self.frames.append(pygame.image.load(self.directory.joinpath(f"{self.id}_{self.max}.png")))
            self.max += 1

    def set_image(self, raw_image):
        sheetwidth, raw_surface = raw_image.get_width() // 16, pygame.surface.Surface((16, 16))
        raw_surface.blit(raw_image, (0 - 16 * (self.index % sheetwidth), 0 - 16 * (self.index // sheetwidth)))
        self.image = pygame.transform.flip(raw_surface, self.dir == "left", False)

    def animate(self):
        self.set_image(self.frames[self.frame // 1])
        self.frame += self.anim_speed
        self.frame %= self.max

    def tick(self):
        if pygame.sprite.collide_rect(self, camera):
            self.render()
        self.control(self.keys[0], self.keys[1], self.keys[2], self.keys[3])
        self.move()
        
    def update(self):
        self.tick()
        if self.max > 1:
            self.animate()


class Ray(Sprite):

    def __init__(self, id, x, y, width, height, vecx, vecy):
        super().__init__(id, x, y, width, height, False, False, False, False, 1)
        #self.image.fill(pygame.Color("black"))
        self.vectx, self.vecty = 0, 0
        self.initvectx, self.initvecty = vecx, vecy
        self.initx, self.inity = x, y
        grad = (vecy / vecx) if vecx != 0 else 0
        if grad == 0:
            if vecx > 0:
                self.vectx, self.vecty = 1, 0
            elif vecx < 0:
                self.vectx, self.vecty = -1, 0
            elif vecy > 0:
                self.vectx, self.vecty = 0, 1
            elif vecy < 0:
                self.vectx, self.vecty = 0, -1
        else:
            absvec = (vecx**2 + vecy**2)**0.5
            self.vectx, self.vecty = vecx / absvec, vecy / absvec
            if self.vectx < 1 and self.vectx > 0:
                self.vectx = 1
            if self.vectx > -1 and self.vectx < 0:
                self.vectx = -1
            if self.vecty < 1 and self.vecty > 0:
                self.vecty = 1
            if self.vecty > -1 and self.vecty < 0:
                self.vecty = -1

    def cast(self):
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        movedx, movedy = 0 + self.vectx, 0 + self.vecty
        checkx, checky = False, False
        attemptedx, attemptedy = 0 + self.vectx, 0 + self.vecty
        if self.initvectx != 0:
            checkx = attemptedx / self.initvectx < 1
        if self.initvecty != 0:
            checky = attemptedy / self.initvecty < 1
        while checky:
            self.rect.y += self.vecty
            movedy += self.vecty
            attemptedy += self.vecty
            #self.render()
            collisions = pygame.sprite.spritecollide(self, tiles, False)
            if self.initvecty != 0:
                checky = movedy / self.initvecty < 1
        #self.image.fill(pygame.Color("gray"))
        while len(collisions) != 0:
            self.rect.y -= self.vecty
            movedy -= self.vecty
            #self.render()
            collisions = pygame.sprite.spritecollide(self, tiles, False)
            if self.initvecty != 0:
                checky = attemptedy / self.initvecty < 1
        #self.image.fill(pygame.Color("black"))
        while checkx:
            self.rect.x += self.vectx
            movedx += self.vectx
            attemptedx += self.vectx
            #self.render()
            collisions = pygame.sprite.spritecollide(self, tiles, False)
            if self.initvectx != 0:
                checkx = attemptedx / self.initvectx < 1
        #self.image.fill(pygame.Color("gray"))
        while len(collisions) != 0:
            self.rect.x -= self.vectx
            movedx -= self.vectx
            #self.render()
            collisions = pygame.sprite.spritecollide(self, tiles, False)
            if self.initvectx != 0:
                checkx = attemptedx / self.initvectx < 1
        #self.image.fill(pygame.Color("black"))
        movedx -= self.vectx
        movedy -= self.vecty
        return movedx, movedy


class Camera(Sprite):

    def __init__(self, width, height):
        super().__init__("camera", 0, 0, width, height, False, False, False, False, 1)

    def follow(self, sprite):
        dx, dy = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
        if dx != 0 or dy != 0:
            absvec = (dx**2 + dy**2)**0.5
            self.vectx, self.vecty = dx / absvec, dy / absvec
        farx, fary = False, False
        if (sprite.rect.centerx < self.rect.centerx - self.width / 6) or (sprite.rect.centerx > self.rect.centerx + self.width / 6):
            farx = True
        if (sprite.rect.centery < self.rect.centery - self.height / 6) or (sprite.rect.centery > self.rect.centery + self.height / 6):
            fary = True
        self.vectx *= (3 if farx else 0) * sprite.movemult
        self.vecty *= (3 if fary else 0) * sprite.movemult
        if self.vectx < 1 and self.vectx > 0:
            self.vectx = 0
        if self.vecty < 1 and self.vecty > 0:
            self.vecty = 0
        if self.vectx > -1 and self.vectx < 0:
            self.vectx = 0
        if self.vecty > -1 and self.vecty < 0:
            self.vecty = 0
        self.move()
        

class Player(Sprite):

    def __init__(self, x, y, width, height, up, down, left, right):
        super().__init__("player", x, y, width, height, up, down, left, right, 1)

    def move(self, vecx, vecy):
        self.rect.x += vecx
        self.rect.y += vecy

    def tick(self):
        self.render()
        self.control(self.keys[0], self.keys[1], self.keys[2], self.keys[3])
        print(self.vectx, self.vecty)
        if self.vectx != 0 or self.vecty != 0:
            ray = Ray("ray", self.rect.x, self.rect.y, self.width, self.height, 0, self.vecty)
            _, vecy = ray.cast()
            ray = Ray("ray", self.rect.x, self.rect.y + vecy, self.width, self.height, self.vectx, 0)
            vecx, _ = ray.cast()
            del ray
            self.move(vecx, vecy)


# DEFINES
def LoadLevel(name):
    global tiles
    directory = PATH.joinpath("levels", name)
    with open(directory.joinpath("main.json"), "r") as file:
        temp = file.read()
        data = json.loads(temp)
    if data["identifier"] != name:
        raise Exception("Level identifier does not match level name")
    print(data["name"])
    layercount, lvx, lvy, spawnx, spawny = 0, 0, 0, 0, 0
    tilestemp = pygame.sprite.Group()
    for layer in data["layers"]:
        file = open(directory.joinpath(layer["file"]), "r").readlines()
        lvy = 0
        for line in file:
            lvx = 0
            for char in line:
                if char != "\n":
                    tilestruct = data["layers"][layercount]["mapping"][char]
                    tiletype = tilestruct["tile"]
                    if tiletype != "blank" and tiletype != "spawn":
                        tile = Tile(tiletype, 21, (lvx + data["layers"][layercount]["offset"][0]) * 16, (lvy + data["layers"][layercount]["offset"][1]) * 16)
                        tile.anim_speed = tilestruct["frame_seconds"]
                        tile.add(tilestemp)
                    if tiletype == "spawn":
                        spawnx, spawny = (lvx + data["layers"][layercount]["offset"][0]) * 16, (lvy + data["layers"][layercount]["offset"][1]) * 16
                lvx += 1
            lvy += 1
        layercount += 1
        for tile in tilestemp:
            checks = [0, 0, 0, 0, 0, 0, 0, 0]
            # REFER TO BLOB TILESET INFO ONLINE
            for tile2 in tilestemp:
                if tile2.rect.y == tile.rect.y - 16 and tile2.rect.x == tile.rect.x:  # N
                    checks[0] = 1
                if tile2.rect.y == tile.rect.y - 16 and tile2.rect.x == tile.rect.x + 16:  # NE
                    checks[1] = 2
                if tile2.rect.y == tile.rect.y and tile2.rect.x == tile.rect.x + 16:  # E
                    checks[2] = 4
                if tile2.rect.y == tile.rect.y + 16 and tile2.rect.x == tile.rect.x + 16:  # SE
                    checks[3] = 8
                if tile2.rect.y == tile.rect.y + 16 and tile2.rect.x == tile.rect.x:  # S
                    checks[4] = 16
                if tile2.rect.y == tile.rect.y + 16 and tile2.rect.x == tile.rect.x - 16:  # SW
                    checks[5] = 32
                if tile2.rect.y == tile.rect.y and tile2.rect.x == tile.rect.x - 16:  # W
                    checks[6] = 64
                if tile2.rect.y == tile.rect.y - 16 and tile2.rect.x == tile.rect.x - 16:  # NW
                    checks[7] = 128
            if checks[0] == 0:
                checks[7], checks[1] = 0, 0
            if checks[2] == 0:
                checks[1], checks[3] = 0, 0
            if checks[4] == 0:
                checks[3], checks[5] = 0, 0
            if checks[6] == 0:
                checks[5], checks[7] = 0, 0
            total, check = checks[0] + checks[1] + checks[2] + checks[
                3] + checks[4] + checks[5] + checks[6] + checks[7], -2
            chx, chy = -1, 0
            while check != total:
                chx += 1
                if chx >= 8:
                    chx = 0
                    chy += 1
                check = tilearray[chy][chx]
            tile.index = chx + 8 * chy
            tile.animate()
            tile.add(tiles)
        for tile in tilestemp:
            tile.remove(tilestemp)
    return [spawnx, spawny]


camera = Camera((TILESIZE[0] + 2) * 16 * DISPLAYMULTS[0], (TILESIZE[1] + 2) * 16 * DISPLAYMULTS[1]) # one extra tile each side
test = Player(0, 0, 16, 16, K_UP, K_DOWN, K_LEFT, K_RIGHT)

level = "temp"
spawncoord = LoadLevel(level)
test.rect.x, test.rect.y = spawncoord[0], spawncoord[1]
camera.rect.centerx, camera.rect.centery = test.rect.centerx, test.rect.centery

def run_platform():
    global tiles, test, camera
    tiles.update()
    test.tick()
    camera.follow(test)

def pause():
    global tiles, test
    for tile in tiles:
        tile.render()
    test.render()

event = "run_platform"
running = True
while running:
    deltatime = clock.tick() / 1000
    screen.fill(pygame.Color("darkslategrey"))
    for pygame_event in pygame.event.get():
        if pygame_event.type == QUIT:
            running = False
        elif pygame_event.type == KEYDOWN:
            if pygame_event.key == K_ESCAPE:
                running = False
            elif pygame_event.key == K_p:
                if event == "run_platform":
                    event = "pause"
                elif event == "pause":
                    event = "run_platform"
    globals()[event]()
    pygame.display.update()
    #print(deltatime)
pygame.quit()

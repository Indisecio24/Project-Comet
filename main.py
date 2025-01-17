import pygame, pathlib, json
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_z, K_x, K_c, K_s, K_UP, K_DOWN, K_LEFT, K_RIGHT

pygame.init()

# CONSTANTS
SIZE = 2 # DEFAULT 1
DISPLAYMULTS = [1, 1] # DEFAULT 1, 1
TILESIZE = [28, 21] # DEFAULT 32, 24
PATH = pathlib.Path()
JosefinSans = pygame.font.Font(PATH.joinpath("assets", "fonts", "JosefinSans-Regular.ttf"), TILESIZE[0])

screen = pygame.display.set_mode((TILESIZE[0] * 16 * SIZE * DISPLAYMULTS[0], TILESIZE[1] * 16 * SIZE * DISPLAYMULTS[1]), pygame.RESIZABLE)
pygame.display.set_caption('Project Comet')
clock = pygame.time.Clock()
deltatime = 0

tile = ""
tiles = []
tilearray = [[20, 68, 92, 112, 28, 124, 116, 80],
             [21, 84, 87, 221, 127, -1, 241, 17],
             [29, 117, 85, 95, 247, 215, 209, 1],
             [23, 213, 81, 31, 253, 125, 113, 16],
             [5, 69, 93, 119, 223, 255, 245, 65],
             [0, 4, 71, 193, 7, 199, 197, 64]]
bounds = pygame.rect.Rect(0, 0, 1, 1)

# CLASSES
class Sprite(pygame.sprite.Sprite):

    def __init__(self, id, x, y, width, height, up, down, left, right, movemult, run = False):
        super().__init__()
        self.id = str(id).lower()
        self.keys, self.movemult = [up, down, left, right, run], movemult
        self.width, self.height = width, height
        self.vectx, self.vecty, self.dir = 0, 0, "right"
        self.anim, self.old_anim, self.frame, self.anim_speed = "", "", 0, 1
        self.image = pygame.Surface((width, height))
        self.image.set_colorkey((196, 6, 125))
        self.rect = self.image.get_rect()
        #self.image.fill(pygame.Color("blue"))
        self.rect.x, self.rect.y = x, y

    def set_image(self, image):
        raw_image = pygame.image.load(image)
        self.image = pygame.transform.flip(raw_image, self.dir == "left", False)
        self.image.set_colorkey((196, 6, 125))

    def animate(self, folder, seconds_advance=1):
        directory, max = PATH.joinpath(folder, self.id), 0
        while directory.joinpath(f"{self.anim}_{max}.png").exists():
            max += 1
        self.set_image(directory.joinpath(f"{self.anim}_{int(self.frame // 1)}.png"))
        self.frame += (1 / seconds_advance) * (deltatime / 1000)  # how much it advances every second
        self.frame %= max

    def render(self):
        visual = pygame.transform.scale(self.image, (self.width * SIZE, self.height * SIZE))
        screen.blit(visual, (((self.rect.x - camera.rect.x) - 16) * SIZE, ((self.rect.y - camera.rect.y) - 16) * SIZE))

    def move(self):
        self.rect.x += self.vectx
        self.rect.y += self.vecty

    def control(self, up, down, left, right, run = False):
        pressed = pygame.key.get_pressed()
        if pressed[up]:
            self.vecty += -1 * self.movemult * (deltatime / 1000)
        if pressed[down]:
            self.vecty += 1 * self.movemult * (deltatime / 1000)
        if pressed[left]:
            self.vectx += -1 * self.movemult * (deltatime / 1000)
        if pressed[right]:
            self.vectx += 1 * self.movemult * (deltatime / 1000)
        self.vectx *= 0.5
        self.vecty *= 0.5

    def tick(self):
        self.render()
        self.control(self.keys[0], self.keys[1], self.keys[2], self.keys[3])
        self.move()


class Tile(Sprite):

    def __init__(self, id, index, x, y):
        super().__init__(id, x, y, 16, 16, False, False, False, False, 0)
        self.index, self.collision = index, 1
        self.directory, self.max, self.frames = PATH.joinpath("assets/tiles"), 0, []
        while self.directory.joinpath(f"{self.id}_{self.max}.png").exists():
            self.frames.append(pygame.image.load(self.directory.joinpath(f"{self.id}_{self.max}.png")))
            self.max += 1

    def set_image(self, raw_image):
        sheetwidth, raw_surface = raw_image.get_width() // 16, pygame.surface.Surface((16, 16))
        raw_surface.blit(raw_image, (0 - 16 * (self.index % sheetwidth), 0 - 16 * (self.index // sheetwidth)))
        self.image = pygame.transform.flip(raw_surface, self.dir == "left", False)
        self.image.set_colorkey((196, 6, 125))

    def animate(self):
        self.set_image(self.frames[int(self.frame // 1)])
        self.frame += (1 / self.anim_speed) * (deltatime / 1000)
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
        self.initvectx, self.initvecty = vecx, vecy
        self.initx, self.inity = x, y
        vect = pygame.math.Vector2(vecx, vecy)
        try:
            vect.normalize_ip()
            self.vectx, self.vecty = vect.x, vect.y
        except:
            self.vectx, self.vecty = 0, 0
        #grad = (vecy / vecx) if vecx != 0 else 0
        #if grad == 0:
        #    if vecx > 0:
        #        self.vectx, self.vecty = 1, 0
        #    elif vecx < 0:
        #        self.vectx, self.vecty = -1, 0
        #    elif vecy > 0:
        #        self.vectx, self.vecty = 0, 1
        #    elif vecy < 0:
        #        self.vectx, self.vecty = 0, -1
        #else:
        #    absvec = (vecx**2 + vecy**2)**0.5
        #    self.vectx, self.vecty = vecx / absvec, vecy / absvec
        #    if self.vectx < 1 and self.vectx > 0:
        #        self.vectx = 1
        #    if self.vectx > -1 and self.vectx < 0:
        #        self.vectx = -1
        #    if self.vecty < 1 and self.vecty > 0:
        #        self.vecty = 1
        #    if self.vecty > -1 and self.vecty < 0:
        #        self.vecty = -1

    def cast(self):
        collidedirs = []
        collidecheck = False
        #for layer in tiles:
        #    for tile in layer:
        #        collision = pygame.sprite.collide_rect(self, tile)
        #        if collision:
        #            if tile.collision == 1.0: # solid
        #                collidecheck = True
        #                if "vert" not in collidedirs:
        #                    collidedirs.append("vert")
        #            elif tile.collision == 0.5 and (self.vecty > 0 and self.rect.bottom - 4 < tile.rect.top): # down and semisolid and above
        #                collidecheck = True
        #                if "vert" not in collidedirs:
        #                    collidedirs.append("vert")
        movedx, movedy = 0 + self.vectx, 0 + self.vecty
        checkx, checky = False, False
        attemptedx, attemptedy = 0 + self.vectx, 0 + self.vecty
        if self.initvectx != 0:
            checkx = attemptedx / self.initvectx < 1
        if self.initvecty != 0:
            checky = attemptedy / self.initvecty < 1
        while checky and not collidecheck: # move in the y direction
            #self.image.fill(pygame.Color("black"))#
            self.rect.y += self.vecty
            movedy += self.vecty
            attemptedy += self.vecty
            #self.render()#
            collidecheck = False
            for layer in tiles:
                for tile in layer:
                    collision = pygame.sprite.collide_rect(self, tile)
                    if collision:
                        if tile.collision == 1.0:
                            collidecheck = True
                            if "vert" not in collidedirs:
                                collidedirs.append("vert")
                        elif tile.collision == 0.5 and (self.vecty > 0 and self.rect.bottom - 4 < tile.rect.top):
                            collidecheck = True
                            if "vert" not in collidedirs:
                                collidedirs.append("vert")
            if self.initvecty != 0:
                checky = movedy / self.initvecty < 1
        while collidecheck: # undo y movement
            #self.image.fill(pygame.Color("gray"))#
            self.rect.y -= self.vecty
            movedy -= self.vecty
            #self.render()#
            collidecheck = False
            for layer in tiles:
                for tile in layer:
                    collision = pygame.sprite.collide_rect(self, tile)
                    if collision:
                        if tile.collision == 1.0:
                            collidecheck = True
                        elif tile.collision == 0.5 and (self.vecty > 0 and self.rect.bottom - 4 < tile.rect.top):
                            collidecheck = True
            if self.initvecty != 0:
                checky = attemptedy / self.initvecty < 1
        while checkx and not collidecheck:
            #self.image.fill(pygame.Color("black"))#
            self.rect.x += self.vectx
            movedx += self.vectx
            attemptedx += self.vectx
            #self.render()#
            collidecheck = False
            for layer in tiles:
                for tile in layer:
                    collision = pygame.sprite.collide_rect(self, tile)
                    if collision and tile.collision == 1.0:
                        collidecheck = True
                        if "horiz" not in collidedirs:
                            collidedirs.append("horiz")
            if self.initvectx != 0:
                checkx = attemptedx / self.initvectx < 1
        while collidecheck:
            #self.image.fill(pygame.Color("gray"))#
            self.rect.x -= self.vectx
            movedx -= self.vectx
            #self.render()#
            collidecheck = False
            for layer in tiles:
                for tile in layer:
                    collision = pygame.sprite.collide_rect(self, tile)
                    if collision and tile.collision == 1.0:
                        collidecheck = True
            if self.initvectx != 0:
                checkx = attemptedx / self.initvectx < 1
        movedx -= self.vectx
        movedy -= self.vecty
        return movedx, movedy, collidedirs


class Camera(Sprite):

    def __init__(self, width, height, speed = 500):
        super().__init__("camera", 0, 0, width, height, False, False, False, False, speed)

    def follow(self, sprite):
        dx, dy = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
        #if dx != 0 or dy != 0:
        #    absvec = (dx**2 + dy**2)**0.5
        #    self.vectx, self.vecty = dx / absvec, dy / absvec
        farx, fary = False, False
        if (sprite.rect.centerx < self.rect.centerx - self.width / 6) or (sprite.rect.centerx > self.rect.centerx + self.width / 6):
            farx = True
        if (sprite.rect.centery < self.rect.centery - self.height / 6) or (sprite.rect.centery > self.rect.centery + self.height / 6):
            fary = True
        self.vectx = pygame.math.lerp(0, dx / 2.5, farx / 9.5) * 0.5
        self.vecty = pygame.math.lerp(0, dy / 2.5, fary / 9.5) * 0.5
        if self.vectx < 1 * (deltatime / 1000) and self.vectx > 0:
            self.vectx = 0
        if self.vecty < 1 * (deltatime / 1000) and self.vecty > 0:
            self.vecty = 0
        if self.vectx > -1 * (deltatime / 1000) and self.vectx < 0:
            self.vectx = 0
        if self.vecty > -1 * (deltatime / 1000) and self.vecty < 0:
            self.vecty = 0
        self.move()
        self.rect.clamp_ip(bounds)

class Hud(Sprite):
    
    def __init__(self, content, tilex, tiley):
        self.text = JosefinSans.render(content, True, "white")
        super().__init__("hud", tilex * 16 * SIZE, tiley * 16 * SIZE, self.text.get_width(), self.text.get_height(), False, False, False, False, 0)

    def updatetext(self, newtext):
        self.text = JosefinSans.render(newtext, True, "white")

    def render(self):
        screen.blit(self.text, (self.rect.x, self.rect.y))

class Menu(Sprite):

    def __init__(self, title, options, up, down, left, right, select):
        super().__init__("menu", 32 * SIZE, 32 * SIZE, (TILESIZE[0] - 4) * 16 * SIZE * DISPLAYMULTS[0], (TILESIZE[1] - 4) * 16 * SIZE * DISPLAYMULTS[1], up, down, left, right, 0)
        self.title = title
        self.options = options
        self.sel = select
        self.cursorpos, self.cursorlim, self.sellim = 0, 200, True
        self.image = pygame.image.load(PATH.joinpath("assets", "graphics", "menu.png"))
        self.image.set_colorkey((196, 6, 125))
        self.cursor = pygame.Surface((16, 16))
        self.cursor.fill("white")

    def render(self):
        visual = pygame.transform.scale(self.image, (self.width, self.height))
        visual.set_colorkey((196, 6, 125))
        screen.blit(visual, (self.rect.x, self.rect.y))
        titletext = JosefinSans.render(self.title, True, "white")
        screen.blit(titletext, (self.rect.x + (self.rect.width - titletext.get_width()) / 2, self.rect.y + 32))
        base = self.rect.height - 16
        tip = base - (titletext.get_height() * len(self.options) - (len(self.options) - 1) * 16) * 2
        current, ind = tip // 1, 0
        for opt in self.options:
            text = opt[0]
            opttext = JosefinSans.render(text, True, "white")
            screen.blit(opttext, (self.rect.x + (self.rect.width - opttext.get_width()) / 2, current))
            if ind == self.cursorpos:
                screen.blit(self.cursor, (self.rect.x + (self.rect.width - opttext.get_width()) / 2 - 32, current + opttext.get_height() / 2 - self.cursor.get_height() / 2))
            current += opttext.get_height() + 16
            ind += 1

    def cursortick(self):
        global event, test, camera
        pressed = pygame.key.get_pressed()
        if self.sellim == True and not pressed[self.sel]:
            self.sellim = False
        if pressed[self.keys[0]] and self.cursorlim <= 0:
            self.cursorpos -= 1
            self.cursorlim = 200
        if pressed[self.keys[1]] and self.cursorlim <= 0:
            self.cursorpos += 1
            self.cursorlim = 200
        if pressed[self.keys[2]] and self.cursorlim <= 0:
            pass
        if pressed[self.keys[3]] and self.cursorlim <= 0:
            pass
        if pressed[self.sel] and not self.sellim:
            if self.options[self.cursorpos][1] == "":
                pass
            elif self.options[self.cursorpos][1] == "back":
                event.pop()
                self.cursorpos = 0
            elif self.options[self.cursorpos][1] == "quit":
                if event[-1] == "main_menu":
                    event.pop()
                while len(event) > 1:
                    event.pop()
                self.cursorpos = 0
            else:
                event.append(self.options[self.cursorpos][1])
            if self.options[self.cursorpos][1] == "run_platform":
                spawncoord = LoadLevel(level)
                test.rect.x, test.rect.y = spawncoord[0], spawncoord[1]
                camera.rect.centerx, camera.rect.centery = test.rect.centerx, test.rect.centery
                camera.follow(test)
            self.sellim = True
        self.cursorlim -= deltatime
        if self.cursorlim < -1:
            self.cursorlim = -1
        if self.cursorpos < 0:
            self.cursorpos += len(self.options)
        if self.cursorpos >= len(self.options):
            self.cursorpos -= len(self.options)

    def tick(self):
        self.render()
        self.cursortick()


class Player(Sprite):

    def __init__(self, x, y, width, height, up, down, left, right):
        super().__init__("player", x, y, width, height, up, down, left, right, 15, K_x)
        self.image.fill(pygame.Color("blue"))
        self.collisions = set()
        self.buffers = [0, 0, 0] # jump input, prev dir, coyote time

    def move(self, vecx, vecy):
        self.rect.x += vecx
        self.rect.y += vecy

    def control(self, up, down, left, right, run):
        pressed = pygame.key.get_pressed()
        self.buffers[0] -= 1 * (deltatime / 1000)
        self.buffers[2] -= 1 * (deltatime / 1000)
        if "vert" in self.collisions and self.buffers[1] > 0: # collision
            self.buffers[2] = 12/60
        elif self.buffers[2] < -0.1:
            self.buffers[2] = -0.1
        if pressed[up]:
            self.buffers[0] = 4/60
        if (self.vectx > 4 or self.vectx < -4) and self.buffers[2] > 0:
            self.vecty += 1 * (deltatime / 1000)
        else:
            self.vecty += 9.8 * (deltatime / 1000)
        if self.vecty > 9.8:
            self.vecty = 9.8
        if self.buffers[0] > 0 and self.buffers[2] > 0:
            self.vecty = -18 * self.movemult * (deltatime / 1000)
        elif self.buffers[0] < 0:
            self.buffers[0] = 0
        if pressed[left]:
            self.vectx += -1 * self.movemult * (deltatime / 1000)
        if pressed[right]:
            self.vectx += 1 * self.movemult * (deltatime / 1000)
        if pressed[run]:
            self.vectx *= 0.94
        else:
            self.vectx *= 0.9

    def tick(self):
        self.render()
        self.control(self.keys[0], self.keys[1], self.keys[2], self.keys[3], self.keys[4])
        self.collisions = set()
        if self.vectx != 0 or self.vecty != 0:
            ray = Ray("ray", self.rect.x, self.rect.y, self.width, self.height, 0, self.vecty)
            _, vecy, temp = ray.cast()
            for i in temp:
                self.collisions.add(i)
            if self.vecty > 0: self.buffers[1] += 0.5
            elif self.vecty < 0: self.buffers[1] -= 0.1
            else:
                if self.buffers[1] > 1 * (deltatime / 1000):
                    self.buffers[1] -= 1 * (deltatime / 1000)
                    if self.buffers[1] <= 1 * (deltatime * 1000):
                        self.buffers[1] = 0
                elif self.buffers[1] < -1 * (deltatime / 1000):
                    self.buffers[1] += 1 * (deltatime / 1000)
                    if self.buffers[1] >= -1 * (deltatime * 1000):
                        self.buffers[1] = 0
            if self.buffers[1] > 1: self.buffers[1] = 1
            if self.buffers[1] < -1: self.buffers[1] = -1
            if "vert" in self.collisions:
                self.vecty = -0.1
                ray = Ray("ray", self.rect.x, self.rect.y, self.width, self.height - 1, 0, -4)
                _, check, _ = ray.cast()
                if check > -2:
                    self.buffers[1] = 0
                    self.vecty = 0
            ray = Ray("ray", self.rect.x, self.rect.y + vecy, self.width, self.height, self.vectx, 0)
            vecx, _, temp = ray.cast()
            for i in temp:
                self.collisions.add(i)
            self.move(vecx, vecy)
            if "horiz" in self.collisions:
                self.vectx = 0


# DEFINES
def LoadLevel(name):
    global tiles, solidtiles, passtiles, bounds
    directory = PATH.joinpath("levels", name)
    tiles = []
    with open(directory.joinpath("main.json"), "r") as file:
        temp = file.read()
        data = json.loads(temp)
    if data["identifier"] != name:
        raise Exception(f"Level identifier does not match level name; {data['identifier']}, {level}")
    layercount, lvx, lvy, spawnx, spawny, tlrect, brrect = 0, 0, 0, 0, 0, pygame.Rect((0, 0), (16, 16)), pygame.Rect((0, 0), (16, 16))
    for layer in data["layers"]:
        tiles.append(pygame.sprite.Group())
        file = open(directory.joinpath(layer["file"]+".layer"), "r").readlines()
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
                        tile.collision = tilestruct["collision"]
                        tile.add(tiles[-1])
                        if tile.rect.x <= tlrect.x and tile.rect.y <= tlrect.y:
                            tlrect = pygame.Rect((tile.rect.x, tile.rect.y), (16, 16))
                        if tile.rect.x >= brrect.x and tile.rect.y >= brrect.y:
                            brrect = pygame.Rect((tile.rect.x, tile.rect.y), (16, 16))
                    if tiletype == "spawn":
                        spawnx, spawny = (lvx + data["layers"][layercount]["offset"][0]) * 16, (lvy + data["layers"][layercount]["offset"][1]) * 16
                lvx += 1
            lvy += 1
        for tile in tiles[-1]:
            tilestruct = data["layers"][layercount]["mapping"][char]
            checks = [0, 0, 0, 0, 0, 0, 0, 0]
            # REFER TO BLOB TILESET INFO ONLINE
            for tile2 in tiles[-1]:
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
            total, check = checks[0] + checks[1] + checks[2] + checks[3] + checks[4] + checks[5] + checks[6] + checks[7], -2
            chx, chy = -1, 0
            while check != total:
                chx += 1
                if chx >= 8:
                    chx = 0
                    chy += 1
                check = tilearray[chy][chx]
            tile.index = chx + 8 * chy
            tile.animate()
            #if tilestruct["collision"] == 0:
            #    tile.add(passtiles)
            #else:
            #    tile.add(solidtiles)
        layercount += 1
    bounds = pygame.Rect.union(tlrect, brrect)
    return [spawnx, spawny]


# INITIALISE
level = "tutorial"
test = Player(0, 0, 16, 16, K_UP, K_DOWN, K_LEFT, K_RIGHT)
# CAMERA
camera = Camera((TILESIZE[0] + 2) * 16 * DISPLAYMULTS[0], (TILESIZE[1] + 2) * 16 * DISPLAYMULTS[1]) # one extra tile each side
camera.rect.centerx, camera.rect.centery = test.rect.centerx, test.rect.centery
camera.follow(test)
# MENUS
mainmenu = Menu("Project Comet", [["Start", "run_platform"], ["Options", "options"], ["Quit", "quit"]], K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z)
pausemenu = Menu("Pause", [["Resume", "back"], ["Options", "options"], ["Quit", "quit"]], K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z)
optionsmenu = Menu("Options", [["--=<|>=--", ""], ["Back", "back"]], K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z)
# HUDS
fps = Hud("FPS: ", 1, 1)

def main_menu():
    mainmenu.tick()

def run_platform():
    global tiles, test, camera
    for layer in tiles:
        layer.update()
    test.tick()
    camera.follow(test)

def pause():
    global tiles, test
    for layer in tiles:
        for tile in layer:
            tile.render()
    test.render()
    pausemenu.tick()

def options():
    if event[-2] == "pause":
        global tiles, test
        for layer in tiles:
            for tile in layer:
                tile.render()
        test.render()
    optionsmenu.tick()

event = ["main_menu"]
running = True
while running:
    if len(event) == 0:
        running = False
        break
    deltatime = clock.tick()
    fps.updatetext(f"FPS: {int(1000/deltatime//1)}")
    #screen.fill(pygame.Color("darkslategrey"))
    screen.fill(pygame.Color(0, 248, 248))
    for pygame_event in pygame.event.get():
        if pygame_event.type == QUIT:
            running = False
        elif pygame_event.type == KEYDOWN:
            if pygame_event.key == K_ESCAPE:
                running = False
            elif pygame_event.key == K_s:
                if event[-1] == "run_platform":
                    event.append("pause")
                elif event[-1] == "pause":
                    event.pop()
                    pausemenu.cursorpos = 0
    globals()[event[-1]]()
    fps.render()
    pygame.display.update()
pygame.quit()

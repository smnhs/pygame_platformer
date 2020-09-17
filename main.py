import pygame
from PIL import Image
import sys
import pickle

# own files
from SETTINGS import *
from button import *

pygame.init()

win = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Platformer')

# fonts
smallfont = pygame.font.SysFont('comicsans', 140)
font = pygame.font.SysFont('comicsans', 180)
bigfont = pygame.font.SysFont('comicsans', 250)
# background image
png_bg = Image.open('bg.png')
bg = pygame.image.fromstring(png_bg.tobytes(), png_bg.size, png_bg.mode).convert()
bgX = 0
bgX2 = bg.get_width()
# music
play_music = False

filename_maps = 'maps'

clock = pygame.time.Clock()


class Player(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = [self.x, self.y, self.x + self.width, self.y + self.height]
        self.vel = 10
        self.gravity_count = 0
        self.jump_count = 0
        self.left = False
        self.right = False
        self.color = fg_color

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def jump(self):
        if self.jump_count:
            self.y -= self.jump_count ** 2 * 0.4
            self.jump_count -= 1
            while self.collide():
                self.y += 1
                self.jump_count = 0

    def on_ground(self):
        stand = False
        # print(self.hitbox)
        for plat in Platform.plats:
            # print(plat.hitbox)
            if self.hitbox[3] == plat.hitbox[1]:
                if self.hitbox[0] < plat.hitbox[2] and self.hitbox[2] > plat.hitbox[0]:
                    stand = True
                    # print("on ground")
        return stand

    def collide(self):
        self.boxupdate()
        for plat in Platform.plats:
            plat.boxupdate()
            if self.hitbox[1] < plat.hitbox[3] and self.hitbox[3] > plat.hitbox[1]:
                if self.hitbox[0] < plat.hitbox[2] and self.hitbox[2] > plat.hitbox[0]:
                    return True
        return False

    def gravity(self):
        if not self.jump_count and not self.on_ground():
            fall = self.gravity_count ** 2 * grav
            formy = self.durchfall(fall)
            if formy:
                self.y = formy - self.height
                self.gravity_count = 0
            else:
                self.y += fall
                self.gravity_count += 1
            if self.collide():
                while self.collide():
                    self.y -= 1
        else:
            self.gravity_count = 0

    def durchfall(self, fall):
        """To not fall through a platform."""
        self.boxupdate()
        for plat in Platform.plats:
            plat.boxupdate()
            if self.hitbox[2] > plat.hitbox[0] and self.hitbox[0] < plat.hitbox[2]:
                if self.hitbox[3] < plat.hitbox[3] and self.hitbox[3] + fall > plat.hitbox[1]:
                    # print("Platform")
                    return plat.hitbox[1]
        return False

    def boxupdate(self):
        self.hitbox = [self.x, self.y, self.x + self.width, self.y + self.height]


class Platform(object):
    plats = []

    def __init__(self, platformlist):
        self.x = platformlist[0]
        self.y = platformlist[1]
        self.width = platformlist[2]
        self.height = platformlist[3]
        self.hitbox = [self.x, self.y, self.x + self.width, self.y + self.height]
        self.color = fg_color

    def movex(self, left, right, vel, back=0):
        if not back:
            if left:
                self.x += vel
            if right:
                self.x -= vel
        if back:
            if left:
                self.x -= 1
            if right:
                self.x += 1

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def boxupdate(self):
        self.hitbox = [self.x, self.y, self.x + self.width, self.y + self.height]


class MapEditor:
    def __init__(self, color=(0, 255, 255)):
        self.x = 90
        self.y = 30
        self.surfwidth = 750
        self.surfheight = 761 # 800
        self.gridwidth = 700
        self.gridheight = 760
        self.cellwidth = 50
        self.cellheight = 40
        self.scrollval = 0
        self.scrollloop = 5
        self.color = color
        self.filename = filename_maps
        try:
            # load saved maps
            with open(self.filename, 'rb') as fp:
                self.maps = pickle.load(fp)
        except:
            self.maps = []
        self.index = len(self.maps)

    def mapeditor(self):
        editor = True
        # empty fields of the map
        maplist = [[0 for e in range(self.gridwidth//self.cellwidth)] for i in range(self.gridheight//self.cellheight)]
        # menu buttons
        rand = 5
        buttons = [Button(fg_color, rand, 530+rand, 90-rand*2, 50, text='+', textsize=100),
                   Button(fg_color, rand, 580+rand, 90-rand*2, 50, text='SAVE', textsize=35),
                   Button(fg_color, rand, 630+rand, 90-rand*2, 50, text='DELETE', textsize=25),
                   Button(fg_color, rand, 750, 90-rand*2, 40, text='BACK', textsize=35)]
        mapbtns = ScrollList(self.maps, rand, 30, 90-rand*2, 500, nummern=True)
        # editor loop
        while editor:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    editor = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # click in surface area?
                    if self.x < pos[0] < self.x + self.surfwidth:
                        if self.y < pos[1] < self.y + self.surfheight:
                            # which cell?
                            surferpos = (pos[0]-self.x, pos[1]-self.y)
                            cellpos = (surferpos[0] - surferpos[0] % self.cellwidth, surferpos[1] - surferpos[1] % self.cellheight)
                            cellnum = (cellpos[0]//self.cellwidth + self.scrollval, cellpos[1]//self.cellheight)
                            # print(cellnum)
                            if maplist[cellnum[1]][cellnum[0]]:
                                maplist[cellnum[1]][cellnum[0]] = 0
                            else:
                                maplist[cellnum[1]][cellnum[0]] = 1
                            # print(maplist)

                # menu buttons actions
                # new map
                if buttons[0].clicked(event, pos):
                    maplist = self.newmap()
                # save map
                if buttons[1].clicked(event, pos):
                    platlist = self.convert(maplist=maplist)
                    self.savemap(platlist)
                    mapbtns = ScrollList(self.maps, rand, 30, 90-rand*2, 500, nummern=True)
                # delete map
                if buttons[2].clicked(event, pos):
                    self.deletemap(self.index)
                    mapbtns = ScrollList(self.maps, rand, 30, 90 - rand * 2, 500, nummern=True)
                # back
                if buttons[3].clicked(event, pos):
                    editor = False
                # maps auswählen
                mapnum = mapbtns.clicked(event, pos)
                if mapnum is not None:
                    self.scrollval = 0
                    self.index = mapnum
                    maplist = self.convert(platlist=self.maps[mapnum])
            # scroll map
            if self.scrollloop <= 0:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    self.scrollval += 1
                    self.scrollloop = 5
                    # print(self.scrollval)
                    if self.scrollval + 14 > len(maplist[0]):
                        # extend list if scrolling beyond the end
                        for r in range(len(maplist)):
                            maplist[r].append(0)
                    # print(len(maplist[0]))
                    # print('right')
                if keys[pygame.K_LEFT] and self.scrollval > 0:
                    self.scrollval -= 1
                    self.scrollloop = 5
                    # print('left')
            elif self.scrollloop > 0:
                self.scrollloop -= 1

            self.draw(maplist, mapbtns, buttons)
            clock.tick(fps)

    def convert(self, maplist=None, platlist=None):
        """
        Convert a maplist from the editor to a platlist for the game 'interpreter' and back.
        maplist: [[0,0,1,1,0, ... ,1,1,0], ... [0,1,1,0,.... ,0,0]]
            (0 or 1 for each table field of the map)
        platlist: [[900, 160, 100, 40], ... [1500, 200, 50, 40]]
            (a list for each platform: [x, y, width, height])
        """
        if maplist is not None:
            platlist = []
            for rownum in range(len(maplist)):
                maplist[rownum].append(0)       # also recognize platforms at the end of a row
                beforecol = 0
                for colnum in range(len(maplist[rownum])):
                    if maplist[rownum][colnum]:
                        if beforecol == 0:
                            x = (colnum)*self.cellwidth
                            y = (rownum+1)*self.cellheight
                        beforecol += 1
                    elif beforecol > 0:
                        width = beforecol*self.cellwidth
                        platlist.append([x, y, width, self.cellheight])
                        beforecol = 0
            return platlist

        if platlist is not None:
            maxes = []
            for plate in platlist:
                maxes.append(max(plate))
            # create empty maplist
            maplist = [[0 for n in range(max(max(maxes), self.gridwidth//self.cellwidth))] for m in range(self.gridheight//self.cellheight)]
            # divide and register plates in maplist
            for plate in platlist:
                colnum = (plate[0]//self.cellwidth)
                rownum = (plate[1]//self.cellheight) - 1
                length = plate[2]//self.cellwidth
                for l in range(length):
                    maplist[rownum][colnum+l] = 1
            return maplist

    def newmap(self):
        """Returns a new, blank maplist."""
        self.scrollval = 0
        self.index = len(self.maps)
        return [[0 for e in range(self.gridwidth // self.cellwidth)] for i in range(self.gridheight // self.cellheight)]

    def savemap(self, platlist):
        """Save actual map in platlist format."""
        if len(platlist) > 0:
            if self.index < len(self.maps):
                # edited map
                self.maps[self.index] = platlist
            else:
                # add new map
                self.maps.append(platlist)
            # print(self.maps)
            with open(self.filename, 'wb') as fp:
                pickle.dump(self.maps, fp)
                # print('saved')

    def deletemap(self, mapindex):
        """Delete actual map."""
        if mapindex < len(self.maps):
            deletedmap = self.maps.pop(mapindex)
            with open(self.filename, 'wb') as fp:
                pickle.dump(self.maps, fp)
                # print('saved')

    def draw(self, maplist, mapbtns, buttons):
        # surface of the map area
        surfer = pygame.Surface((self.surfwidth, self.surfheight))
        surfer.fill((0, 0, 0))
        # draw finish
        lastplat = 0
        for row in maplist:
            for col_num in range(len(row)):
                if row[col_num] == 1:
                    if lastplat < col_num:
                        lastplat = col_num
        x_ziel = lastplat * self.cellwidth - 50
        for yi in range(0, self.surfheight, int(self.cellheight*3)):
            pygame.draw.rect(surfer, (220, 220, 220), (x_ziel - self.scrollval*self.cellwidth, yi, 30, self.cellheight*1.5))
        # draw player
        pygame.draw.rect(surfer, (0, 100, 100), (400 - player_width//2 - self.scrollval*self.cellwidth, 300 - self.y, player_width, player_height))
        # draw grid
        for li in range(800//self.cellheight):
            liy = self.cellheight*li
            pygame.draw.line(surfer, (200,200,200), (0, liy), (self.gridwidth, liy))
        for li in range(750//self.cellwidth):
            lix = self.cellwidth*li
            pygame.draw.line(surfer, (200,200,200), (lix, 0), (lix, self.gridheight))
        # draw plats
        rownum = 0
        for row in maplist:
            cnum = 0
            for col_num in row[self.scrollval:self.scrollval+14]:     # current visible plates
                if col_num == 1:
                    xpos = cnum * self.cellwidth
                    ypos = rownum * self.cellheight
                    pygame.draw.rect(surfer, self.color, (xpos, ypos, self.cellwidth, self.cellheight))
                cnum += 1
            rownum += 1
        # draw Buttons
        for btn in buttons:
            btn.draw(win, 1)
        mapbtns.draw(win)
        win.blit(surfer, (self.x, self.y))
        pygame.display.update()


def scrollbg(left, right):
    global bgX, bgX2, bgX3
    ST = 4
    if left:
        bgX += ST
        bgX2 += ST
    if right:
        bgX -= ST
        bgX2 -= ST

    # reset after end
    if bgX < bg.get_width() * -1:
        bgX = 0
    elif bgX > 0:
        bgX = bg.get_width() * -1
    if bgX2 < 0:
        bgX2 = bg.get_width()
    elif bgX2 > bg.get_width():
        bgX2 = 0

def start():
    text = smallfont.render("PLATFORMER", 1, (220, 220, 220))
    text2 = smallfont.render("PLATFORMER", 1, (0, 0, 0))
    Map = MapEditor()
    editButton = Button(fg_color, 50, 690, 700, 60, 'NEW/EDIT MAP', textsize=50)
    mapbtns = ScrollList(Map.maps, 50, 500, 700, 170, anzpersite=4, orientation=0, textsize=80, nummern=True)

    while True:
        # draw
        win.fill((0,0,0))
        textwidth = text.get_width()
        pygame.draw.rect(win, fg_color, (400-textwidth/2-10, 200-20, textwidth+20, text.get_height()+40))
        win.blit(text2, (400-textwidth/2+2, 199))
        win.blit(text, (400-textwidth/2, 200))
        editButton.draw(win)
        mapbtns.draw(win)
        pygame.display.update()
        # input events
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if editButton.clicked(event, pos):
                win.fill((0,0,0))
                Map.mapeditor()
                mapbtns = ScrollList(Map.maps, 50, 500, 700, 170, anzpersite=4, orientation=0, textsize=80, nummern=True)
            mapnum = mapbtns.clicked(event, pos)
            if mapnum is not None:
                return mapnum
        clock.tick(fps)

def gameover():
    over = True
    # last gamescreen without pause button
    win.fill((0, 0, 0))
    win.blit(bg, (bgX, 0))
    win.blit(bg, (bgX2, 0))
    for plat in Platform.plats:
        plat.draw(win)
    # save last gamescene
    imgstring = pygame.image.tostring(win, 'RGB')
    win.fill((0,0,0))
    gamebg = pygame.image.frombuffer(imgstring, (800,800), 'RGB')
    gamebg.set_alpha(80)
    win.blit(gamebg, (0,0))
    # text
    text1 = bigfont.render("GAME", 1, (200, 200, 200))
    text2 = bigfont.render("OVER", 1, (200, 200, 200))
    win.blit(text1, (400 - text1.get_width() / 2, 150))
    win.blit(text2, (400 - text2.get_width() / 2, 350))
    pygame.display.update()
    # Buttons
    w = 500
    btns = [Button(fg_color, 400-w/2, 550, w, 60, "NOCHMAL", textsize=60),
            Button(fg_color, 400-w/2, 615, w, 60, "MENÜ", textsize=60)]

    while over:
        pos = pygame.mouse.get_pos()
        # manage input events
        for event in pygame.event.get():
            # quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # again
            if btns[0].clicked(event, pos):
                # print('restart')
                return 0
            # menü
            if btns[1].clicked(event, pos):
                # print('menu')
                return 1
        # draw
        for btn in btns:
            btn.draw(win)
        pygame.display.update()
        clock.tick(fps)

def ziel():
    ziel = True
    endval = 0
    # last gamescreen without pause button
    win.fill((0, 0, 0))
    win.blit(bg, (bgX, 0))
    win.blit(bg, (bgX2, 0))
    for plat in Platform.plats:
        plat.draw(win)
    # save last gamescene
    imgstring = pygame.image.tostring(win, 'RGB')
    win.fill((0,0,0))
    gamebg = pygame.image.frombuffer(imgstring, (800,800), 'RGB')
    gamebg.set_alpha(80)
    win.blit(gamebg, (0,0))
    # text
    text1 = bigfont.render("ZIEL", 1, (0, 0, 0))
    text2 = bigfont.render("ZIEL", 1, (250, 250, 250))
    # Buttons
    w = 500
    btns = [Button((0,0,0), 400-w/2, 550, w, 60, "NÄCHSTES", bg=(0,150,150), textsize=60),
            Button((0,0,0), 400-w/2, 615, w, 60, "NOCHMAL", bg=(0,150,150), textsize=60),
            Button((0,0,0), 400-w/2, 680, w, 60, "MENÜ", bg=(0,150,150), textsize=60)]

    while ziel:
        pos = pygame.mouse.get_pos()
        # manage input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # next
            if btns[0].clicked(event, pos):
                # print('nachstes')
                return 2
            # again
            if btns[1].clicked(event, pos):
                # print('restart')
                return 0
            # menu
            if btns[2].clicked(event, pos):
                # print('menu')
                return 1
        # draw
        if endval <= 900:
            # little animation
            pygame.draw.rect(win, fg_color, (0, 400 - endval/2, 800, endval))
            endval += 50
        else:
            win.blit(text1, (400 - text1.get_width() / 2, 150))
            win.blit(text2, (398 - text2.get_width() / 2, 152))
            for btn in btns:
                btn.draw(win)
        pygame.display.update()
        clock.tick(fps)

def playMusic(file):
    music = pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1)

def loadmap(index):
    """Creates Platform objects from map data."""
    global anz_maps
    with open(filename_maps, 'rb') as fp:
        maps = pickle.load(fp)
    Platform.plats = []
    for plat in maps[index]:
        Platform.plats.append(Platform(plat))
    anz_maps = len(maps)

def redrawWindow():
    # background
    win.blit(bg, (bgX, 0))
    win.blit(bg, (bgX2, 0))
    # ui
    pauseButton.draw(win)
    # foreground
    man.draw(win)
    for plat in Platform.plats:
        plat.draw(win)
    pygame.display.update()

# variables
gamevar = 1         # next game state: 0=previous-level; 1=startpage; 2=next-level
anz_maps = 0        # total number of maps
mapnum = 0          # number of current map

while True:
    if gamevar == 1:
        mapnum = start()
    elif gamevar == 2:
        mapnum += 1
        if mapnum >= anz_maps:
            mapnum = 0
    # print(mapnum)
    if play_music:
        playMusic('music.mp3')

    # pause
    pauseButton = Button(fg_color, 750, 10, 40, 40, 'II', fill=False)

    # main
    man = Player(400 - player_width // 2, 300, player_width, player_height)

    loadmap(mapnum)
    run = True

    # finish
    platxs = []
    for plat in Platform.plats:
        platxs.append(plat.x+plat.width)
    finishplatindex = platxs.index(max(platxs))     # last platform

    # gameloop
    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            pos = pygame.mouse.get_pos()
            # pause
            if pauseButton.clicked(event, pos):
                pause = True
                pygame.mixer.music.pause()
                surf = pygame.Surface((800, 800))
                surf.set_alpha(200)
                surf.fill((0, 20, 20))
                win.blit(surf, (0, 0))
                pausetext = font.render("PAUSE", 1, (200, 200, 200))
                win.blit(pausetext, (400 - pausetext.get_width() / 2, 300))
                pygame.display.update()
                while pause:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pause = False
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        pause = False
                    clock.tick(fps)
                pygame.mixer.music.unpause()

        # right/left input
        keys = pygame.key.get_pressed()
        man.left = False
        man.right = False
        if keys[pygame.K_LEFT]:
            man.left = True
        if keys[pygame.K_RIGHT]:
            man.right = True

        # move right/left
        undo = False
        for plat in Platform.plats:
            plat.movex(man.left, man.right, man.vel)
        if man.collide():
            while man.collide():
                for plat in Platform.plats:
                    plat.movex(man.left, man.right, man.vel, 1)
            man.left = False
            man.right = False

        scrollbg(man.left, man.right)

        # jump + gravity
        if keys[pygame.K_SPACE]:
            if man.on_ground():
                man.jump_count = 12
        man.jump()
        man.gravity()

        # draw
        redrawWindow()

        # finish
        finishplat = Platform.plats[finishplatindex]
        finishx = finishplat.x+finishplat.width - 100
        if man.x+man.width/2 > finishx:
            run = False
            gamevar = ziel()

        # gameover
        if man.y > 800:
            pygame.mixer.music.fadeout(800)
            run = False
            gamevar = gameover()
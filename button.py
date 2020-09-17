import pygame


class Button:
    buttons = []

    def __init__(self, color, x, y, width, height, text='', bg=(0, 0, 0), fill=False, textsize=60):
        """
        Creates a Button.
        color,x,y,width,height, (text='',bg=(0,0,0),fill=False,textsize=60)
        """
        self.color = color
        self.fg_color = color  # initial color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.bg_color = bg
        self.fill = fill
        self.textsize = textsize

    def draw(self, win, outline=None):
        if self.fill:
            win.fill(self.bg_color)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        if outline:
            pygame.draw.rect(win, outline, (self.x, self.y, self.width, self.height), 2)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', self.textsize)
            text = font.render(self.text, 1, self.bg_color)
            win.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # pos = (x,y)
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False

    def clicked(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.isOver(pos):
                return True

        if event.type == pygame.MOUSEMOTION:
            if self.isOver(pos):
                self.color = (220, 220, 220)
            else:
                self.color = self.fg_color
        return False


class ScrollList:
    def __init__(self, elementlist, x, y, width, height, anzpersite=7, color=(0,255,255), bg_color=(0,0,0), orientation=1, textsize=60, nummern=False):
        """
        Creates a list which contains Buttons.
        elementlist,x,y,width,height, (anzpersite=7,color=(0,255,255),bg_color=(0,0,0),orientation=1,textsize=60,nummern=False)
        """
        self.elements = elementlist         # elements which are represented as buttons
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anzpersite = anzpersite        # number of visible buttons at once
        self.color = color
        self.color2 = (180,230,230)
        self.bg_color = bg_color
        self.orientation = orientation
        self.textsize = textsize
        self.sidebtnsize = max(self.height // 18, self.width // 18)
        self.btntext = elementlist
        self.elementslen = len(elementlist)
        self.scrollval = 0
        if nummern:
            self.btntext = [i for i in range(1, self.elementslen + 1)]
        # Buttons
        if self.orientation:
            self.scrollbtns = (Button(self.color2, 0, 0, self.width, self.sidebtnsize, 'A', textsize=self.textsize - 10, bg=bg_color),
                               Button(self.color2, 0, self.height - self.sidebtnsize, self.width, self.sidebtnsize, 'V', textsize=self.textsize - 10, bg=bg_color))
            self.elementsize = (self.height - 2 * self.sidebtnsize) // self.anzpersite
            self.elementbtns = [Button(self.color, 0, self.sidebtnsize + self.elementsize * i, self.width, self.elementsize,
                                       str(self.btntext[i]), textsize=self.textsize, bg=bg_color)
                                for i in range(self.elementslen)]

        else:
            self.scrollbtns = (Button(self.color2, 0, 0, self.sidebtnsize, self.height, '<', textsize=self.textsize, bg=bg_color),
                               Button(self.color2, self.width - self.sidebtnsize, 0, self.sidebtnsize, self.height, '>', textsize=textsize, bg=bg_color))
            self.elementsize = (self.width - 2 * self.sidebtnsize) // self.anzpersite
            self.elementbtns = [Button(self.color, self.sidebtnsize + self.elementsize * i, 0, self.elementsize, self.height,
                                       str(self.btntext[i]), textsize=self.textsize, bg=bg_color)
                                for i in range(self.elementslen)]
        # print(self.scrollbtns)

    def clicked(self, event, pos):
        pos = (pos[0]-self.x, pos[1]-self.y)
        if 0 < pos[0] < self.width and 0 < pos[1] < self.height:
            # up/down Buttons
            if self.scrollbtns[0].clicked(event, pos):
                self.scroll(1)
            elif self.scrollbtns[1].clicked(event, pos):
                self.scroll(-1)
            # elements
            else:
                for btn in self.elementbtns:
                    if btn.clicked(event, pos):
                        return self.elementbtns.index(btn)

    def scroll(self, factor):
        if self.scrollval-factor >= 0 and self.scrollval+self.anzpersite-factor-1 <= self.elementslen:
            if self.orientation:
                for btn in self.elementbtns:
                    btn.y += self.elementsize * factor
            else:
                for btn in self.elementbtns:
                    btn.x += self.elementsize * factor
            self.scrollval -= factor

    def draw(self, win):
        surfer = pygame.Surface((self.width,self.height))

        for e in range(self.scrollval, self.scrollval+self.anzpersite):
            try:
                self.elementbtns[e].draw(surfer, 1)
            except IndexError:
                break

        self.scrollbtns[0].draw(surfer)
        self.scrollbtns[1].draw(surfer)

        win.blit(surfer, (self.x, self.y))

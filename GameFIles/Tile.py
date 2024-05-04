import pygame
import sys

Resolution = 20
Dimensions = (28,28)
Screen = (Resolution*Dimensions[0], Resolution*Dimensions[1])
display = pygame.display.set_mode(Screen)

class Tile:
    def __init__(self, c, r, state):
        self.c = c
        self.r = r
        self.x = self.c * Resolution
        self.y = self.r * Resolution
        self.state = 0
        self.rect = pygame.Rect(self.x, self.y, Resolution, Resolution)

    def draw(self):
        pygame.draw.rect(display, self.getColor(), self.rect)
    
    def getColor(self):
        if self.state == 0:
            return "black"
        return "white"

grid = []
for r in range(Dimensions[1]):
    row = []
    for c in range(Dimensions[0]):
        tile = Tile(c,r,0)
        row.append(tile)
    grid.append(row)


def draw():
    display.fill('white')
    pygame.display.flip()


def update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



while True:
    draw()
    update()
